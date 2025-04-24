from enum import Enum
import pygame
import csv
from datetime import datetime
import time

class XboxController:
    class Axis(int, Enum):
        LJOYX = 0
        LJOYY = 1
        RJOYX = 2
        RJOYY = 3
        RTRIGGER = 4
        LTRIGGER = 5
        A = 6
        B = 7
        X = 8

    def __init__(self, max_steering=80, max_throttle=20, logging_enabled=False):
        """Initialize the Xbox controller with optional logging."""
        # Initialize pygame and controller
        pygame.init()
        pygame.joystick.init()
        
        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            print(f"Detected controller: {self.controller.get_name()}")
        except pygame.error:
            raise RuntimeError("No controller found! Please connect an Xbox controller.")

        # Controller state
        self.triggers = [-1.0, -1.0]  # [left trigger, right trigger]
        self.joystick1 = [0, 0]      # [x axis, y axis] for left stick
        self.joystick2 = [0, 0]      # [x axis, y axis] for right stick
        self.dpad = [0, 0]           # [x axis, y axis]
        self.buttons = [0] * 15      # Array for button states

        # Control parameters
        self.max_steering = max_steering
        self.max_throttle = max_throttle

        # Logging setup
        self.logging_enabled = logging_enabled
        if logging_enabled:
            self._setup_logging()

    def _setup_logging(self):
        """Setup CSV logging for controller inputs."""
        filename = f"data/controller/controller_log_{int(time.time())}.csv"
        self.log_file = open(filename, 'w', newline='')
        self.csv_writer = csv.writer(self.log_file)
        self.csv_writer.writerow(['timestamp', 'steering', 'throttle', 
                                'left_trigger', 'right_trigger',
                                'left_stick_x', 'left_stick_y',
                                'right_stick_x', 'right_stick_y'])

    def update(self):
        """Update controller state from events."""
        pygame.event.pump()
        
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                self._handle_axis_event(event)
            elif event.type == pygame.JOYHATMOTION:
                self.dpad = [event.value[0], event.value[1]]
            elif event.type == pygame.JOYBUTTONUP:
                self.buttons[event.button] = 0
            elif event.type == pygame.JOYBUTTONDOWN:
                self.buttons[event.button] = 1

        if self.logging_enabled:
            self._log_state()

    def _handle_axis_event(self, event):
        """Handle joystick axis events."""
        if event.axis == self.Axis.LTRIGGER:
            self.triggers[0] = event.value + 1
        elif event.axis == self.Axis.RTRIGGER:
            self.triggers[1] = event.value + 1
        elif event.axis == self.Axis.LJOYX:
            self.joystick1[0] = event.value
        elif event.axis == self.Axis.LJOYY:
            self.joystick1[1] = event.value
        elif event.axis == self.Axis.RJOYX:
            self.joystick2[0] = event.value
        elif event.axis == self.Axis.RJOYY:
            self.joystick2[1] = event.value

    def get_steering(self):
        """Get the current steering value (-max_steering to +max_steering)."""
        return self.num_to_range(self.joystick1[0], -1, 1, 
                               -self.max_steering, self.max_steering)

    def get_throttle(self):
        """Get the current throttle value (-max_throttle to +max_throttle)."""
        left_throttle = self.num_to_range(self.triggers[0], 0, 2, 0, 0.2) if self.triggers[0] > 0 else 0
        right_throttle = self.num_to_range(self.triggers[1], 0, 2, 0, 0.2) if self.triggers[1] > 0 else 0
        throttle = left_throttle - right_throttle
        return throttle * self.max_throttle

    @staticmethod
    def num_to_range(num, inMin, inMax, outMin, outMax):
        """Scale a number from one range to another."""
        return round(outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin)), 3)

    def _log_state(self):
        """Log current controller state to CSV."""
        if not self.logging_enabled:
            return
            
        self.csv_writer.writerow([
            datetime.now().timestamp(),
            self.get_steering(),
            self.get_throttle(),
            self.triggers[0],
            self.triggers[1],
            self.joystick1[0],
            self.joystick1[1],
            self.joystick2[0],
            self.joystick2[1]
        ])
        self.log_file.flush()

    def close(self):
        """Clean up controller resources."""
        if self.logging_enabled:
            self.log_file.close()
        pygame.quit()

def test_button_mappings():
    controller = XboxController()
    print("Press each button on the controller to see its mapping...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            controller.update()
            for i, is_pressed in enumerate(controller.buttons):
                if is_pressed:
                    print(f"Button {i} was pressed")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting button test...")
    finally:
        controller.close()

# Test
if __name__ == "__main__":
    test_button_mappings()
    # try:
    #     controller = XboxController(logging_enabled=True)
    #     print("Controller test started. Press Ctrl+C to exit.")
        
    #     while True:
    #         controller.update()
    #         steering = controller.get_steering()
    #         throttle = controller.get_throttle()
    #         print(f"Steering: {steering:.2f}, Throttle: {throttle:.2f}")
    #         time.sleep(0.1)
            
    # except KeyboardInterrupt:
    #     print("\nExiting...")
    # finally:
    #     controller.close()