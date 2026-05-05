import pigpio # For PWM
import time
import pubsub
from pubsub import get_topic

''' 
Design Doc/Notes


'''

pwm = pigpio.pi()

class Motors():
    def __init__(self):
        self.servo = 13
        self.drive_pin = 12 
        self.steer_center = 1450
        self.drive_center = 1500
        self.steer_amount = 310
        self.drive_amount = 200
        self.wait_time = 7
        pwm.set_mode(self.servo, pigpio.OUTPUT)
        pwm.set_mode(self.drive_pin, pigpio.OUTPUT) 

    def start(self):
        # For fun rumble 
        rumble = get_topic("controller/rumble")
        if rumble:
            rumble(self.wait_time)
        time.sleep(self.wait_time)

    def clamp(self, x, a, b):
        return min(b, max(a, x))

    def update(self): 
        x = get_topic('controller/right_x')
        x *= abs(x)
        y = -get_topic('controller/left_y')
        y *= abs(y)
        y2 = self.drive_center + self.drive_amount * y
        if y > 0:
            y2 += 15
        else:
            y2 -= 15
        y2 = self.clamp(y2, 1100, 1900) 
        pwm.set_servo_pulsewidth(self.drive_pin, y2)
        pwm.set_servo_pulsewidth(self.servo, self.steer_center + self.steer_amount * x)

    def stop(self):
        pwm.set_servo_pulsewidth(self.servo, self.steer_center)
        pwm.set_servo_pulsewidth(self.drive_pin, self.drive_center)
    
