import math
import os
import socket
import traceback
from fpformat import fix
from multiprocessing import Process, Pipe
from time import sleep

from flask import Flask
from flask_cors import CORS

from utils import gps_handler as my_gps, conf
from utils import gyro_handler as gyro
from utils import ultrasonic_handler as us

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def root():
    return 'hello! this is index!@#$'


def run(api_connection):
    child_socket, father_socket = Pipe()
    Process(target=listen_to_socket, args=(child_socket,)).start()
    app.run(host="0.0.0.0", port=8082)

def listen_to_socket(father_connection):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('0.0.0.0', 8089))
    serversocket.listen(5)  # become a server socket, maximum 5 connections
    while True:
        connection, address = serversocket.accept()
        while True:
            msg = connection.recv(512)
            if len(msg) > 0:
                if msg == conf.MARK:
                    print msg
            break


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
    try:
        # distance = us.getDistance()
        distance = 1000
        latitude = gps.lat
        print 'lat'
        print latitude
        longitude = gps.lon
        print 'lon'
        print longitude
        # azimut = gyro.get_azimut()
        azimut = 270
        dx = distance * math.sin(azimut)
        dy = distance * math.cos(azimut)

        delta_longitude = dx / (111320 * math.cos(latitude))
        delta_latitude = dy / 110540

        final_longitude = fix(longitude + delta_longitude, 6)
        final_latitude = fix(latitude + delta_latitude, 6)
        print '%\t%\t%\t%\t%\t%\t'
        print 'final_longitude '
        print final_longitude
        print 'final_latitude'
        print final_latitude
        print '%\t%\t%\t%\t%\t%\t'
    except:
        print traceback.format_exc()


def print_data():
    while True:
        main()
        print '*\t*\t*\t*\t*\t*\t*\t'
        mark_target()
        sleep(0.1)


if __name__ == '__main__':
    try:
        print 'start init'
        gps = my_gps.my_gps()
        init()
        while True:
            main()
            print '*\t*\t*\t*\t*\t*\t*\t'
            mark_target()
            sleep(0.25)
            # threading.Thread(target=print_data, args=()).start()
            # print 'starting api'
            # app.run(host=conf.HOST, port=conf.PORT)
    except:
        print traceback.format_exc()
