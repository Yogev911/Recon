from fpformat import fix
from math import sin, cos, sqrt, atan2, radians, pi, acos, tan, atan, asin, degrees

def mark_target(elevation, azimuth,hypotenuse = 100.0):
    # Setting new target cord based on self coord, azimuth, distanse and elevation angle to target
        R = 6371e3
        azimuth = radians(azimuth)
        distance = hypotenuse * cos(elevation)
        delta_alt = hypotenuse * sin(elevation)
        delta = distance / R

        print ''
        longitude = radians(longitude)
        latitude = radians(latitude)

        final_latitude = asin(sin(latitude) * cos(delta) +
                              cos(latitude) * sin(delta) * cos(azimuth))
        final_longitude = longitude + atan2(sin(azimuth) * sin(delta) * cos(a.latitude),
                                              cos(delta) - sin(a.latitude) * sin(final_latitude))

        final_latitude = degrees(final_latitude)
        final_longitude = degrees(final_longitude)
        final_altitude = altitude + delta_alt
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