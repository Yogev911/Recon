import math
from time import sleep
from fpformat import fix
import traceback

import conf

from utils import gps_handler as my_gps
from utils import gyro_handler as gyro
from utils import ultrasonic_handler as us


class Soldier():
    def __init__(self, service_connection):
        self.gps = my_gps.my_gps()
        self.should_run = True
        self.distance = None
        self.latitude = None
        self.longitude = None
        self.azimut = None
        self.final_longitude = None
        self.final_latitude = None
        self.init()

    def run(self):
        while self.should_run:
            try:
                sleep(conf.SOLDIER_SCAN_INTERVAL)
                self.distance = us.getDistance()
                self.latitude = self.gps.lat
                self.longitude = self.gps.lon
                self.azimut = gyro.get_azimut()

                dx = self.distance * math.sin(self.azimut)
                dy = self.distance * math.cos(self.azimut)

                delta_longitude = dx / (111320 * math.cos(self.latitude))
                delta_latitude = dy / 110540

                self.final_longitude = fix(self.longitude + delta_longitude, 6)
                self.final_latitude = fix(self.latitude + delta_latitude, 6)
                print  "lat: {} lon: {}".format(self.final_latitude, self.final_longitude)
            except Exception:
                print traceback.format_exc()

            except KeyboardInterrupt:
                self.should_run = False

    def init(self):
        us.init()

    def mark_target(self):
        try:
            self.distance = us.getDistance()
            self.latitude = self.gps.lat
            self.longitude = self.gps.lon
            self.azimut = gyro.get_azimut()

            dx = self.distance * math.sin(self.azimut)
            dy = self.distance * math.cos(self.azimut)

            delta_longitude = dx / (111320 * math.cos(self.latitude))
            delta_latitude = dy / 110540

            self.final_longitude = fix(self.longitude + delta_longitude, 6)
            self.final_latitude = fix(self.latitude + delta_latitude, 6)
            print  "lat: {} lon: {}".format(self.final_latitude, self.final_longitude)
        except Exception:
            print traceback.format_exc()


if __name__ == '__main__':
    s1 = Soldier('test')
