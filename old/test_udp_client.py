import socket  # for sockets
import sys  # for exit

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

port = 8081

host = '192.168.43.221'
msg = 'mark elv -5.87 azimuth 17.26'
try:
    s.sendto(msg, (host,port))
except socket.error, msg:
    print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()