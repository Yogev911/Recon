import socket
import traceback
from multiprocessing import Process , Queue
# from Soldier import Soldier


class SocketApi():
    def __init__(self,q):

        # self.s = Soldier()
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind(('0.0.0.0', 8081))
        self.serversocket.listen(5)  # become a server socket, maximum 5 connections
        self.should_run = True
        self.command = ''
        self.run()

    def run(self):
        print 'Running...'
        try:
            while self.should_run:
                print 'outside loop'
                self.connection, self.address = self.serversocket.accept()
                print 'found client {}'.format(self.address[0])
                while True:
                    try:
                        print 'innet loop'
                        buf = self.connection.recv(64)
                        if len(buf) > 0:
                            if buf == 'stop'.lower():
                                print 'killing connection'
                                self.connection.close()
                                break
                            print 'reading from {}'.format(self.address[0])
                            print buf
                            cords = buf.split(' ')
                            self.x = cords[0]
                            self.y = cords[1]
                            self.z = cords[2]

                            command = buf
                            # if command == 'mark_target':
                            #     connection.send(self.s.mark_target() + '\n')
                            #     q.put(command)
                            #     msg = q.get()
                            #     if msg == '':
                            #         connection.send(msg + '\n')
                            #     else:
                            #         connection.send(msg + '\n')
                            self.connection.send('Yogev the king\n')
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

if __name__ == '__main__':
    s = SocketApi('')