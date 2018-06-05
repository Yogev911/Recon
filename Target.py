import traceback
import itertools, sys
from fpformat import fix
from time import sleep
from math import sin, cos, sqrt, atan2, radians, pi, acos, tan, atan

from utils import gps_handler as my_gps, conf
# from utils import ultrasonic_handler as us

spinner = itertools.cycle(['-', '/', '|', '\\'])

# R = 6373.0


class Target():
    def __init__(self):
        print 'setting up all components'
        self.gps = my_gps.my_gps()
        self.should_run = True
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self._init()

    def update_gps(self):
        self.gps.read
        self.latitude = self.gps.lat
        self.longitude = self.gps.lon
        self.altitude = self.gps.alt

    def _init(self):
        # TODO: get new laser!
        print 'init laser.. skip it.'
        # us.init()
        distance = 20  # us.getDistance()
        if not distance:
            print 'Warrning laser is not working!'

        print 'calibrating GPS.. may take few minuets'
        print 'waiting for signal'
        while not (self.latitude and self.longitude and self.altitude):
            self.update_gps()
            sys.stdout.write(spinner.next())  # write the next character
            sys.stdout.flush()  # flush stdout buffer (actual character display)
            sys.stdout.write('\b')  # erase the last written char
            sleep(0.1)
        print 'All components are ready! lat: {}, lon: {}, alt: {}'.format(self.latitude, self.longitude, self.altitude)

    def mark_target(self, alpha, azimut):
        # Setting new target cord based on self coord, azimuth, distanse and elevation angle to target
        try:
            self.update_gps()
            alpha = float(alpha)
            azimut = float(azimut)

            # find the delta altitude of the target
            hypotenuse = 20  # Distance from the laser.
            distance = hypotenuse * cos(alpha)
            delta_alt = hypotenuse * sin(alpha)

            # get target coords
            dx = distance * sin(azimut)
            dy = distance * cos(azimut)
            delta_longitude = dx / (111320 * cos(self.latitude))
            delta_latitude = dy / 110540

            final_longitude = fix(self.longitude + delta_longitude, 6)
            final_latitude = fix(self.latitude + delta_latitude, 6)
            final_altitude = self.altitude + delta_alt

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
            target_params = {'lat': self.latitude, 'lon': self.longitude, 'alt': self.altitude}
            self_params = {'lat': float(target['latitude']), 'lon': float(target['longitude']),
                           'alt': float(target['altitude'])}
            bp = self._location_to_point(self_params)
            ap = self._location_to_point(target_params)

            distKm = fix(0.001 * self._target_distance(ap, bp), 3)
            br = self._rotate_globe(self_params, target_params, bp['radius'])
            if br['z'] * br['z'] + br['y'] * br['y'] > 1.0e-06:
                theta = atan2(br['z'], br['y']) * 180.0 / pi
                azimuth = 90.0 - theta
                if (azimuth < 0.0):
                    azimuth += 360.0
                if (azimuth > 360.0):
                    azimuth -= 360.0
            else:
                azimuth = 0.0

            bma = self._normalize_vector_diff(bp, ap)
            if bma:
                altitude = 90.0 - (180.0 / pi) * acos(
                    bma['x'] * ap['nx'] + bma['y'] * ap['ny'] + bma['z'] * ap['nz'])
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
