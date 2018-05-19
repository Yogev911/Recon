import api
from Soldier import Target
from multiprocessing import Pipe, Process, Queue
from socket_server import SoldierApi


if __name__ == '__main__':
    q = Queue()

    Process(target=api.run,args=(q,)).start()
    Process(target=Target, args=(q,)).start()
    Process(target=SoldierApi, args=(q,)).start()
