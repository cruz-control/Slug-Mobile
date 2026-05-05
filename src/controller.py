import pygame
import time
import csv
from node import Node
from pubsub import set_topic

class Controller(Node):
    def rumble(self, time):
        self.connect_controller()
        if self.controller is not None:
            self.controller.rumble(0.1, 0.1, time)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.axes = ['left_x', 'left_y', 'right_x', 'right_y', 'left_trigger', 'right_trigger']
        self.buttons = ['a', 'b', 'x', 'y', 'left_bumper', 'right_bumper', 'back', 'start', 'left_stick_pressed', 'right_stick_pressed', 'guide']
        set_topic('controller/rumble', self.rumble)

    def connect_controller(self):
        if pygame.joystick.get_count() > 0 and self.controller is None:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            print(f'Joystick connected: {self.controller.get_name()}')
        elif pygame.joystick.get_count() == 0 and self.controller is not None:
            print('Joystick disconnected')
            self.controller = None

    def start(self):
        # Initialize pygame/controller here so the object manages its own sensor
        pygame.init()
        pygame.joystick.init()
        self.connect_controller()
        if self.controller is None:
            print('No joystick connected at startup')
        for a in self.axes:
            set_topic(f'controller/{a}', 0.0)
        for b in self.buttons:
            set_topic(f'controller/{b}', False)

    def stop(self):
        pygame.quit()

    def update(self):
        pygame.event.pump()
        self.connect_controller()
        if self.controller is None:
            return
        for i in range(len(self.axes)):
            set_topic(f'controller/{self.axes[i]}', self.controller.get_axis(i))
