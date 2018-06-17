import traceback
import itertools, sys
from fpformat import fix
from time import sleep
from math import sin, cos, sqrt, atan2, radians, pi, acos, tan, atan, asin, degrees

from utils import gps_handler as my_gps, conf

# from utils import ultrasonic_handler as us

spinner = itertools.cycle(['-', '/', '|', '\\'])


class Target():
    def __init__(self):
        print 'setting up all components'
        # self.gps = my_gps.my_gps()
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self._init()

    def get_fake_gps_data(self):
        self.latitude = 32.0897516667
        self.longitude = 34.8025283333
        self.altitude = 29.6

    def update_gps(self):
        self.get_fake_gps_data()
        return
        self.gps.read
        self.latitude = self.gps.lat
        self.longitude = self.gps.lon
        self.altitude = self.gps.alt

    def print_gps_data(self):
        self.update_gps()
        print self.latitude, self.longitude, self.altitude

    def _init(self):
        # TODO: get new laser!
        print 'init laser.. skip it.'
        # us.init()
        distance = 20  # us.getDistance()
        if not distance:
            print 'Warrning laser is not working!'

        print 'calibrating GPS.. may take few minuets'
        print 'waiting for signal'
        self.sync_gps()
        print 'All components are ready! lat: {}, lon: {}, alt: {}'.format(self.latitude, self.longitude, self.altitude)

    def sync_gps(self, intervals=0.1):
        self.update_gps()
        while not (self.latitude and self.longitude and self.altitude):
            self.update_gps()
            sys.stdout.write(spinner.next())  # write the next character
            sys.stdout.flush()  # flush stdout buffer (actual character display)
            sys.stdout.write('\b')  # erase the last written char
            sleep(intervals)

    def mark_target(self, alpha, azimut):
        # Setting new target cord based on self coord, azimuth, distanse and elevation angle to target
        try:
            R = 6371e3
            self.sync_gps(intervals=0.01)
            alpha = float(alpha)
            hypotenuse = 20.0  # Distance from the laser.
            distance = hypotenuse * cos(alpha)
            delta_alt = hypotenuse * sin(alpha)
            tetha = radians(float(azimut))
            delta = distance / R

            print ''
            self.longitude = radians(self.longitude)
            self.latitude = radians(self.latitude)

            final_latitude = asin(sin(self.latitude) * cos(delta) +
                                  cos(self.latitude) * sin(delta) * cos(tetha))
            final_longitude = self.longitude + atan2(sin(tetha) * sin(delta) * cos(self.latitude),
                                                     cos(delta) - sin(self.latitude) * sin(final_latitude))

            final_altitude = self.altitude + delta_alt
            final_latitude = degrees(final_latitude)
            final_longitude = degrees(final_longitude)
            return self.create_target_json(final_altitude, final_latitude, final_longitude)
        except Exception:
            print traceback.format_exc()
            return self.create_target_json(self.altitude, self.longitude, self.latitude)

    @staticmethod
    def create_target_json(final_altitude, final_latitude, final_longitude):
        return {
            "altitude": final_altitude,
            "longitude": final_longitude,
            "latitude": final_latitude,
            "reconunitid": conf.RECONUNITID
        }

    def get_relative_target(self, target):
        try:
            # get target distance, azimuth and elevation relative to self
            self.sync_gps()
            self_data = {'lat': self.latitude, 'lon': self.longitude, 'alt': self.altitude}
            target_data = {'lat': float(target['latitude']), 'lon': float(target['longitude']),
                           'alt': float(target['altitude'])}


            ap = self._location_to_point(target_data)
            bp = self._location_to_point(self_data)

            distKm = fix(0.001 * self._target_distance(ap, bp), 3)
            br = self._rotate_globe(target_data, self_data, bp['radius'])
            if br['z'] * br['z'] + br['y'] * br['y'] > 1.0e-06:
                theta = atan2(br['z'], br['y']) * 180.0 / pi
                azimuth = 90.0 - theta
                if (azimuth < 0.0):
                    azimuth += 360.0
                if (azimuth > 360.0):
                    azimuth -= 360.0
            else:
                azimuth = 0.0

            bma = self._normalize_vector_diff(ap, bp)
            if bma:
                altitude = 90.0 - (180.0 / pi) * acos(
                    bma['x'] * bp['nx'] + bma['y'] * bp['ny'] + bma['z'] * bp['nz'])
            else:
                altitude = 0.0
            return self.relative_target_json(altitude, azimuth, distKm, target)
        except:
            print traceback.format_exc()
            return self.relative_target_json(0, 0, 0, target)

    def _rotate_globe(self, b, a, bradius):
        br = {'lat': b['lat'], 'lon': (b['lon'] - a['lon']), 'alt': b['alt']}
        brp = self._location_to_point(br)
        alat = -a['lat'] * pi / 180.0
        alat = atan((1.0 - 0.00669437999014) * tan(alat))
        acos = cos(alat)
        asin = sin(alat)
        bx = (brp['x'] * acos) - (brp['z'] * asin)
        by = brp['y']
        bz = (brp['x'] * asin) + (brp['z'] * acos)
        return {'x': bx, 'y': by, 'z': bz, 'radius': bradius}

    @staticmethod
    def relative_target_json(altitude, azimuth, distKm, target):
        return {'id': target['id'], 'azimut': fix(azimuth, 4), 'distance': float(distKm) * 1000,
                'altitude': fix(altitude, 4)}

    @staticmethod
    def _location_to_point(new_target):
        lat = new_target['lat'] * pi / 180.0
        lon = new_target['lon'] * pi / 180.0
        t1 = 6378137.0 * 6378137.0 * cos(lat)
        t2 = 6356752.3 * 6356752.3 * sin(lat)
        t3 = 6378137.0 * cos(lat)
        t4 = 6356752.3 * sin(lat)
        radius = sqrt((t1 * t1 + t2 * t2) / (t3 * t3 + t4 * t4))
        clat = atan((1.0 - 0.00669437999014) * tan(lat))

        cosLon = cos(lon)
        sinLon = sin(lon)
        cosLat = cos(clat)
        sinLat = sin(clat)
        x = radius * cosLon * cosLat
        y = radius * sinLon * cosLat
        z = radius * sinLat
        cosGlat = cos(lat)
        sinGlat = sin(lat)
        nx = cosGlat * cosLon
        ny = cosGlat * sinLon
        nz = sinGlat
        x += new_target['alt'] * nx
        y += new_target['alt'] * ny
        z += new_target['alt'] * nz
        return {'x': x, 'y': y, 'z': z, 'radius': radius, 'nx': nx, 'ny': ny, 'nz': nz};

    @staticmethod
    def _target_distance(self_point, new_point):
        dx = self_point['x'] - new_point['x']
        dy = self_point['y'] - new_point['y']
        dz = self_point['z'] - new_point['z']
        return sqrt(dx * dx + dy * dy + dz * dz)

    @staticmethod
    def _normalize_vector_diff(b, a):
        dx = b['x'] - a['x']
        dy = b['y'] - a['y']
        dz = b['z'] - a['z']
        dist2 = dx * dx + dy * dy + dz * dz
        if dist2 == 0:
            return None
        dist = sqrt(dist2)
        return {'x': (dx / dist), 'y': (dy / dist), 'z': (dz / dist), 'radius': 1.0}
