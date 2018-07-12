import itertools
import sys
import traceback
from fpformat import fix
from time import sleep


import coordinate as coord
from gps_handler import my_gps
from lidar_handler import GLLv3
from settings import conf

spinner = itertools.cycle(['-', '/', '|', '\\'])


def _spin():
    sys.stdout.write(spinner.next())  # write the next character
    sys.stdout.flush()  # flush stdout buffer (actual character display)
    sys.stdout.write('\b')  # erase the last written char


def create_target_json(final_altitude, final_latitude, final_longitude):
    return {
        "altitude": final_altitude,
        "longitude": final_longitude,
        "latitude": final_latitude,
        "reconunitid": conf.RECONUNITID
    }


def relative_target_json(altitude, azimuth, distance_km, target_id):
    return {'id': target_id,
            'azimut': fix(azimuth, 4),
            'distance': float(distance_km) * 1000,
            'altitude': fix(altitude, 4)}


class Target():
    def __init__(self):
        print 'setting up all components'
        self.laser = GLLv3()
        self.laser.read()
        self.latitude = None
        self.longitude = None
        self.altitude = None
        print 'calibrating GPS.. may take few minuets'
        self.gps = my_gps()
        print 'waiting for signal'
        self.sync_gps(intervals=0.1)
        print 'All components are ready! lat: {}, lon: {}, alt: {}'.format(self.latitude, self.longitude, self.altitude)

    def get_fake_gps_data(self):
        self.latitude = 32.09002201237831
        self.longitude = 34.80290894928055
        self.altitude = 60

    def print_gps_data(self):
        self.sync_gps()
        print self.latitude, self.longitude, self.altitude

    @property
    def my_coord(self):
        self.sync_gps()
        my_point = coord.Point(altitude=self.altitude, longitude=self.longitude, latitude=self.latitude)
        return my_point

    def update_gps(self):
        self.get_fake_gps_data()
        return
        self.gps.read()
        self.latitude = self.gps.lat
        self.longitude = self.gps.lon
        self.altitude = self.gps.alt

    def sync_gps(self, intervals=0.01):

        self.update_gps()
        while not (self.latitude and self.longitude and self.altitude):
            _spin()
            self.update_gps()
            sleep(intervals)

    def mark_target(self, alpha, azimuth):
        # Setting new target cord based on self coord, azimuth, distanse and elevation angle to target
        try:
            final_altitude, final_latitude, final_longitude = coord.get_point(coord_a=self.my_coord,
                                                                              distance=self.laser.read(),
                                                                              azimuth=azimuth, bearing=alpha)
            return create_target_json(final_altitude, final_latitude, final_longitude)
        except Exception:
            print traceback.format_exc()
            return create_target_json(self.altitude, self.longitude, self.latitude)

    def get_relative_target(self, target):
        try:
            # get target distance, azimuth and elevation relative to self
            target_coord = coord.Point(latitude=target['latitude'],longitude=target['longitude'],altitude=['altitude'])
            bearing, azimuth, distance_km = coord.get_relative_point_position(coord_a=self.my_coord,coord_b=target_coord)
            return relative_target_json(bearing, azimuth, distance_km, target['id'])
        except:
            print traceback.format_exc()
            return relative_target_json(0, 0, 0, target['id'])
