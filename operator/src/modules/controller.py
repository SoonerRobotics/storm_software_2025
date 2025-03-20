import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import sys
import socket
import numpy as np
import os
import time
from PyQt6.QtCore import QThread, pyqtSignal
from .helpers import log, log_config, HOST, MESSAGE_PORT

class Controller(QThread):

    MOTOR_COMMAND = 0x01
    ARM_COMMAND = 0x02
    ACTUATOR_COMMAND = 0x03

    controller_update = pyqtSignal(str)
    log_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.joystick.init()
        self.name = 'Controller Thread'
        self.joystick = None
        self.running = True

    def send(self, data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(data.encode(), (HOST, MESSAGE_PORT))
        except Exception as e:
            self.log_update.emit(log(f'Error sending data: {e}', self.name))

    def controller_state(self):
        if not self.joystick or not self.joystick.get_init():
            state = "Controller State: Disconnected\n"
            buttons = {
                'A': 0,
                'B': 0,
                'X': 0,
                'Y': 0,
            }

            sticks = {
                'Left': (0.0, 0.0),
                'Right': (0.0, 0.0)
            }

            dpad = {
                'Up': 0,
                'Down': 0,
                'Left': 0,
                'Right': 0
            }

            triggers = {
                'Left': 0.0,
                'Right': 0.0
            }

            misc = {
                'Left Bumper': 0,
                'Right Bumper': 0,
                'Start': 0,
                'Select': 0
            }

        else:
            state = "Controller State: Connected\n"
            buttons = {
                'A': self.joystick.get_button(0),
                'B': self.joystick.get_button(1),
                'X': self.joystick.get_button(2),
                'Y': self.joystick.get_button(3),
            }

            sticks = {
                'Left': (self.joystick.get_axis(0), self.joystick.get_axis(1)),
                'Right': (self.joystick.get_axis(2), self.joystick.get_axis(3))
            }

            dpad = {
                'Up': self.joystick.get_button(10),
                'Down': self.joystick.get_button(12),
                'Left': self.joystick.get_button(11),
                'Right': self.joystick.get_button(13)
            }

            triggers = {
                'Left': self.joystick.get_axis(4),
                'Right': self.joystick.get_axis(5)
            }

            misc = {
                'Left Bumper': self.joystick.get_button(4),
                'Right Bumper': self.joystick.get_button(5),
                'Start': self.joystick.get_button(7),
                'Select': self.joystick.get_button(6)
            }

        state += "\n"
        for button, value in buttons.items():
            state += f'{button} Button: {value}\n'
        for stick, value in sticks.items():
            state += f'{stick} Stick: {value[0]}, {value[1]}\n'
        for direction, value in dpad.items():
            state += f'{direction} DPad: {value}\n'
        for trigger, value in triggers.items():
            state += f'{trigger} Trigger: {value}\n'
        for key, value in misc.items():
            state += f'{key}: {value}\n'

        self.controller_update.emit(state)
    
    def run(self):
        
        self.log_update.emit(log(f'Thread initialized. Sending on port {MESSAGE_PORT}.', self.name))

        while pygame.joystick.get_count() == 0:
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.log_update.emit(log('Controller connected.', self.name))
                self.controller_state()
            else:
                self.log_update.emit(log('No controller detected. Retrying (5s)...', self.name))
                self.controller_state()
                QThread.sleep(5)

        if not self.joystick:
            return

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                else:
                    if event.axis == 1:
                        if (abs(controller.get_axis(0)) > 0.25):
                            right_motor = (-controller.get_axis(0) * 255) * TURN_PERCENTAGE
                            left_motor = (controller.get_axis(0) * 255) * TURN_PERCENTAGE
                            packet = MOTORS.to_bytes(1,'little')
                            packet = packet + bytearray(struct.pack("<f",right_motor)) + bytearray(struct.pack("<f",left_motor))
                            self.send(packet)
                        else:
                            packet = MOTORS.to_bytes(1, "little")
                            packet = packet + bytearray(struct.pack("<f",0.0)) + bytearray(struct.pack("<f", 0.0))
                            self.send(packet)
                    elif event.axis == 2:
                        right_y = (-controller.get_axis(3)) * 255
                        right_x = controller.get_axis(2) * 255
                        packet = ARM.to_bytes(1,'little')
                        packet = packet + bytearray(struct.pack("<f",right_x)) + bytearray(struct.pack("<f",right_y))
                        self.send(packet)
                    elif event.axis == 4:
                        left_trig = controller.get_axis(4)
                        left_trig = -((left_trig + 1) / 2)
                        right_motor = (left_trig * 255) * SPEED_PERCENTAGE
                        left_motor = (left_trig * 255) * SPEED_PERCENTAGE
                        packet = MOTORS.to_bytes(1,'little')
                        packet = packet + bytearray(struct.pack("<f",right_motor)) + bytearray(struct.pack("<f",left_motor))
                        self.send(packet)
                    elif event.axis == 5:
                        right_trig = controller.get_axis(5)
                        right_trig = (right_trig + 1) / 2
                        right_motor = (right_trig * 255) * SPEED_PERCENTAGE
                        left_motor = (right_trig * 255) * SPEED_PERCENTAGE
                        packet = MOTORS.to_bytes(1,"little")
                        packet = packet + bytearray(struct.pack("<f",right_motor)) + bytearray(struct.pack("<f",left_motor))
                        self.send(packet)

                    self.controller_state()
        
        pygame.quit()

    def stop(self):
        self.running = False