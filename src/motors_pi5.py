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

    def update(self): 
        # Get controller input
        steer = get_topic('motors/steer')
        drive = get_topic('motors/drive')

        self.drive_pwm.change_duty_cycle((self.drive_center + self.drive_amount * drive) / 20000 * 100)
        self.servo_pwn.change_duty_cycle((self.steer_center + self.steer_amount * steer) / 20000 * 100)

    def stop(self):
        self.drive_pwm.change_duty_cycle(self.drive_center / 20000 * 100)
        self.servo_pwn.change_duty_cycle(self.steer_center / 20000 * 100)
