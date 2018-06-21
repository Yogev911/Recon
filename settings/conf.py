import imp
import os

print os.environ
env = os.environ.get('IDE_PROJECT_ROOTS','recon1') +'.py'
conf = imp.load_source('reconConf',env)