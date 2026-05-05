import cv2
from pubsub import set_topic
from node import Node
import numpy as np

class RGB(Node):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def start(self):
        set_topic("rgb/frame", np.zeros((1080, 1920, 3), dtype=np.uint8))

    def update(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return

        set_topic('rgb/frame', frame)

    def stop(self):
        self.cap.release()
