import pigpio
import time
import pubsub
from pubsub import get_topic
from node import Node


pwm = None

class Motors(Node):
    def __init__(self):
        global pwm
        self.servo = 13
        self.drive_pin = 12 
        self.steer_center = 1450
        self.drive_center = 1500
        self.steer_amount = 310
        self.drive_amount = 200
        self.wait_time = 7
        if pwm is None:
            pwm = pigpio.pi()
        pwm.set_mode(self.servo, pigpio.OUTPUT)
        pwm.set_mode(self.drive_pin, pigpio.OUTPUT) 

    def start(self):
        # Arm ESC and set steering to center
        pwm.set_servo_pulsewidth(self.drive_pin, self.drive_center)
        pwm.set_servo_pulsewidth(self.servo, self.steer_center)
        
        # For fun rumble 
        rumble = get_topic("controller/rumble")
        if rumble:
            rumble(self.wait_time)
        time.sleep(self.wait_time)

    def update(self): 
        steer = get_topic('motors/steer')
        drive = get_topic('motors/drive')
        pwm.set_servo_pulsewidth(self.drive_pin, self.drive_center + self.drive_amount * drive)
        pwm.set_servo_pulsewidth(self.servo, self.steer_center + self.steer_amount * steer)

    def stop(self):
        pwm.set_servo_pulsewidth(self.servo, self.steer_center)
        pwm.set_servo_pulsewidth(self.drive_pin, self.drive_center)
    
