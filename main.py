import libs.mpu9150 as compass
import libs.adafruit_i2c_interface as i2c_bus
imu = compass.mpu9150(i2c_bus.Device())
print 'statring'
print imu.read_x_acc_raw()
print imu.read_x_acc_raw()
print 'done'