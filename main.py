import api
from Soldier import Soldier
from multiprocessing import Pipe, Process, Queue
from socket_server import SocketApi


if __name__ == '__main__':
    q = Queue()

    Process(target=api.run,args=(q,)).start()
    Process(target=Soldier,args=(q,)).start()
    Process(target=SocketApi,args=(q,)).start()
