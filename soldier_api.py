import errno
import itertools
import json
import socket
import subprocess
import sys
import traceback
from time import sleep
from ipgetter import myip
from Target import Target
from db_utils import db
from settings import conf

spinner = itertools.cycle(['-', '/', '|', '\\'])


class SoldierApi():
    def __init__(self):
        try:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.soldier = Target()
            self.serversocket.bind(('0.0.0.0', 8081))
            self.serversocket.setblocking(False)
            self.should_run = True
            self.command = ''
            self.targets = {}
            self.address = conf.HOLOLENC_ADDR
            self.db = db()
            self.run()
        except socket.error, msg:
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def run(self):
        self._wait_for_hololence()

        print 'Running...'
        try:
            while self.should_run:
                self.update_recon()
                self.sync_msg()
                self.sync_targets()
                try:
                    buf, self.address = self.serversocket.recvfrom(1024)
                    if len(buf) > 0:
                        try:
                            print '#### recived message: {} ####'.format(buf)
                            if buf == 'stop'.lower():
                                print 'killing connection'
                                self.should_run = False
                                sys.exit(0)
                            hololence_values = buf.split()
                            if hololence_values[0] == conf.MARK and len(hololence_values) == 5:
                                # mark new target
                                alpha = hololence_values[2]
                                azimut = hololence_values[4]
                                new_target = self.soldier.mark_target(alpha, azimut)
                                self.update_db(new_target)
                                print 'new target marked! ' + json.dumps(new_target)
                            elif len(hololence_values) == 3:
                                # delete target from hololence
                                target_id = hololence_values[2]
                                self.delete_db_target(target_id)
                        except Exception:
                            print traceback.format_exc()
                            print "keep reading"
                            continue
                except IOError as e:  # and here it is handeled
                    if e.errno == errno.EWOULDBLOCK:
                        sleep(0.1)
                        sys.stdout.write(spinner.next())  # write the next character
                        sys.stdout.flush()  # flush stdout buffer (actual character display)
                        sys.stdout.write('\b')  # erase the last written char
                        continue
                except:
                    print traceback.format_exc()
                    print "keep reading"
                    sleep(5)
                    continue
                sys.stdout.write(spinner.next())  # write the next character
                sys.stdout.flush()  # flush stdout buffer (actual character display)
                sys.stdout.write('\b')  # erase the last written char
                sleep(1)

        except KeyboardInterrupt:
            self.serversocket.close()
            print "closed"
            print traceback.format_exc()

        except Exception:
            self.serversocket.close()
            print "closed"
            print traceback.format_exc()

        finally:
            self.serversocket.close()
            print "closed"
            print traceback.format_exc()

    def _wait_for_hololence(self):
        print 'looking for hololence on ip {} in port {}...'.format(self.address[0], self.address[1])
        print 'waiting for hololence to send start msg...'
        while True:
            try:
                self.serversocket.sendto('ip: {}'.format(myip()), self.address)
                sleep(1)
                buf, address = self.serversocket.recvfrom(1024)
                if len(buf) > 0:
                    print buf
                    try:
                        if buf.lower() == conf.START:
                            break
                    except Exception:
                        print traceback.format_exc()
                        continue
                self._spinner()
                sleep(0.5)
            except IOError as e:  # and here it is handeled
                if e.errno == errno.EWOULDBLOCK:
                    sleep(0.5)
                    continue
            except:
                print traceback.format_exc()
                sleep(2)
                continue
        print 'Ready to go!'

    def _ping(self):
        try:
            response = subprocess.check_output(
                ['ping', '-c', '3', self.address[0]],
                stderr=subprocess.STDOUT,  # get all output
                universal_newlines=True  # return string not bytes
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _spinner(self):
        sys.stdout.write(spinner.next())  # write the next character
        sys.stdout.flush()  # flush stdout buffer (actual character display)
        sys.stdout.write('\b')  # erase the last written char

    def update_recon(self):
        self.soldier.sync_gps()
        self.db.update_location(self.soldier.latitude, self.soldier.longitude)

    def sync_targets(self):
        targets_to_add, targets_ids_to_remove = self.get_target_diff()
        for target in targets_to_add:
            print 'adding new target {}'.format(json.dumps(target))
            self.targets[target['id']] = target
            relative_target = self.soldier.get_relative_target(target)
            self.add_target(relative_target)
            sleep(2)
        for target_id in targets_ids_to_remove:
            self.remove_target_id(target_id)
            sleep(2)

    def sync_msg(self):
        try:
            data = self.db.gets_msg()
            if data:
                for msg in data:
                    if self.address:
                        warning_msg = msg['message']
                        msg_id = msg['id']
                        self.serversocket.sendto('warning: {}'.format(warning_msg), self.address)
                        sleep(1)
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
        msg = 'add: id {} azimuth {} distance {} elv {}'.format(msg['id'], msg['azimut'], msg['distance'],
                                                                msg['altitude'])
        if self.address:
            self.serversocket.sendto(msg, self.address)

    def remove_target_id(self, msg):
        self.targets.pop(msg)
        if self.address:
            self.serversocket.sendto('remove: id {}'.format(msg), self.address)

    def delete_db_target(self, t_id):
        try:
            payload = {'id': t_id}
            res = self.db.delete_target(t_id)
            if res.status_code != 200:
                print 'error update db'
        except:
            print 'error in update db {}'.format(traceback.format_exc())
