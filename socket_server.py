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
            self.targets = []
            self.soldier = Target()
            self.address = None #('192.168.1.19',8888)
            self.run()
        except socket.error, msg:
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

    def run(self):
        print 'Running...'
        try:
            while self.should_run:
                sleep(5)
                self.soldier.get_data()
                self.sync_targets()
                buf = ''
                try:
                    buf, self.address = self.serversocket.recvfrom(1024)
                except:
                    pass
                if len(buf) > 0:
                    print 'found client {} on port'.format(self.address[0],self.address[1])
                    try:
                        print 'innet loop'
                        if buf == 'stop'.lower():
                            print 'killing connection'
                            self.should_run = False
                        if buf.startswith('mark'):
                            new_target = self.soldier.mark_target()
                            new_target['reconunitid'] = conf.RECONUNITID
                            self.update_db(new_target)
                            print 'new target marked! ' + json.dumps(new_target)
                        print buf + '#####################################'

                    except Exception:
                        print traceback.format_exc()
                        print "keep reading"
                        break
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
        targets_to_remove, targets_to_add = self.sync_with_db()
        for target in targets_to_add:
            relative_target = self.soldier.get_relative_target(target)
            self.send(json.dumps(relative_target))
        for target in targets_to_remove:
            target_id = json.dumps(target)['id']
            self.send(target_id)

    def update_db(self, target):
        print 'update db... '
        print target
        return
        post(url="{}:{}/{}".format(conf.DB_HOST, conf.DB_PORT, conf.DB_LANE), data=json.dumps(target),
             headers=conf.HEADER)

    def get_targets(self):
        return conf.data
        res = get(url="{}:{}/{}".format(conf.DB_HOST, conf.DB_PORT, conf.DB_LANE))
        return json.loads(res.content)

    def sync_with_db(self):
        tagets_to_remove = []
        targets_to_add = []
        for target in self.get_targets():
            targets_to_add.append(target)
        return tagets_to_remove, targets_to_add

    def send(self,msg):
        if self.address:
            self.serversocket.sendto('add {}\n'.format(msg), self.address)


if __name__ == '__main__':
    s = SoldierApi()
