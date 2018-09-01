from settings import conf
from fpformat import fix
import itertools
import sys

spinner_items = itertools.cycle(['-', '/', '|', '\\'])


def spinner():
    sys.stdout.write(spinner_items.next())  # write the next character
    sys.stdout.flush()  # flush stdout buffer (actual character display)
    sys.stdout.write('\b')  # erase the last written char



def raw_target_format(final_altitude, final_latitude, final_longitude):
    return {
        "altitude": final_altitude,
        "longitude": final_longitude,
        "latitude": final_latitude,
        "reconunitid": conf.RECONUNITID
    }


def client_target_format(bearing, azimuth, distance, target_id):
    return {'id': target_id,
            'azimuth': fix(azimuth, 4),
            'distance': float(distance) * 1000,
            'bearing': fix(bearing, 4)}
