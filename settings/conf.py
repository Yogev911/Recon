import imp
import socket
import os

env = socket.gethostname()
print 'working on {}'.format(env)
try:
    conf = imp.load_source('Config', os.path.join('settings', env + '.py'))
except IOError:
    print 'cant find {}.py, using default conf'.format(env)
    conf = imp.load_source('Config', 'settings/recon1.py')
