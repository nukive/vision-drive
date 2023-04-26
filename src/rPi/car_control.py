import socket

import sys
from path import Path

coreDir = Path(__file__).parent.parent
sys.path.append(coreDir.abspath())

from core.utils import *

class CarControl:
    def __init__(self) -> None:
        try:
            self.ser = find_arduino(serial_number=arduino_serial_number)
        except IOError as e:
            print(e)
            sys.exit()

        self.ser.flush()

    def process_control_input(self) -> None:
        control_socket = socket.socket()
        control_socket.connect(control_data_stream_address)
        
        try:
            while True:
                data = control_socket.recv(1024)
                print("Control ===>>> ", data)

                if (data == b'Left'):
                    self.ser.write(b'4')
                elif (data == b'Right'):
                    self.ser.write(b'3')
                elif (data == b'Forward'):
                    self.ser.write(b'1')
                else:
                    self.ser.write(b'0')
        finally:
            print('Exit')
            control_socket.close()
            self.ser.write(b'0')
            self.ser.close()