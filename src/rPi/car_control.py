import socket
import time
from threading import Thread, Event

import sys
from path import Path

coreDir = Path(__file__).parent.parent
sys.path.append(coreDir.abspath())

from core.utils import *

pause_event = Event()

class CarControl:
    def __init__(self) -> None:
        pause_event.set()

        pause_thread = Thread(target=self.control_pause_event)
        pause_thread.start()

        try:
            self.ser = find_arduino(serial_number=arduino_serial_number)
        except IOError as e:
            print(e)
            sys.exit()

        self.ser.flush()

    def control_pause_event(self):
        while True:
            is_set = pause_event.is_set()
            # print("pause state ===>>> ", is_set)

            time.sleep(0.7)

            if(is_set):
                pause_event.clear()
            else:
                pause_event.set()

    def stop_car(self):
        self.ser.write(b'0')


    def process_control_input(self) -> None:
        control_socket = socket.socket()
        control_socket.connect(control_data_stream_address)
        
        try:
            while True:
                data = control_socket.recv(1024)
                print("Prediction received ===>>> ", data)

                if(pause_event.is_set()):
                    self.stop_car()
                    continue 
                
                if (data == b'Left'):
                    self.ser.write(b'4')
                elif (data == b'Right'):
                    self.ser.write(b'3')
                elif (data == b'Forward'):
                    self.ser.write(b'1')
                else:
                    self.stop_car()
        finally:
            print('Exit')
            control_socket.close()
            self.ser.write(b'0')
            self.ser.close()