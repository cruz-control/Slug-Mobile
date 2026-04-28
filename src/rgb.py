import numpy as np
import cv2
import pubsub
from sensor import Sensor
from dataclasses import dataclass

class rgb(Sensor):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def update(self):
        ret, frame = self.cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # # Display the resulting frame
        # cv2.imshow('frame',frame)
        # cv2.imshow('gray',gray)

        pubsub.set_topic('rgb/gray', gray)

    def stop(self):
        # How to stop the camera in main
        # if cv2.waitKey(20) & 0xFF == ord('q'):
        #     break
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()