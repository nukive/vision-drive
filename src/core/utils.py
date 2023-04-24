import serial
import serial.tools.list_ports

# Server
server_ip = '192.168.157.235'

server_address = (server_ip, 45710)
video_stream_address = (server_ip, 45720)
sensor_data_stream_address = (server_ip, 45730)

# Raspberry Pi
rpi_ip = "192.168.157.78"
rpi_port = 49220

rpi = (rpi_ip, rpi_port)

# Arduino
arduino_serial_number = '75830303934351011210' # is the serial number of my Arduino

def find_arduino(serial_number):
    for p in serial.tools.list_ports.comports():
        if p.serial_number == serial_number:
            return serial.Serial(p.device)

    raise IOError("Could not find the Arduino - is it plugged in ?!?")