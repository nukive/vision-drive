"""auto_driver.py: Multi-threaded server program that receives jpeg video frames, ultrasonic
sensor data and allows the RC car to drive itself with front collision avoidance."""

import cv2
import math
import numpy as np
import threading
import socketserver
import struct

import sys
from path import Path

coreDir = Path(__file__).parent.parent
sys.path.append(coreDir.abspath())

from core.utils import *
from neural_network import *
from object_detection import ObjectDetection
from distance_to_camera import DistanceToCamera
from rc_control import RCControl


# Ultrasonic sensor distance value
obstruction = threading.Event()

class VideoStreamHandler(socketserver.StreamRequestHandler):
    # Cascade Classifiers
    stop_classifier = cv2.CascadeClassifier(stop_cascade)
    light_classifier = cv2.CascadeClassifier(traffic_cascade)

    # Object detection instance
    obj_detection = ObjectDetection()

    # Distance to camera instance
    dist_to_camera = DistanceToCamera()
    h_stop = 14.5 - 10 # cm
    h_light = 14.5 - 10 # cm
    d_stop = 30.0
    d_light = 30.0

    # Create a neural network
    model = NeuralNetwork()

    car = RCControl()

    def handle(self):
        stop_sign_active = True
        stop_flag = False
        stop_start = 0
        stop_finish = 0
        stop_time = 0
        drive_time_after_stop = 0

        # read the video frames one by one
        try:
            while True:
                image_len = struct.unpack('<L', self.rfile.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break

                recv_bytes = b''
                recv_bytes += self.rfile.read(image_len)

                gray = cv2.imdecode(np.fromstring(recv_bytes, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                image = cv2.imdecode(np.fromstring(recv_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)

                # Get ROI
                roi = gray[120:240, :]

                # Reshape ROI
                image_array = roi.reshape(1, 38400).astype(np.float32)

                cv2.imshow('Video', image)

                # Object detection
                v_stop = self.obj_detection.detect(image, gray, self.stop_classifier)
                v_light = self.obj_detection.detect(image, gray, self.light_classifier)

                v_stop = 1 if v_stop is None else v_stop
                v_light = 1 if v_light is None else v_light

                if(v_stop is None or v_light is None): continue

                # Distance measurement
                if v_stop > 0 or v_light > 0:
                    d_stop = self.dist_to_camera.calculate(v_stop, self.h_stop, 300, image)
                    d_light = self.dist_to_camera.calculate(v_light, self.h_light, 100, image)
                    self.d_stop = d_stop
                    self.d_light = d_light

                # Neural Network makes the prediction
                prediction = self.model.predict(image_array)

                # Check for stop conditions
                if obstruction.is_set():
                    # Front collision avoidance
                    self.car.stop()
                    print("Stopping, obstacle in front!")

                elif 0.0 < self.d_stop < 30.0 and stop_sign_active:
                    print('Stop sign ahead. Stopping...')
                    self.car.stop()

                    # Stop for 5 seconds
                    if stop_flag is False:
                        stop_start = cv2.getTickCount()
                        stop_flag = True

                    stop_finish = cv2.getTickFrequency()
                    stop_time = stop_finish - stop_start
                    print(f"Stop time: {stop_time}")

                    # Waited 5 seconds, continue driving
                    if stop_time > 5:
                        stop_flag = False
                        stop_sign_active = False
                        print("Waited for 5 seconds")

                elif 0.0 < self.d_light < 30.0:
                    if self.obj_detection.red_light:
                        print("Red light")
                        self.car.stop()
                    elif self.obj_detection.green_light:
                        print("Green light")
                        pass
                        
                    self.obj_detection.red_light = False
                    self.obj_detection.green_light = False
                    self.d_light = 30.0

                else:
                    self.car.steer(prediction)
                    self.d_stop = 30.0
                    stop_start = cv2.getTickCount()

                    if stop_sign_active is False:
                        drive_time_after_stop = (stop_start - stop_finish) / cv2.getTickFrequency()
                        if drive_time_after_stop > 5:
                            stop_sign_active = True

                if (cv2.waitKey(5) & 0xFF) == ord('q'):
                    break

            cv2.destroyAllWindows()

        finally:
            self.car.stop()
            print("Connection closed on the server video thread!")


class SensorStreamHandler(socketserver.BaseRequestHandler):
    sensor_data = 0
    data = " "

    def handle(self):
        try:
            while self.data:
                self.data = self.request.recv(1024)
                self.sensor_data = round(float(self.data), 1)

                if self.sensor_data < 30:
                    obstruction.set()
                else:
                    obstruction.clear()

                print(f"Dist: {self.sensor_data}")
        finally:
            print("Connection closed on sensor server thread!")


class ThreadServer():
    def server_video_thread(host, port):
        server = socketserver.TCPServer((host, port), VideoStreamHandler)
        server.serve_forever()

    def ultrasonic_server_thread(host, port):
        server = socketserver.TCPServer((host, port), SensorStreamHandler)
        server.serve_forever()

    @classmethod
    def serve(cls):
        video_thread = threading.Thread(target=cls.server_video_thread, args=video_stream_address)
        video_thread.start()

        ultrasonic_sensor_thread = threading.Thread(target=cls.ultrasonic_server_thread, args=sensor_data_stream_address)
        ultrasonic_sensor_thread.start()

if __name__ == '__main__':
    ThreadServer().serve()