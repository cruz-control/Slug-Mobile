import cv2
import csv
import os
from datetime import datetime
from node import Node

class CSVLoggerNode(Node):
    def __init__(self, topic, filename):
        super().__init__()
        self.topic = topic
        self.filename = filename

        if not os.path.exists(filename):
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "value"])

    def update(self):
        value = self.get_topic(self.topic)
        if value is not None:
            with open(self.filename, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now().isoformat(), value])

class ImageLoggerNode(Node):
    def __init__(self, topic, folder="images"):
        super().__init__()
        self.topic = topic
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

    def update(self):
        frame = self.get_topic(self.topic)
        if frame is None:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(self.folder, f"{timestamp}.png")

        cv2.imwrite(filename, frame)

class VideoLoggerNode(Node):
    def __init__(self, topic, filename="output.avi", fps=30):
        super().__init__()
        self.topic = topic
        self.writer = None
        self.filename = filename
        self.fps = fps

    def update(self):
        frame = self.get_topic(self.topic)
        if frame is None:
            return

        if self.writer is None:
            h, w, _ = frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.writer = cv2.VideoWriter(self.filename, fourcc, self.fps, (w, h))

        self.writer.write(frame)

    def stop(self):
        if self.writer:
            self.writer.release()