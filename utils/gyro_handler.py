import time
import sys
import math
import FaBo9Axis_MPU9250

mpu9250 = FaBo9Axis_MPU9250.MPU9250()


def get_accel():
    accel = mpu9250.readAccel()
    print " ax = ", (accel['x'])
    print " ay = ", (accel['y'])
    print " az = ", (accel['z'])


def get_gyro():
    gyro = mpu9250.readGyro()
    print " gx = ", (gyro['x'])
    print " gy = ", (gyro['y'])
    print " gz = ", (gyro['z'])


def get_magnet():
    mag = mpu9250.readMagnet()
    print " mx = ", (mag['x'])
    print " my = ", (mag['y'])
    print " mz = ", (mag['z'])
    print math.atan2(mag['x'], mag['y'])*180/math.pi

def get_temp():
    temp = mpu9250.readTemperature()
    print "temp = ", temp

def get_azimut():
    mag = mpu9250.readMagnet()
    # print " mx = ", (mag['x'])
    # print " my = ", (mag['y'])
    # print " mz = ", (mag['z'])
    azimut = (math.atan2(mag['y'], mag['x']) * 180) / math.pi
    # azimut+=360 if azimut < 0 else azimut
    if azimut <= 0:
        azimut+=360
    print azimut


def _map_azimut(i):
    x = i % 360
    if x > 180:
        x -= 360
    elif x == 180 and i < 0:
        x = -x
    return x
    # try:
    #     while True:
    #         accel = mpu9250.readAccel()
    #         print " ax = " , ( accel['x'] )
    #         print " ay = " , ( accel['y'] )
    #         print " az = " , ( accel['z'] )
    #
    #         gyro = mpu9250.readGyro()
    #         print " gx = " , ( gyro['x'] )
    #         print " gy = " , ( gyro['y'] )
    #         print " gz = " , ( gyro['z'] )
    #
    #         mag = mpu9250.readMagnet()
    #         print " mx = " , ( mag['x'] )
    #         print " my = " , ( mag['y'] )
    #         print " mz = " , ( mag['z'] )
    #         print
    #
    #         time.sleep(0.5)
    #
    # except KeyboardInterrupt:
    #     sys.exit()
