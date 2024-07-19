from enum import Enum
from time import sleep
from adafruit_servokit import ServoKit


class SlugMobile:

    def __init__(self, max_steering=80, max_throttle=20):
        """
        max_steering: max percentage of steering angle
        max_throttle: max percentage of thrust
        """
        self.max_steering = max_steering
        self.max_throttle = max_throttle

        self.steering_angle = 0
        self.throttle = 0

        self.servo_kit = ServoKit(address=0x60, channels=16)

