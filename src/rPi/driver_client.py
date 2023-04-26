import io
import time
import picamera
import struct
import socket
import socketserver
import threading
import RPi.GPIO as GPIO

import sys
from path import Path

coreDir = Path(__file__).parent.parent
sys.path.append(coreDir.abspath())

from core.utils import *
from car_control import CarControl

GPIO_TRIGGER = 23
GPIO_ECHO = 24

def measure():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    start = time.time()

    while GPIO.input(GPIO_ECHO) == 0:
        start = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        stop = time.time()

    elapsed = stop - start
    distance = (elapsed * 34300) / 2

    return distance


def measure_average():
    distance1 = measure()
    time.sleep(0.1)

    distance2 = measure()
    time.sleep(0.1)

    distance3 = measure()
    distance = (distance1 + distance2 + distance3) / 3
    return distance

class ThreadServer:
    car_control = CarControl()

    def stream_video(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Starting connection')

        client_socket.connect(video_stream_address)

        print('Connected to server')

        connection = client_socket.makefile('wb')

        try:
            camera = picamera.PiCamera()
            camera.resolution = (320, 240)
            camera.framerate = 15
            time.sleep(2)

            start = time.time()
            stream = io.BytesIO()

            for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                connection.write(struct.pack('<L', stream.tell()))
                connection.flush()
                stream.seek(0)

                connection.write(stream.read())

                stream.seek(0)
                stream.truncate()
            connection.write(struct.pack('<L', 0))
        finally:
            print('Closing the connection...')
            connection.close()
            client_socket.close()
            print('Connection closed')

    def stream_sensor_data(self):
        sock = socket.socket()
        sock.connect(sensor_data_stream_address)
        print("Connected to the server! Starting to measure the distance...")

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(GPIO_ECHO, GPIO.IN)

        GPIO.output(GPIO_TRIGGER, False)
        time.sleep(0.5)

        try:
            while True:
                distance = measure_average()
                print("Distance: {0:.1f}".format(distance))
                sock.send(str(distance).encode())
                time.sleep(0.5)
        finally:
            sock.close()
            GPIO.cleanup()

    @classmethod
    def serve(cls):
        sensor_thread = threading.Thread(target=cls.stream_sensor_data, args=[cls])
        sensor_thread.start()
        
        video_thread = threading.Thread(target=cls.stream_video, args=[cls])
        video_thread.start()

        control_thread = threading.Thread(target=cls.car_control.process_control_input)
        control_thread.start()




if __name__ == '__main__':
    ThreadServer().serve()
