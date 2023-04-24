import cv2
import math

class DistanceToCamera(object):
    def __init__(self):
        # Params obtained from camera calibration
        self.alpha = 8.0 * math.pi / 180
        self.v0 = 119.865631
        self.ay = 332.262498

    def calculate(self, v, h, x_shift, image):
        """Calculates the distance to an object through a geometry model using monocular vision"""
        d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))

        if d > 0:
            cv2.putText(image, f"{d:.1f}cm", (image.shape[1] - x_shift, image.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return d