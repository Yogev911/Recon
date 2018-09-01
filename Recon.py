import errno
import json
import socket
import subprocess
import sys
import traceback
from time import sleep
from ipgetter import myip

import utils
from ElectronicUnit import ElectronicUnit
from db_utils import db
from settings import conf


class Recon:
    def __init__(self):
        try:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.elect_unit = ElectronicUnit()
            self.serversocket.bind(('0.0.0.0', 8081))
            self.serversocket.setblocking(False)
            self.command = ''
            self.targets = {}
            self.address = conf.HOLOLENC_ADDR
            self.db = db()
            self.run()
        except socket.error, msg:
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def run(self):
        self._wait_for_client_connection()
        print 'Running...'
        try:
            while True:
                utils.spinner()
                self._update_recon_location()
                self.sync_msg()
                self.sync_targets()
                try:
                    buf, address = self.serversocket.recvfrom(1024)
                    if len(buf) > 0:
                        try:
                            self._parse_client_data(buf)
                        except:
                            print traceback.format_exc()
                            continue
                except IOError as e:
                    if e.errno == errno.EWOULDBLOCK:
                        continue
                except:
                    print traceback.format_exc()
                    continue
        except:
            self._exit_gracefully()

    def _parse_client_data(self, buf):
        print '#### recived message: {} ####'.format(buf)
        if buf.lower() == conf.STOP_MESSAGE:
            self._exit_gracefully()
        hololence_values = buf.split()
        if hololence_values[0] == conf.MARK and len(hololence_values) == 5:
            # mark new target
            self._set_new_target(hololence_values)
        elif len(hololence_values) == 3:
            # delete target from hololence
            self._delete_target(hololence_values)

    def _exit_gracefully(self):
        print 'Killing connection'
        self.serversocket.sendto('disconnect', self.address)
        self.serversocket.close()
        sys.exit(0)

    def _delete_target(self, hololence_values):
        target_id = hololence_values[2]
        self.delete_db_target(target_id)
        self.sync_targets()

    def _set_new_target(self, hololence_values):
        bearing = hololence_values[2]
        azimuth = hololence_values[4]
        new_target = self.elect_unit.mark_target(bearing, azimuth)
        print 'Adding marked target to DB ' + json.dumps(new_target)
        self.update_db(new_target)
        self.sync_targets()

    def _wait_for_client_connection(self):
        print 'looking for hololence on ip {} in port {}...'.format(self.address[0], self.address[1])
        while True:
            try:
                utils.spinner()
                self.serversocket.sendto('ip: {}'.format(myip()), self.address)
                sleep(conf.SLEEP_TIME)
                buf, address = self.serversocket.recvfrom(1024)
                if len(buf) > 0:
                    print buf
                    if buf.lower() == conf.START:
                        break
            except IOError as e:
                if e.errno == errno.EWOULDBLOCK:
                    continue
            except:
                print traceback.format_exc()
                continue

    def _ping(self):
        try:
            subprocess.check_output(
                ['ping', '-c', '3', self.address[0]],
                stderr=subprocess.STDOUT,  # get all output
                universal_newlines=True  # return string not bytes
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _update_recon_location(self):
        self.elect_unit.sync_gps()
        self.db.update_location(self.elect_unit.latitude, self.elect_unit.longitude)

    def sync_targets(self):
        targets_to_add, targets_ids_to_remove = self.get_target_diff()
        for target in targets_to_add:
            print 'adding new target {}'.format(target['id'])
            self.targets[target['id']] = target
            relative_target = self.elect_unit.get_relative_target(target)
            self.add_target(relative_target)
            sleep(conf.SLEEP_TIME)
        for target_id in targets_ids_to_remove:
            self.remove_target_id(target_id)
            sleep(conf.SLEEP_TIME)

    def sync_msg(self):
        try:
            data = self.db.gets_msg()
            if data:
                for msg in data:
                    if self.address:
                        self.serversocket.sendto('warning: {}'.format(msg['message']), self.address)
                        sleep(conf.SLEEP_TIME)
        except:
            print traceback.format_exc()

    def update_db(self, target):
        try:
            self.db.send_target(target)
        except:
            print 'error in update db {}'.format(traceback.format_exc())

    def get_targets(self):
        return self.db.get_targets()

    def get_target_diff(self):
        targets = self.get_targets()
        if not targets:
            return [], []
        targets_ids = map(lambda l: l['id'], targets)
        targets_ids_to_remove = set(self.targets.keys()) - set(targets_ids)
        targets_to_add = filter(lambda l: l['id'] not in self.targets.keys(), targets)
        return targets_to_add, targets_ids_to_remove

    def add_target(self, msg):
        msg = 'add: id {} azimuth {} distance {} elv {}'.format(msg['id'],
                                                                msg['azimuth'],
                                                                msg['distance'],
                                                                msg['bearing'])
        print msg
        self.serversocket.sendto(msg, self.address)

    def remove_target_id(self, target_id):
        self.targets.pop(target_id)
        msg = 'remove: id {}'.format(target_id)
        print msg
        if self.address:
            self.serversocket.sendto('remove: id {}'.format(target_id), self.address)

    def delete_db_target(self, t_id):
        try:
            res = self.db.delete_target(t_id)
            if res.status_code != 200:
                print 'error update db'
        except:
            print 'error in update db {}'.format(traceback.format_exc())
