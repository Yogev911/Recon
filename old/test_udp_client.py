import socket  # for sockets
import sys  # for exit

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

port = 8081

host = 'recon2'
msg = 'start'
try:
    s.sendto(msg, (host,port))
except socket.error, msg:
    print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()