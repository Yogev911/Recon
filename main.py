import time
import libs.gps_module as gpsm
# my_ultrasonic = ultrasonic.init()
# my_ultrasonic = ultrasonic.getDistance()
# print my_ultrasonic
# time.sleep(1)
#
# gps = gpsm.mt3339("/dev/ttyAMA0")
# gps.cold_start()
# gps.warm_start()
# gps.hot_start()
# gps.set_baudrate(115200)
# gps.set_nmea_update_rate(1000)
# gps.set_nav_speed_threshold(1.5)
# gps.set_nmea_output(gll = 0, rmc = 1, vtg = 0, gga = 5, gsa = 5, gsv = 5)
#
# gps.set_fix_update_rate(800)
# gps.set_nmea_update_rate(800)
# gps.set_baudrate(115200)
# gps.set_nmea_update_rate(1000)
# gps.set_nav_speed_threshold(1.5)
# gps.set_nmea_output(gll = 0, rmc = 1, vtg = 0, gga = 5, gsa = 5, gsv = 5)

from libs.new_gps import GPS
myGPS=GPS()

while(1):
        myGPS.ser.flushInput() #Clear Buffers
        myGPS.ser.flushInput()
        print 'while'
        while myGPS.ser.inWaiting()==0: #Wait for input
                pass
        NMEA1=myGPS.ser.readline()      #Read NMEA1
        while myGPS.ser.inWaiting()==0:
                pass
        NMEA2=myGPS.ser.readline()
        print NMEA1
        print NMEA2

