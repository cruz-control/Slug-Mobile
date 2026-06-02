# LSM9DS1 9-DOF
# https://learn.adafruit.com/adafruit-lsm9ds1-accelerometer-plus-gyro-plus-magnetometer-9-dof-breakout/python-circuitpython
# Using Sensor.py base class

import time
import board
import busio
import adafruit_lsm9ds1
from node import Node

class IMU(Node):
    def __init__(self):
        # Initialize I2C + IMU
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_lsm9ds1.LSM9DS1_I2C(self.i2c)

    def start(self):
        self.set_topic("imu/accel", (0, 0, 0))
        self.set_topic("imu/gyro", (0, 0, 0))
        self.set_topic("imu/mag", (0, 0, 0))
        self.set_topic("imu/temp", 0)
        self.set_topic("imu/timestamp", -1)

    def update(self):

        # Reads IMU data and publishes it to topics.
        accel_x, accel_y, accel_z = self.sensor.acceleration
        accel = (accel_x, accel_y, accel_z) # (x, y, z) m/s^2
        gyro_x, gyro_y, gyro_z = self.sensor.gyro
        gyro = (gyro_x, gyro_y, gyro_z)              # (x, y, z) rad/s
        mag_x, mag_y, mag_z = self.sensor.magnetic
        mag = (mag_x, mag_y, mag_z)            # (x, y, z) gauss
        temp = self.sensor.temperature        # °C
        timestamp = time.time()

        # Publish individual topics
        self.set_topic("imu/accel", tuple(accel))
        self.set_topic("imu/gyro", tuple(gyro))
        self.set_topic("imu/mag", tuple(mag))
        self.set_topic("imu/temp", temp)
        self.set_topic("imu/timestamp", timestamp)
