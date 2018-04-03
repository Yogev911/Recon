from libs import hcsr04 as ultrasonic
from libs.mtk3339 import mtk3339 as gps

from libs.gyro_compass import mpu9150 as gc

my_ultrasonic = ultrasonic.getDistance()
print my_ultrasonic