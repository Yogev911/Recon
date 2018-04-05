import libs.mpu9150 as compass
import libs.adafruit_i2c_interface as i2c_bus
bus = i2c_bus.Device()
imu = compass.mpu9150(bus)
print 'statring'
print imu.read_x_acc_raw()
print imu.read_x_acc_raw()
print 'done'