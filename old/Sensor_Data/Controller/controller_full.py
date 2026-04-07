import pygame
import time
import csv

class ControllerInputLogger:
    def __init__(self, max_steering=80, max_throttle=20):
        self.max_steering = max_steering
        self.max_throttle = max_throttle
        self.steering_angle = 0
        self.throttle = 0

        # Open CSV file for recording controller data
        self.data_file = open("controller_data.csv", 'w', newline='')
        self.csv_writer = csv.writer(self.data_file)
        
        # Write the header row
        self.csv_writer.writerow(['timestamp', 'steering_angle', 'throttle'])

    def __del__(self):
        # Close the CSV file when the instance is deleted
        if self.data_file:
            self.data_file.close()

    def set_steering_angle(self, angle):
        """Sets and records the steering angle."""
        self.steering_angle = angle
        self.record_data()

    def set_throttle(self, throttle):
        """Sets and records the throttle."""
        self.throttle = throttle
        self.record_data()

    def record_data(self):
        """Records timestamp, steering angle, and throttle values to a CSV file."""
        timestamp = time.time()
        data = [timestamp, self.steering_angle, self.throttle]
        self.csv_writer.writerow(data)
        self.data_file.flush()  # Ensure data is written immediately

# Initialize Pygame and the controller
pygame.init()
pygame.joystick.init()

try:
    controller = pygame.joystick.Joystick(0)
    controller.init()
except pygame.error:
    print("No joystick found. Please connect a controller and try again.")
    pygame.quit()
    exit()

# Initialize Controller Logger
controller_logger = ControllerInputLogger()

print("Starting controller input logging. Press Ctrl+C to stop.")

try:
    while True:
        pygame.event.pump()  # Process events to update controller state

        # Read the controller input
        steering_value = controller.get_axis(0)    # Left thumbstick horizontal axis
        forward_value = controller.get_axis(5)     # Right trigger (forward throttle)
        reverse_value = controller.get_axis(4)     # Left trigger (reverse throttle)

        # Combine throttle values into a single throttle range (-1 to 1)
        throttle_value = (forward_value + 1) / 2 - (reverse_value + 1) / 2  # Ensure values are scaled correctly

        # Map and log the values
        controller_logger.set_steering_angle(steering_value * controller_logger.max_steering)
        controller_logger.set_throttle(throttle_value * controller_logger.max_throttle)

        # Print to console for real-time feedback (optional)
        print(f"Steering: {steering_value * controller_logger.max_steering}, Throttle: {throttle_value * controller_logger.max_throttle}")

        # Delay for a smoother output (adjust as needed)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Logging stopped by user.")
finally:
    pygame.quit()
