# from libs.mpu9150 import mpu9150
# import libs.raspberrypi.adafruit_i2c_interface as i2c_bus
# from time import sleep
# dev = i2c_bus.Device()
# imu = mpu9150(dev)
# print 'statring'
# while 1:
#     print '*\t*\t*\t*\t*\t*\t*\t*'
#     print imu.read_y_acc()
#     sleep(0.001)
#     print imu.read_x_acc_raw()
#     sleep(0.001)
#     print imu.read_x_acc()
#     sleep(0.001)
#     print imu.get_acc_sensitivity()
#     sleep(0.001)
#     print imu.read_y_acc_raw()
#     sleep(0.001)
#     print imu.read_z_acc()
#     sleep(0.001)
#     print imu.read_z_acc_raw()
#     sleep(1)
# print 'done'


# coding: utf-8
## @package faboMPU9250
#  This is a library for the FaBo 9AXIS I2C Brick.
#
#  http://fabo.io/202.html
#
#  Released under APACHE LICENSE, VERSION 2.0
#
#  http://www.apache.org/licenses/
#
#  FaBo <info@fabo.io>

import FaBo9Axis_MPU9250
import time
import sys

mpu9250 = FaBo9Axis_MPU9250.MPU9250()

try:
    while True:
        accel = mpu9250.readAccel()
        print " ax = " , ( accel['x'] )
        print " ay = " , ( accel['y'] )
        print " az = " , ( accel['z'] )

        gyro = mpu9250.readGyro()
        print " gx = " , ( gyro['x'] )
        print " gy = " , ( gyro['y'] )
        print " gz = " , ( gyro['z'] )

        mag = mpu9250.readMagnet()
        print " mx = " , ( mag['x'] )
        print " my = " , ( mag['y'] )
        print " mz = " , ( mag['z'] )
        print

        time.sleep(0.5)

except KeyboardInterrupt:
    sys.exit()