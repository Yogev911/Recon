import socket
from time import sleep
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('192.168.1.23', 8081))
clientsocket.send('mark ally')
sleep(5)
clientsocket.send('stop')