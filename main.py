from libs.gyro_compass import mpu9150 as compass
imu = compass.MPU9150(3)
print 'statring'
print(imu.accel.xyz)
print(imu.gyro.xyz)
print(imu.mag.xyz)
print(imu.temperature)
print(imu.accel.z)
print 'done'