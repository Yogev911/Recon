import socket
import traceback
import itertools

from Target import Target
from requests import get, post, delete
import json
from utils import conf
import sys
from time import sleep

spinner = itertools.cycle(['-', '/', '|', '\\'])

class db():
    def __init__(self):
        self.root = "https://reconsevice.herokuapp.com/"
        self.target = "target/"
        self.reconunit = 'reconunit/'
        self.msg = 'message/'

    def send_target(self,target):
        return post(self.root+self.target, json=target)

    def get_target(self,target_id):
        return get(self.root+self.target+target_id)

    def get_targets(self):
        return get(self.root+self.target)

    def delete_target(self,target_id):
        return delete(self.root+self.target+target_id)

    def gets_msg(self):
        return get(self.root+self.msg+conf.RECONUNITID)


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
                sleep(0.5)
                self.sync_targets()
                try:
                    buf, self.address = self.serversocket.recvfrom(1024)
                    if len(buf) > 0:
                        try:
                            print buf + '#####################################'
                            if buf == 'stop'.lower():
                                print 'killing connection'
                                self.should_run = False
                                break
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
                except:
                    print "keep reading"
                    sleep(5)
                    continue

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
        print 'looking for hololence on ip {} in port {}...'.format(self.address[0],self.address[1])
        while True:
            # HOST_UP = True if os.system("ping -c 1 " + self.address[0]) is 0 else False
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            HOST_UP = True if sock.connect_ex(self.address) is 0 else False
            if HOST_UP:
                break
            self._spinner()
            sleep(1)

    def _spinner(self):
        sys.stdout.write(spinner.next())  # write the next character
        sys.stdout.flush()  # flush stdout buffer (actual character display)
        sys.stdout.write('\b')  # erase the last written char

    def sync_targets(self):
        targets_to_add, targets_ids_to_remove = self.get_target_diff()
        for target in targets_to_add:
            print 'adding new target'
            print target
            self.targets[target['id']] = target
            relative_target = self.soldier.get_relative_target(target)
            self.add_target(relative_target)
            sleep(3)
        for target_id in targets_ids_to_remove:
            self.remove_target_id(target_id)
            sleep(3)

    def sync_msg(self):
        res = self.db.gets_msg()
        if res.status_code == 200:
            data = json.loads(res.content)
            for msg in data['data']:
                if self.address:
                    warning_msg = msg['msg']
                    msg_id = msg['id']
                    self.serversocket.sendto('warrning: {}\n'.format(warning_msg), self.address)
                    sleep(1)
                    # r = delete("https://reconsevice.herokuapp.com/target")

    def update_db(self, target):
        try:
            print 'update db... '
            # print target
            res = self.db.send_target(target)
            if res.status_code != 200:
                print 'error update db'
                print res.json()
        except:
            print 'error in update db {}'.format(traceback.format_exc())

    def get_targets(self):
        res = self.db.get_targets()
        if res.status_code == 200:
            data = json.loads(res.content)
            return data['data']
        return None

    def get_target_diff(self):
        targets = self.get_targets()
        if not targets:
            return [], []
        targets_ids = map(lambda l: l['id'], targets)
        targets_ids_to_remove = set(self.targets.keys()) - set(targets_ids)
        targets_to_add = filter(lambda l: l['id'] not in self.targets.keys(), targets)
        return targets_to_add, targets_ids_to_remove

    def add_target(self, msg):
        data = 'add: id {} azimuth {} distance {} elv {} \n'.format(msg['id'], msg['azimut'], msg['distance'],
                                                                    msg['altitude'])
        print 'sending target to hololence: '
        print msg
        if self.address:
            self.serversocket.sendto(msg, self.address)

    def remove_target_id(self, msg):
        print 'remove target id {}'.format(msg)
        self.targets.pop(msg)
        if self.address:
            self.serversocket.sendto('remove: id {}\n'.format(msg), self.address)

    def delete_db_target(self, t_id):
        try:
            payload = {'id': t_id}
            res = self.db.delete_target(t_id)
            print 'remove target {} '.format(t_id)
            if res.status_code != 200:
                print 'error update db'
        except:
            print 'error in update db {}'.format(traceback.format_exc())
