import json
from werkzeug.utils import secure_filename
from werkzeug.datastructures import ImmutableMultiDict
from flask_cors import CORS
from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
from time import sleep
import traceback
import api_handler
import math
import threading

from utils import conf
from utils import gps_handler as my_gps
from utils import gyro_handler as gyro
from utils import ultrasonic_handler as us

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def root():
    return 'hello! this is index!@#$'


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print 'gyro:'
    gyro.get_gyro()
    print 'accel:'
    gyro.get_gyro()
    print 'temp:'
    gyro.get_temp()
    print 'azimut:'
    gyro.get_azimut()
    print 'gps:'
    gps.get_location()
    print 'ultra sonic:'
    print us.getDistance()


def init():
    us.init()


def mark_target():
    distance = us.getDistance()
    latitude = gps.lat
    longitude = gps.lon

    dx = distance * math.sin(gyro.get_azimut())
    dy = distance * math.cos(gyro.get_azimut())

    delta_longitude = dx / (111320 * math.cos(latitude))
    delta_latitude = dy / 110540

    final_longitude = longitude + delta_longitude
    final_latitude = latitude + delta_latitude

    print 'final_longitude '+final_longitude
    print 'final_latitude' + final_latitude


def print_data():
    while 1:
        main()
        print '*\t*\t*\t*\t*\t*\t*\t'
        mark_target()
        sleep(1)


if __name__ == '__main__':
    try:
        gps = my_gps.my_gps()
        print 'start init'
        init()
        threading.Thread(target=print_data, args=()).start()
        print 'starting api'
        app.run(host=conf.HOST, port=conf.PORT)
    except:
        print traceback.format_exc()
