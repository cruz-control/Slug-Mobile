# LSM9DS1 9-DOF
# https://learn.adafruit.com/adafruit-lsm9ds1-accelerometer-plus-gyro-plus-magnetometer-9-dof-breakout/python-circuitpython
# Using Sensor.py base class

import time
import board
import busio
import adafruit_lsm9ds1
from sensor import Sensor

class IMUSensor(Sensor):
    def __init__(self):
        # Initialize I2C and sensor
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_lsm9ds1.LSM9DS1_I2C(self.i2c)

        # Cache for latest frame
        self._frame = None

    def update(self):
        # Reads fresh data from the IMU and stores it internally.
        accel_x, accel_y, accel_z = self.sensor.acceleration
        gyro_x, gyro_y, gyro_z = self.sensor.gyro
        mag_x, mag_y, mag_z = self.sensor.magnetic
        temp = self.sensor.temperature

        self._frame = {
            "timestamp": time.time(),
            "acceleration": (accel_x, accel_y, accel_z),  # m/s^2
            "gyro": (gyro_x, gyro_y, gyro_z),             # rad/s
            "magnetometer": (mag_x, mag_y, mag_z),        # gauss
            "temperature": temp                           # °C
        }

    def get_frame(self):
        """
        Returns the most recent sensor frame.
        """
        if self._frame is None:
            raise RuntimeError("IMU frame not available. Call update() first.")
        return self._frame


