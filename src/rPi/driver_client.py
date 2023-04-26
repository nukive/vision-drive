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
from stream_sensor_data import measure_average

class CarControl(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        pass

class ThreadServer:
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

        GPIO_TRIGGER = 23
        GPIO_ECHO = 24

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
        video_thread = threading.Thread(target=cls.stream_video, args=[cls])
        video_thread.start()

        sensor_thread = threading.Thread(target=cls.stream_sensor_data, args=[cls])
        sensor_thread.start()




if __name__ == '__main__':
    ThreadServer().serve()
