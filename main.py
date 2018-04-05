from libs.mpu9150 import mpu9150
import libs.raspberrypi.adafruit_i2c_interface as i2c_bus
dev = i2c_bus.Device()
imu = mpu9150(dev)
print 'statring'
print imu.read_x_acc_raw()
print imu.read_y_acc()
print 'done'