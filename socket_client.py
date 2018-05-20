import socket
from time import sleep
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('192.168.1.23', 8081))
for x in range(1,3):
    clientsocket.send('yogev '+str(x))
    sleep(2)