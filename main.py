import libs.mpu9150 as compass
imu = compass.mpu9150(3)
print 'statring'
print imu.read_x_acc_raw()
print imu.read_x_acc_raw()
print 'done'

imu = compass.mpu9150(5)
print 'statring'
print imu.read_x_acc_raw()
print imu.read_x_acc_raw()
print 'done'