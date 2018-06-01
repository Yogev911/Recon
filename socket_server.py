import socket
import traceback
from multiprocessing import Process, Queue
from Target import Target
from requests import get, post
import json
from utils import conf
import sys
from time import sleep


class SoldierApi():
    def __init__(self):
        try:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.serversocket.bind(('0.0.0.0', 8081))
            self.serversocket.setblocking(False)
            self.should_run = True
            self.command = ''
            self.targets = {}
            self.soldier = Target()
            self.address = ('213.57.75.18', 12346)
            self.run()
        except socket.error, msg:
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def run(self):
        print 'Running...'
        try:
            while self.should_run:
                sleep(1)
                self.soldier.update_gps()
                self.sync_targets()
                try:
                    buf, self.address = self.serversocket.recvfrom(1024)
                    print 'self address : '
                    print self.address
                    if len(buf) > 0:
                        print 'found client {} on port'.format(self.address[0], self.address[1])
                        try:
                            print 'innet loop'
                            if buf == 'stop'.lower():
                                print 'killing connection'
                                self.should_run = False
                            if buf.startswith(conf.MARK):
                                hololence_values = buf.split()
                                if len(hololence_values) == 5:
                                    alpha = hololence_values[2]
                                    azimut = hololence_values[4]
                                    new_target = self.soldier.mark_target(alpha, azimut)
                                    new_target['reconunitid'] = conf.RECONUNITID
                                    self.update_db(new_target)
                                    print 'new target marked! ' + json.dumps(new_target)
                            print buf + '#####################################'

                        except Exception:
                            print traceback.format_exc()
                            print "keep reading"
                            continue
                except:
                    pass
                sleep(5)

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

    def sync_targets(self):
        targets_to_add, targets_ids_to_remove = self.get_target_diff()
        for target in targets_to_add:
            print 'adding new target'
            print target
            self.targets[target['id']] = target
            relative_target = self.soldier.get_relative_target(target)
            self.add_target(json.dumps(relative_target))
        for target_id in targets_ids_to_remove:
            self.remove_target_id(target_id)

    def update_db(self, target):
        print 'update db... '
        print target
        # return
        # post(url="{}:{}/{}".format(conf.DB_HOST, conf.DB_PORT, conf.DB_LANE), data=json.dumps(target),
        #      headers=conf.HEADER)

    def get_targets(self):
        res = get(url="https://reconsevice.herokuapp.com/target")
        if res.status_code == 200:
            data = json.loads(res.content)
            return data['data']
        return None
        # res = get(url="{}:{}/{}".format(conf.DB_HOST, conf.DB_PORT, conf.DB_LANE))
        # return json.loads(res.content)

    def get_target_diff(self):
        targets = self.get_targets()
        if not targets:
            return [], []
        targets_ids = map(lambda l: l['id'], targets)
        targets_ids_to_remove = set(self.targets.keys()) - set(targets_ids)
        targets_to_add = filter(lambda l: l['id'] not in self.targets.keys(), targets)
        return targets_to_add, targets_ids_to_remove

    def add_target(self, msg):
        print 'adding '
        print msg
        if self.address:
            self.serversocket.sendto(
                'add: id {} azimuth {} distance {} elv {} \n'.format(msg['id'], msg['azimut'], msg['distance'],
                                                                     msg['altitude']), self.address)

    def remove_target_id(self, msg):
        print 'remove target id {}'.format(msg)
        self.targets.pop(msg)
        if self.address:
            self.serversocket.sendto('remove: {}\n'.format(msg), self.address)


if __name__ == '__main__':
    s = SoldierApi()
