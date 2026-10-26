from rpi_hardware_pwm import HardwarePWM
import time
import pubsub
from pubsub import get_topic
from node import Node


class Motors(Node):
    def __init__(self):
        # Channel 2 == GPIO 18
        self.servo_pwn = HardwarePWM(pwm_channel=2, chip=0, hz=50)
        # Channel 3 == GPIO 19
        self.drive_pwm = HardwarePWM(pwm_channel=3, chip=0, hz=50)

        self.steer_center = 1450
        self.drive_center = 1500
        self.steer_amount = 310
        self.drive_amount = 200
        self.wait_time = 7

    def start(self):
        # Arm ESC and set steering to center
        self.drive_pwm.start(self.drive_center / 20000 * 100)
        self.servo_pwn.start(self.steer_center / 20000 * 100)
        
        # For fun rumble 
        rumble = get_topic("controller/rumble")
        if rumble:
            rumble(self.wait_time)
        time.sleep(self.wait_time)

    def clamp(self, x, a, b):
        return min(b, max(a, x))

    def update(self): 
        # Get controller input
        x = get_topic('controller/right_x')
        y = -get_topic('controller/left_y')

        # Use quadratic scaling for easier control at low speeds
        x *= abs(x)
        y *= abs(y)

        # Calculate pulse width and reduce dead zone
        y2 = self.drive_center + self.drive_amount * y
        if y > 0:
            y2 += 15
        else:
            y2 -= 15
        
        # Clamp y2 in the allowed range and set pulse widths
        y2 = self.clamp(y2, 1100, 1900) 
        self.drive_pwm.change_duty_cycle(y2 / 20000 * 100)
        self.servo_pwn.change_duty_cycle((self.steer_center + self.steer_amount * x) / 20000 * 100)

    def stop(self):
        self.drive_pwm.change_duty_cycle(self.drive_center / 20000 * 100)
        self.servo_pwn.change_duty_cycle(self.steer_center / 20000 * 100)
