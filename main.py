from time import sleep
import math
import os

from utils import conf
from utils import gps_handler as my_gps
from utils import gyro_handler as gyro
from utils import ultrasonic_handler as us


def main():
    print 'gyro:'
    gyro.get_gyro()
    print 'accel:'
    gyro.get_gyro()
    print 'temp:'
    gyro.get_temp()
    print 'azimut:'
    gyro.get_azimut()
    print 'gps:'
    gps.get_location()
    print 'ultra sonic:'
    print us.getDistance()
    os.system('cls' if os.name == 'nt' else 'clear')


def init():
    us.init()


def mark_target():
    distance = us.getDistance()
    latitude = gyro.get_latitude()
    longitude = gyro.get_longitude()

    dx = distance * math.sin(gyro.get_azimut())
    dy = distance * math.cos(gyro.get_azimut())

    delta_longitude = dx/(111320*math.cos(latitude))
    delta_latitude = dy / 110540



    final_longitude = longitude + delta_longitude
    final_latitude =  latitude + delta_latitude




if __name__ == '__main__':
    gps = my_gps.my_gps()
    init()
    while 1:
        main()
        sleep(0.1)
