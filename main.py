from libs import hcsr04 as ultrasonic
#from libs.mtk3339 import mtk3339 as gps
import time
#from libs.gyro_compass import mpu9150 as gc
my_ultrasonic = ultrasonic.init()
while True:
	my_ultrasonic = ultrasonic.getDistance()
	print my_ultrasonic
	time.sleep(1)
