import cv2

class ObjectDetection(object):
    def __init__(self):
        self.red_light = False
        self.green_light = False

    def detect(self, image, gray, classifier):
        v = 0
        threshold = 150

        # Detect the objects
        objects = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))

        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.rectangle(image, (x+5, y+5), (x+w-5, y+h-5), (255, 255, 255), 2)
            v = y + h - 5

            # print(f"width/height is: {w/h}")
            # Stop sign
            if w / h == 1:
                cv2.putText(image, 'STOP', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Traffic light
            else:
                roi = gray[y+10: y+h-10, x+10: x+w-10]

                mask = cv2.GaussianBlur(roi, (25,25), 0)
                (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)

                # Check to see if light is on
                if maxVal - minVal > threshold:
                    cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)

                    # Red light
                    if 1.0/8*(h - 30) < maxLoc[1] < 4.0/8*(h - 30):
                        cv2.putText(image, 'Red', (x+5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        self.red_light = True

                    # Green light
                    if 5.5/8*(h-30) < maxLoc[1] < h - 30:
                        cv2.putText(image, 'Red', (x + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        self.green_light = True

            return v