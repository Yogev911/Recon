import socket  # for sockets
import sys  # for exit

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

port = 12346

host = '192.168.1.25'
msg = 'remove: id 126'
try:
    s.sendto(msg, (host,port))
except socket.error, msg:
    print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()