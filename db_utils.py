import json
from time import sleep

from requests import post, get, delete

from settings import conf


class db():
    def __init__(self):
        self.root = "https://reconsevice.herokuapp.com/"
        self.target = "target/"
        self.reconunit = 'reconunit/'
        self.msg = 'message/'

    def send_target(self, target):
        res = post(self.root + self.target, json=target)
        if res.status_code != 200:
            print 'error update db'
            print res.json()

    def get_target(self, target_id):
        return get(self.root + self.target + target_id)

    def get_targets(self):
        res = get(self.root + self.target)
        if res.status_code == 200:
            responds = json.loads(res.content)
            if responds['success']:
                return responds['data']
            else:
                print 'host unavailable'
                sleep(2)
                return None
        else:
            print 'host unavailable'
            sleep(2)
            return None

    def delete_target(self, target_id):
        return delete(self.root + self.target + target_id)

    def gets_msg(self):
        res = get(self.root + self.msg + str(conf.RECONUNITID))
        if res.status_code == 200:
            responds = json.loads(res.content)
            if responds['success']:
                return responds['data']
            else:
                print 'host unavailable'
                sleep(2)
                return None
