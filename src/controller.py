import pygame
from pygame._sdl2 import controller
import time
import csv
from node import Node
from pubsub import set_topic

class Controller(Node):
    axes = {
        "left_x": pygame.CONTROLLER_AXIS_LEFTX,
        "left_y": pygame.CONTROLLER_AXIS_LEFTY,
        "right_x": pygame.CONTROLLER_AXIS_RIGHTX,
        "right_y": pygame.CONTROLLER_AXIS_RIGHTY,
        "left_trigger": pygame.CONTROLLER_AXIS_TRIGGERLEFT,
        "right_trigger": pygame.CONTROLLER_AXIS_TRIGGERRIGHT
    }
    buttons = {
        "a": pygame.CONTROLLER_BUTTON_A,
        "b": pygame.CONTROLLER_BUTTON_B,
        "x": pygame.CONTROLLER_BUTTON_X,
        "y": pygame.CONTROLLER_BUTTON_Y,
        "back": pygame.CONTROLLER_BUTTON_BACK,
        "guide": pygame.CONTROLLER_BUTTON_GUIDE,
        "start": pygame.CONTROLLER_BUTTON_START,
        "left_stick_pressed": pygame.CONTROLLER_BUTTON_LEFTSTICK,
        "right_stick_pressed": pygame.CONTROLLER_BUTTON_RIGHTSTICK,
        "left_bumper": pygame.CONTROLLER_BUTTON_LEFTSHOULDER,
        "right_bumper": pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,
        "dpad_up": pygame.CONTROLLER_BUTTON_DPAD_UP,
        "dpad_down": pygame.CONTROLLER_BUTTON_DPAD_DOWN,
        "dpad_left": pygame.CONTROLLER_BUTTON_DPAD_LEFT,
        "dpad_right": pygame.CONTROLLER_BUTTON_DPAD_RIGHT
    }

    def rumble(self, time):
        self.connect_controller()
        if self.controller is not None:
            self.controller.rumble(0.1, 0.1, time * 1000)

    def __init__(self):
        super().__init__()
        self.controller = None
        set_topic('controller/rumble', self.rumble)

    def connect_controller(self):
        if controller.get_count() > 0 and self.controller is None:
            for i in range(controller.get_count()):
                if controller.is_controller(i):
                    self.controller = controller.Controller(i)
                    print(f'Joystick connected: {self.controller.get_name()}')
                    break
        elif controller.get_count() == 0 and self.controller is not None:
            print('Joystick disconnected')
            self.controller.quit()
            self.controller = None

    def start(self):
        # Initialize pygame and controller
        pygame.init()
        controller.init()
        self.connect_controller()
        if self.controller is None:
            print('No joystick connected at startup')
        
        for topic, axis in self.axes.items():
            set_topic(f'controller/{topic}', 0.0)
        for topic, button in self.buttons.items():
            set_topic(f'controller/{topic}', False)

    def stop(self):
        if self.controller is not None:
            self.controller.quit()
            self.controller = None
        pygame.quit()

    def update(self):
        pygame.event.pump()
        self.connect_controller()
        if self.controller is None:
            for topic, axis in self.axes.items():
                set_topic(f'controller/{topic}', 0.0)
            for topic, button in self.buttons.items():
                set_topic(f'controller/{topic}', False)
            return

        for topic, axis in self.axes.items():
            set_topic(f'controller/{topic}', self.controller.get_axis(axis) / 32768.0)
        for topic, button in self.buttons.items():
            set_topic(f'controller/{topic}', bool(self.controller.get_button(button)))
