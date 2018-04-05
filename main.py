from libs.mpu9150 import mpu9150
import libs.raspberrypi.adafruit_i2c_interface as i2c_bus
from time import sleep
dev = i2c_bus.Device()
imu = mpu9150(dev)
print 'statring'
while 1:
    print '*\t*\t*\t*\t*\t*\t*\t*'
    print imu.read_y_acc()
    sleep(0.001)
    print imu.read_x_acc_raw()
    sleep(0.001)
    print imu.read_x_acc()
    sleep(0.001)
    print imu.get_acc_sensitivity()
    sleep(0.001)
    print imu.read_y_acc_raw()
    sleep(0.001)
    print imu.read_z_acc()
    sleep(0.001)
    print imu.read_z_acc_raw()
    sleep(1)
print 'done'