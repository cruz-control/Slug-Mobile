# LSM9DS1 9-DOF
# https://learn.adafruit.com/adafruit-lsm9ds1-accelerometer-plus-gyro-plus-magnetometer-9-dof-breakout/python-circuitpython
# Using Sensor.py base class

import time
import board
import busio
import adafruit_lsm9ds1
from node import Node

class IMUSensor(Node):
    def __init__(self):
        # Initialize I2C + IMU
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_lsm9ds1.LSM9DS1_I2C(self.i2c)

    def update(self):

        # Reads IMU data and publishes it to topics.
        accel = self.sensor.acceleration      # (x, y, z) m/s^2
        gyro = self.sensor.gyro               # (x, y, z) rad/s
        mag = self.sensor.magnetic            # (x, y, z) gauss
        temp = self.sensor.temperature        # °C
        timestamp = time.time()

        # Publish individual topics
        self.set_topic("imu/accel", accel)
        self.set_topic("imu/gyro", gyro)
        self.set_topic("imu/mag", mag)
        self.set_topic("imu/temp", temp)
        self.set_topic("imu/timestamp", timestamp)


