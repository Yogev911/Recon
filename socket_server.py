import socket
import traceback
from multiprocessing import Process, Queue
from Target import Target
from requests import get, post
import json
from utils import conf


class SoldierApi():
    def __init__(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind(('0.0.0.0', 8081))
        self.serversocket.listen(5)  # become a server socket, maximum 5 connections
        self.should_run = True
        self.command = ''
        self.targets = []
        self.soldier = Target()
        self.run()

    def __del__(self):
        self.connection.close()

    def run(self):
        print 'Running...'
        try:
            while self.should_run:
                print 'wating for new connection'
                self.connection, self.address = self.serversocket.accept()
                print 'found client {}'.format(self.address[0])
                while True:
                    try:
                        print 'innet loop'
                        self.soldier.get_data()
                        self.sync_targets()
                        buf = self.connection.recv(64)
                        if len(buf) > 0:
                            if buf == 'stop'.lower():
                                print 'killing connection'
                                self.connection.close()
                                break
                            if buf.startswith('mark'):
                                new_target = self.soldier.mark_target()
                                target_type = buf.startswith(conf.MARK).split(' ')[1]
                                if target_type in conf.TARGET_TYPES:
                                    new_target['type'] = target_type
                                else:
                                    continue
                                new_target['reconunitid'] = conf.RECONUNITID
                                self.update_db(new_target)
                                print new_target
                            print 'reading from {}'.format(self.address[0])
                            print buf

                    except Exception:
                        print traceback.format_exc()
                        print "keep reading"
                        break
        except KeyboardInterrupt:
            self.serversocket.close()
            print "closed"
            print traceback.format_exc()
            self.connection.close()

        except Exception:
            self.serversocket.close()
            print "closed"
            print traceback.format_exc()
            self.connection.close()

        finally:
            self.serversocket.close()
            print "closed"
            print traceback.format_exc()
            self.connection.close()

    def sync_targets(self):
        targets_to_remove, targets_to_add = self.sync_with_db()
        for target in targets_to_add:
            relative_target = self.soldier.get_relative_target(target)
            print relative_target
            # self.connection.send('add {}\n'.format(json.dumps(relative_target)))
        for target in targets_to_remove:
            target_id = json.dumps(target)['id']
            # self.connection.send('remove {}\n'.format(target_id))

    def update_db(self, target):
        print 'update db... '
        print target
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


if __name__ == '__main__':
    s = SoldierApi()
