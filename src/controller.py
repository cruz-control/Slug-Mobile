import pygame
import time
import csv
from sensor import Sensor


class ControllerInputLogger(Sensor):
    def __init__(self, max_steering=80, max_throttle=20):
        super().__init__()

        self.max_steering = max_steering
        self.max_throttle = max_throttle

        self.steering_angle = 0
        self.throttle = 0
        self.frame = None   # stores the most recent controller frame

        # Open CSV file for recording controller data
        self.data_file = open("controller_data.csv", "w", newline="")
        self.csv_writer = csv.writer(self.data_file)

        # Write the header row
        self.csv_writer.writerow([
            "timestamp",
            "raw_steering",
            "raw_forward",
            "raw_reverse",
            "steering_angle",
            "throttle"
        ])

        # Initialize pygame/controller here so the object manages its own sensor
        pygame.init()
        pygame.joystick.init()

        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
        except pygame.error:
            pygame.quit()
            raise RuntimeError("No joystick found. Please connect a controller and try again.")

    def __del__(self):
        if hasattr(self, "data_file") and self.data_file:
            self.data_file.close()
        pygame.quit()

    def record_data(self):
        """
        Records the current frame to CSV.
        """
        if self.frame is None:
            return

        self.csv_writer.writerow([
            self.frame["timestamp"],
            self.frame["raw_steering"],
            self.frame["raw_forward"],
            self.frame["raw_reverse"],
            self.frame["steering_angle"],
            self.frame["throttle"],
        ])
        self.data_file.flush()

    def update(self):
        """
        Read the current controller values and store them as the newest frame.
        """
        pygame.event.pump()

        # Read raw controller input
        steering_value = self.controller.get_axis(0)   # left stick horizontal
        forward_value = self.controller.get_axis(5)    # right trigger
        reverse_value = self.controller.get_axis(4)    # left trigger

        # Convert triggers into one throttle value in range [-1, 1]
        throttle_value = (forward_value + 1) / 2 - (reverse_value + 1) / 2

        # Scale to your car ranges
        self.steering_angle = steering_value * self.max_steering
        self.throttle = throttle_value * self.max_throttle

        # Save a full "frame" of controller state
        self.frame = {
            "timestamp": time.time(),
            "raw_steering": steering_value,
            "raw_forward": forward_value,
            "raw_reverse": reverse_value,
            "steering_angle": self.steering_angle,
            "throttle": self.throttle,
        }

        # Log one complete row
        self.record_data()

    def get_frame(self):
        """
        Returns the most recent controller frame.
        If no frame exists yet, update once first.
        """
        if self.frame is None:
            self.update()
        return self.frame