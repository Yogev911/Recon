import math
from fpformat import fix
from time import sleep  # import sleep library

import pynmea2
import serial  # import pyserial library

from utils import conf

ser = serial.Serial('/dev/ttyAMA0', 9600)  # Initialize Serial Port
COMPASS = {'N': -1, 'E': 1, 'W': -1, 'S': -1}


class my_gps:  # Create GPS class
    def __init__(self):  # This init will run when you create a GPS object.
        # This sets up variables for useful commands.
        # This set is used to set the rate the GPS reports
        self.NMEA = None
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
        ser.write(conf.GPGGA_ONLY)  # Ask for only GPRMC and GPGGA Sentences
        sleep(1)
        ser.flushInput()  # clear buffers
        ser.flushOutput()
        print "GPS is Initialized"  # Print message

    @property
    def lat(self):
        mult = 1.0

        while ser.inWaiting() == 0:  # Wait for input
            pass
        lat = pynmea2.parse(ser.readline()).lat
        if lat == '':
            return None
        deg = lat[:2]
        mins = lat[2:]
        sec = math.fabs((float(mins) - (int(float(mins))) * 60))
        return mult * float(fix((float(deg) + float(mins) / 60), 6))

    @property
    def lat_dir(self):
        while ser.inWaiting() == 0:  # Wait for input
            pass
        return pynmea2.parse(ser.readline()).lat_dir

    @property
    def alt(self):
        while ser.inWaiting() == 0:  # Wait for input
            pass
        return pynmea2.parse(ser.readline()).altitude

    @property
    def lon(self):
        while ser.inWaiting() == 0:  # Wait for input
            pass
        lon = pynmea2.parse(ser.readline()).lon
        if lon == '':
            return None
        mult = 1.0
        deg = int(lon[:3])
        mins = float(lon[3:])
        sec = math.fabs((mins - (int(mins)) * 60))
        return mult * float(fix((deg + mins / 60), 6))

    @property
    def lon_dir(self):
        while ser.inWaiting() == 0:  # Wait for input
            pass
        return pynmea2.parse(ser.readline()).lon_dir

    def get_location(self):
        while ser.inWaiting() == 0:  # Wait for input
            pass
        self.NMEA = ser.readline()  # Read NMEA1
        print self.NMEA
        cord = pynmea2.parse(self.NMEA)
        attrs = vars(cord)
        print ', '.join("%s: %s" % item for item in attrs.items())

    def get_latitude(self):
        while ser.inWaiting() == 0:  # Wait for input
            pass
        lat = pynmea2.parse(ser.readline()).lat
        mult = -1
        print type(lat)
        deg = int(lat[:2])
        mins = float(lat[2:])
        sec = math.fabs((mins - (int(mins)) * 60))
        dd = mult * float(fix((deg + mins / 60), 6))
        print deg
        print mins
        print sec
        print dd
        return dd

    def get_longitude(self):
        return None

