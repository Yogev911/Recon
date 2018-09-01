import traceback
from time import sleep

import coordinate as coord
from gps_handler import my_gps
from lidar_handler import GLLv3
import utils


class ElectronicUnit:
    def __init__(self):
        print 'Setting up Laser.'
        self.laser = GLLv3()

        print 'Setting up GPS'
        self.gps = my_gps()
        self.latitude = None
        self.longitude = None
        self.altitude = None
        print 'waiting for signal'
        self.sync_gps()
        print 'All components are ready! lat: {}, lon: {}, alt: {}'.format(self.latitude, self.longitude, self.altitude)

    def sync_gps(self, intervals=0.1):
        self.update_gps()
        while not (self.latitude and self.longitude and self.altitude):
            utils.spinner()
            self.update_gps()
            sleep(intervals)

    def update_gps(self):
        self.latitude = self.gps.lat
        self.longitude = self.gps.lon
        self.altitude = self.gps.alt
        #self.set_fake_gps_data()

    def set_fake_gps_data(self):
        self.latitude = 32.09002201237831
        self.longitude = 34.80290894928055
        self.altitude = 60

    @property
    def my_coord(self):
        self.sync_gps()
        my_point = coord.Point(altitude=self.altitude, longitude=self.longitude, latitude=self.latitude)
        return my_point

    def mark_target(self, bearing, azimuth):
        # Setting new target cord based on self coord, azimuth, distanse and elevation angle to target
        try:
            final_altitude, final_latitude, final_longitude = coord.get_point(coord_a=self.my_coord,
                                                                              distance=self.laser.read(),
                                                                              azimuth=azimuth,
                                                                              bearing=bearing)
            return utils.raw_target_format(final_altitude, final_latitude, final_longitude)
        except:
            print traceback.format_exc()
            return utils.raw_target_format(self.altitude, self.longitude, self.latitude)

    def get_relative_target(self, target):
        try:
            # get target distance, azimuth and elevation relative to self
            target_coord = coord.Point(latitude=target['latitude'], longitude=target['longitude'],
                                       altitude=target['altitude'])
            bearing, azimuth, distance_km = coord.get_relative_point_position(coord_a=self.my_coord,
                                                                              coord_b=target_coord)
            return utils.client_target_format(bearing, azimuth, distance_km, target['id'])
        except:
            print traceback.format_exc()
            return utils.client_target_format(0, 0, 0, target['id'])
