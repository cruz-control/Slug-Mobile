from enum import Enum
from time import sleep
from adafruit_servokit import ServoKit
import cv2
from metavision_core.event_io import EventsIterator
from hokuyolx import HokuyoLX

class SlugMobile:

    def __init__(self, max_steering=80, max_throttle=20, i2c_address=0x60, channels=16):
        """
        max_steering: max percentage of steering angle
        max_throttle: max percentage of thrust
        """
        self.max_steering = max_steering
        self.max_throttle = max_throttle

        self.steering_angle = 0
        self.throttle = 0

        self.servo_kit = ServoKit(address=i2c_address, channels=channels)
        self.DrivingServo = self.servo_kit.servo[15]
        self.SteeringServo = self.servo_kit.servo[0]

        self.DrivingServo.angle = 90
        self.SteeringServo.angle = 90

        self.event_iterator = EventsIterator(input_path="", mode="n_events", n_events=1)

        self.lidar = HokuyoLX()

        sleep(5)

    def num_to_range(num, inMin, inMax, outMin, outMax):
        return round(
            outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin)), 3
        )

    def set_steering_angle(self, angle):
        self.SteeringServo.angle = angle

    def set_throttle(self, throttle):
        self.DrivingServo.angle = throttle

    def get_RGB(self):
        vid = cv2.VideoCapture(0)
        _, frame = vid.read()
        vid.release()
        return frame

    def get_event(self):
        event = next(self.event_iterator)
        return event.x, event.y, event.p, event.t
    
    def get_distance(self):
        timestamp, scan = self.lidar.get_dist()
        return timestamp, scan
