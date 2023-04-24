import cv2

# Global variables
mlp_model = 'src/server/mlp_xml/mlp_1670436357.xml'
stop_cascade = 'src/server/cascade_classifiers/stop_sign.xml'
traffic_cascade = 'src/server/cascade_classifiers/traffic_light.xml'

class NeuralNetwork():
    def __init__(self):
        self.model = cv2.ml.ANN_MLP_load(mlp_model)

    def predict(self, samples):
        ret, resp = self.model.predict(samples)
        return resp.argmax(-1)