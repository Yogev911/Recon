import serial  # import pyserial library
import pynmea2
from time import sleep  # import sleep library
import threading

import conf

ser = serial.Serial('/dev/ttyAMA0', 9600)  # Initialize Serial Port


class my_gps:  # Create GPS class
    def __init__(self):  # This init will run when you create a GPS object.
        # This sets up variables for useful commands.
        # This set is used to set the rate the GPS reports
        self.NMEA1 = None
        self.NMEA2 = None
        ser.write(conf.BAUD_57600)  # Set Baud Rate to 57600
        sleep(1)  # Paulse
        ser.baudrate = 57600  # IMPORTANT Since change ser baudrate to match GPS
        sleep(1)
        ser.write(conf.WARM_START)  # Set update rate
        sleep(1)
        ser.write(conf.UPDATE_200_msec)  # Set update rate
        sleep(1)
        ser.write(conf.MEAS_200_msec)  # Set measurement rate
        sleep(1)
        ser.write(conf.GPRMC_GPGGA)  # Ask for only GPRMC and GPGGA Sentences
        sleep(1)
        ser.flushInput()  # clear buffers
        ser.flushOutput()
        print "GPS is Initialized"  # Print message

    def get_location(self):
        while ser.inWaiting() == 0:  # Wait for input
            pass
        self.NMEA1 = ser.readline()  # Read NMEA1
        self.NMEA2 = ser.readline()
        print self.NMEA1
        cord = pynmea2.parse(self.NMEA1)
        print cord.timestamp
        print cord.lat_dir
        print cord.lon
        print cord.lon_dir
        print cord.gps_qual
        print cord.num_sats
        print cord.horizontal_dil
        print cord.altitude
        print cord.altitude_units
        print cord.geo_sep
        print cord.geo_sep_units
        print cord.age_gps_data
        print cord.ref_station_id


        # print pynmea2.parse(self.NMEA2)
        # print self.NMEA2

# myGPS = my_gps()
# while (1):
#     # ser.flushInput() #Clear Buffers
#     # ser.flushInput()
#     while ser.inWaiting() == 0:  # Wait for input
#         pass
#     NMEA1 = ser.readline()  # Read NMEA1
#     NMEA2 = ser.readline()
#     print pynmea2.parse(NMEA1)
#     print NMEA1
#     print pynmea2.parse(NMEA2)
#     print NMEA2
#     print '******************'
