import pigpio # For PWM
import time
import pubsub

''' 
Design Doc/Notes


'''

pwm = pigpio.pi()

class Motor():
    def __init__(self):
        self.servo = 13
        self.drive_pin = 12 
        self.steer_center = 1450
        self.drive_center = 1500
        self.steer_amount = 310
        self.drive_amount = 200
        #self.wait_time = 7
        pwm.set_mode(self.servo, pigpio.OUTPUT)
        pwm.set_mode(self.drive_pin, pigpio.OUTPUT) 
        self.start = False

    def start(self):
        # time.sleep(self.wait_time)
        # print("Initialized")
        # # # For fun rumble 
        # # if get_topic("joystick"):
        # # if has_joystick:
        # #     self.joystick.rumble(0.1, 0.1, self.wait_time)
        self.start = True

    def clamp(x, a, b):
        return min(b, max(a, x))

    def update(self): 
        if (self.start = False):
            self.start = True
        # pygame.event.pump() # Waiting on controller.py
        x = self.joystick.get_axis(2) # May want to read 'controller_x' topic
        x *= abs(x)
        y = -self.joystick.get_axis(1) # May want to read 'controller_y' topic
        y *= abs(y)
        y2 = self.drive_center + self.drive_amount * y
        if y > 0:
            y2 += 15
        else:
            y2 -= 15
        y2 = clamp(y2, 1100, 1900) 
        pwm.set_servo_pulsewidth(self.drive_pin, y2)
        pwm.set_servo_pulsewidth(self.servo, self.steer_center + self.steer_amount * x)
        # Include wait time in main

    def stop(self):
        pwm.set_servo_pulsewidth(self.servo, self.steer_center)
        pwm.set_servo_pulsewidth(self.drive_pin, self.drive_center)
        self.start = False
    