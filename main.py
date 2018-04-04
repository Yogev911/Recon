from libs import hcsr04 as ultrasonic
# from libs.mtk3339 import mtk3339
from libs.mtk3339 import mtk3339 as gpsmodule
import time
#from libs.gyro_compass import mpu9150 as gc
my_ultrasonic = ultrasonic.init()
my_ultrasonic = ultrasonic.getDistance()
print my_ultrasonic
time.sleep(1)

gps = gpsmodule.mt3339("/dev/ttyAMA0")
gps.cold_start()
gps.warm_start()
gps.hot_start()
gps.set_baudrate(115200)
gps.set_nmea_update_rate(1000)
gps.set_nav_speed_threshold(1.5)
gps.set_nmea_output(gll = 0, rmc = 1, vtg = 0, gga = 5, gsa = 5, gsv = 5)

gps.set_fix_update_rate(800)
gps.set_nmea_update_rate(800)
gps.set_baudrate(115200)
gps.set_nmea_update_rate(1000)
gps.set_nav_speed_threshold(1.5)
gps.set_nmea_output(gll = 0, rmc = 1, vtg = 0, gga = 5, gsa = 5, gsv = 5)
