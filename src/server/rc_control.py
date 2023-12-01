from queue import Queue

control_prediction = Queue()
prediction_default_stop = 4

class RCControl(object):
    def __init__(self):
        print("Initiating RC control...")
        # self.ser = find_arduino(serial_number=arduino_serial_number)

    def steer(self, prediction):
        if prediction == 0:
            # self.ser.write(b'6')
            control_prediction.put("Left")
            # print("Left")

        elif prediction == 1:
            # self.ser.write(b'5')
            control_prediction.put("Right")
            # print("Right")

        elif prediction == 2:
            # self.ser.write(b'1')
            control_prediction.put("Forward")
            # print("Forward")

        else:
            self.stop(prediction_default_stop)

    def stop(self, stop_index):
        control_prediction.put("Stop")
        print("Stop, index ===>>> ", stop_index)
        # self.ser.write(b'0')
