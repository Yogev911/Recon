from time import sleep

from utils import conf
from utils import gps_handler as my_gps
from utils import gyro_handler as gyro
from utils import ultrasonic_handler as us


def main():
    print 'gyro:'
    gyro.get_gyro()
    print 'accel:'
    gyro.get_gyro()
    # print 'magnet'
    # gyro.get_magnet()
    print 'temp:'
    gyro.get_temp()
    print 'azimut:'
    gyro.get_azimut()
    print 'gps:'
    gps.get_location()
    print 'ultra sonic:'
    print us.getDistance()


def init():
    us.init()

if __name__ == '__main__':
    gps = my_gps.my_gps()
    init()
    while 1:
        main()
        sleep(1)
