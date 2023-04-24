class RCControl(object):
    def __init__(self):
        print("Initiating RC control...")
        # self.ser = find_arduino(serial_number=arduino_serial_number)

    def steer(self, prediction):
        if prediction == 0:
            # self.ser.write(b'6')
            print("Left")

        elif prediction == 1:
            # self.ser.write(b'5')
            print("Right")

        elif prediction == 2:
            # self.ser.write(b'1')
            print("Forward")

        else:
            self.stop()

    def stop(self):
        print("Stop")
        # self.ser.write(b'0')