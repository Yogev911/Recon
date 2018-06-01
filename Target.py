import math
import traceback
from fpformat import fix
from time import sleep
from math import sin, cos, sqrt, atan2, radians

from utils import gps_handler as my_gps, conf
from utils import gyro_handler as gyro
from utils import ultrasonic_handler as us

R = 6373.0


class Target():
    def __init__(self):
        print 'setting up all components'
        self.gps = my_gps.my_gps()
        self.should_run = True
        self.distance = None
        self.latitude = self.gps.lat
        self.longitude = self.gps.lon
        self.altitude = self.gps.alt
        self.azimut = None
        self.final_longitude = None
        self.final_latitude = None
        self.init()

    def update_gps(self):
        self.latitude = self.gps.lat
        self.longitude = self.gps.lon
        self.altitude = self.gps.alt

    def get_data(self):
        self.update_gps()
        print self.latitude
        print self.longitude
        print self.altitude

    def init(self):
        print 'init laser'
        us.init()
        self.distance = us.getDistance()
        print 'calibrate GPS.. may take few minuets'
        while not (self.latitude and self.longitude and self.altitude):
            print 'waiting for signal'
            self.latitude = self.gps.lat
            self.longitude = self.gps.lon
            self.altitude = self.gps.alt
            sleep(0.5)

        print self.latitude
        print self.longitude
        print self.altitude

    def mark_target(self, alpha, azimut):
        try:
            hypotenuse = us.getDistance()
            self.distance = hypotenuse * math.cos(alpha)
            leg = hypotenuse * math.sin(alpha)
            self.latitude = self.gps.lat
            self.longitude = self.gps.lon
            self.altitude = self.gps.alt
            self.azimut = azimut  # gyro.get_azimut()

            dx = self.distance * math.sin(self.azimut)
            dy = self.distance * math.cos(self.azimut)

            delta_longitude = dx / (111320 * math.cos(self.latitude))
            delta_latitude = dy / 110540

            self.final_longitude = fix(self.longitude + delta_longitude, 6)
            self.final_latitude = fix(self.latitude + delta_latitude, 6)
            print  "lat: {} lon: {}".format(self.final_latitude, self.final_longitude)
            target_altitude = self.altitude + leg
            target = {
                "altitude": target_altitude,
                "longitude": self.final_longitude,
                "latitude": self.final_latitude
            }
            return target
        except Exception:
            print traceback.format_exc()

    def get_relative_target(self, target):
        azimuth = 0
        distKm = 0
        altitude = 0

        b = {'lat': self.latitude, 'lon': self.longitude, 'alt': self.altitude}
        # print 'self coords:' +  str(b)
        bp = self._location_to_point(b)
        a = {'lat': float(target['latitude']), 'lon': float(target['longitude']), 'alt': float(target['altitude'])}
        # print 'target coords:' + str(a)
        ap = self._location_to_point(a)

        distKm = fix(0.001 * self._target_distance(ap, bp), 3)
        br = self._rotate_globe(b, a, bp['radius'], ap['radius'])
        if (br['z'] * br['z'] + br['y'] * br['y'] > 1.0e-06):
            theta = math.atan2(br['z'], br['y']) * 180.0 / math.pi
            azimuth = 90.0 - theta
            if (azimuth < 0.0):
                azimuth += 360.0
            if (azimuth > 360.0):
                azimuth -= 360.0

        bma = self._normalize_vector_diff(bp, ap)
        if bma:
            altitude = 90.0 - (180.0 / math.pi) * math.acos(
                bma['x'] * ap['nx'] + bma['y'] * ap['ny'] + bma['z'] * ap['nz'])

        return {'id': target['id'], 'azimut': fix(azimuth, 4), 'distance': float(distKm) * 1000,
                'altitude': fix(altitude, 4)}

    def _location_to_point(self, new_target):

        lat = new_target['lat'] * math.pi / 180.0
        lon = new_target['lon'] * math.pi / 180.0
        t1 = 6378137.0 * 6378137.0 * math.cos(lat)
        t2 = 6356752.3 * 6356752.3 * math.sin(lat)
        t3 = 6378137.0 * math.cos(lat)
        t4 = 6356752.3 * math.sin(lat)
        radius = math.sqrt((t1 * t1 + t2 * t2) / (t3 * t3 + t4 * t4))
        clat = math.atan((1.0 - 0.00669437999014) * math.tan(lat))

        cosLon = math.cos(lon)
        sinLon = math.sin(lon)
        cosLat = math.cos(clat)
        sinLat = math.sin(clat)
        x = radius * cosLon * cosLat
        y = radius * sinLon * cosLat
        z = radius * sinLat
        cosGlat = math.cos(lat)
        sinGlat = math.sin(lat)
        nx = cosGlat * cosLon
        ny = cosGlat * sinLon
        nz = sinGlat
        x += new_target['alt'] * nx
        y += new_target['alt'] * ny
        z += new_target['alt'] * nz
        return {'x': x, 'y': y, 'z': z, 'radius': radius, 'nx': nx, 'ny': ny, 'nz': nz};

    def _target_distance(self, self_point, new_point):
        dx = self_point['x'] - new_point['x']
        dy = self_point['y'] - new_point['y']
        dz = self_point['z'] - new_point['z']
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def _rotate_globe(self, b, a, bradius, aradius):
        br = {'lat': b['lat'], 'lon': (b['lon'] - a['lon']), 'alt': b['alt']}
        brp = self._location_to_point(br)
        alat = -a['lat'] * math.pi / 180.0
        alat = math.atan((1.0 - 0.00669437999014) * math.tan(alat))
        acos = math.cos(alat)
        asin = math.sin(alat)
        bx = (brp['x'] * acos) - (brp['z'] * asin)
        by = brp['y']
        bz = (brp['x'] * asin) + (brp['z'] * acos)
        return {'x': bx, 'y': by, 'z': bz, 'radius': bradius}

    def _normalize_vector_diff(self, b, a):
        dx = b['x'] - a['x']
        dy = b['y'] - a['y']
        dz = b['z'] - a['z']
        dist2 = dx * dx + dy * dy + dz * dz
        if dist2 == 0:
            return None
        dist = math.sqrt(dist2)
        return {'x': (dx / dist), 'y': (dy / dist), 'z': (dz / dist), 'radius': 1.0}
