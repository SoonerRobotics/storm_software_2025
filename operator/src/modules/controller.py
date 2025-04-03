import socket
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from dualsense_controller import DualSenseController
from google.protobuf.message import Message
import modules.helpers as helpers
import modules.messages_pb2 as messages_pb2

class Controller(QThread):

    controller_update = pyqtSignal(str)
    log_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.name = 'Controller Thread'
        device_infos = DualSenseController.enumerate_devices()
        if len(device_infos) < 1:
            self.log_update.emit(helpers.log('No DualSense Controller available.', self.name))
        self.controller = DualSenseController()
        self.controller.btn_cross.on_down(self.send_intake_command_off)
        self.controller.btn_square.on_down(self.send_intake_command_slow)
        self.controller.btn_triangle.on_down(self.send_intake_command_fast)
        self.controller.btn_circle.on_down(self.send_actuator_command)
        self.controller.activate()
        self.log_update.emit(helpers.log('Controller connected.', self.name))
        self.running = True

    def send_right_trigger_motor_command(self):
        message = messages_pb2.Wrapper()
        message.type = messages_pb2.MOTOR_COMMAND
        motor_command = message.motor_command
        motor_command.right_motor_speed = self.controller.right_trigger._get_value()
        motor_command.left_motor_speed = self.controller.right_trigger._get_value()
        serialized = message.SerializeToString()
        if self.controller.right_trigger._get_value() > helpers.CONTROLLER_DEADZONE:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
                    return 1
            except Exception as e:
                self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))
        else:
            return 0

    def send_left_trigger_motor_command(self):
        message = messages_pb2.Wrapper()
        message.type = messages_pb2.MOTOR_COMMAND
        motor_command = message.motor_command
        motor_command.right_motor_speed = -self.controller.left_trigger._get_value()
        motor_command.left_motor_speed = -self.controller.left_trigger._get_value()
        serialized = message.SerializeToString()
        if self.controller.left_trigger._get_value() > helpers.CONTROLLER_DEADZONE:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
                    return 1
            except Exception as e:
                self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))
        else:
            return 0
    
    def send_stick_motor_command(self):
        message = messages_pb2.Wrapper()
        message.type = messages_pb2.MOTOR_COMMAND
        motor_command = message.motor_command
        motor_command.right_motor_speed = self.controller.left_stick_x._get_value()
        motor_command.left_motor_speed = -self.controller.left_stick_x._get_value()
        serialized = message.SerializeToString()
        if abs(self.controller.left_stick_x._get_value()) > helpers.CONTROLLER_DEADZONE:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
                    return 1
            except Exception as e:
                self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))
        else:
            return 0
    
    def send_arm_command(self):
        message = messages_pb2.Wrapper()
        message.type = messages_pb2.ARM_COMMAND
        arm_command = message.arm_command
        arm_command.x_dir = self.controller.right_stick_x._get_value()
        arm_command.y_dir = self.controller.right_stick_y._get_value()
        if abs(self.controller.right_stick_x._get_value()) > abs(self.controller.right_stick_y._get_value()):
            arm_command.y_dir = 0.0
        else:
            arm_command.x_dir = 0.0
        serialized = message.SerializeToString()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
        except Exception as e:
            self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))

    def send_intake_command_off(self):
        message = messages_pb2.Wrapper()
        message.type = messages_pb2.INTAKE_COMMAND
        intake_command = message.intake_command
        intake_command.speed = 0.0
        serialized = message.SerializeToString()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
        except Exception as e:
            self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))

    def send_intake_command_slow(self):
        message = messages_pb2.Wrapper()
        message.type = messages_pb2.INTAKE_COMMAND
        intake_command = message.intake_command
        intake_command.speed = 0.5
        serialized = message.SerializeToString()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
        except Exception as e:
            self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))

    def send_intake_command_fast(self):
        message = messages_pb2.Wrapper()
        message.type = messages_pb2.INTAKE_COMMAND
        intake_command = message.intake_command
        intake_command.speed = 1.0
        serialized = message.SerializeToString()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
        except Exception as e:
            self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))

    def send_actuator_command(self):
        message = messages_pb2.Wrapper()
        message.type = messages_pb2.ACTUATOR_COMMAND
        actuator_command = message.actuator_command
        actuator_command.id = 1
        serialized = message.SerializeToString()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
        except Exception as e:
            self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))

    def on_error(self, error):
        self.log_update.emit(helpers.log(f'Error: {error}', self.name))
        stop()

    def controller_state(self):

        if not self.controller:
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

                'Cross': self.controller.btn_cross._get_value(),
                'Square': self.controller.btn_square._get_value(),
                'Triangle': self.controller.btn_triangle._get_value(),
                'Circle': self.controller.btn_circle._get_value(),
                
            }

            sticks = {

                'Left': (self.controller.left_stick_x._get_value(), self.controller.left_stick_y._get_value()),
                'Right': (self.controller.right_stick_x._get_value(), self.controller.right_stick_y._get_value()),

            }

            dpad = {

                'Up': self.controller.btn_up._get_value(),
                'Down': self.controller.btn_down._get_value(),
                'Left': self.controller.btn_left._get_value(),
                'Right': self.controller.btn_right._get_value(),

            }

            triggers = {
                
                'Left': self.controller.left_trigger._get_value(),
                'Right': self.controller.right_trigger._get_value()

            }

            misc = {

                'Left Bumper': self.controller.btn_l1._get_value(),
                'Right Bumper': self.controller.btn_r1._get_value(),
                'Options': self.controller.btn_options._get_value(),
                'Create': self.controller.btn_create._get_value(),

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
        
        self.log_update.emit(helpers.log(f'Thread initialized. Sending on port {helpers.CONTROLLER_PORT}.', self.name))

        left_trig = 0
        right_trig = 0
        left_stick = 0

        while self.running:

            left_trig = self.send_left_trigger_motor_command()
            right_trig = self.send_right_trigger_motor_command()
            left_stick = self.send_stick_motor_command()

            if left_trig == 0 and right_trig == 0 and left_stick == 0:
                try:
                    message = messages_pb2.Wrapper()
                    message.type = messages_pb2.MOTOR_COMMAND
                    motor_command = message.motor_command
                    motor_command.right_motor_speed = 0.0
                    motor_command.left_motor_speed = 0.0
                    serialized = message.SerializeToString()
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        sock.sendto(serialized, (helpers.HOST, helpers.CONTROLLER_PORT))
                except Exception as e:
                    self.log_update.emit(helpers.log(f'Error sending data: {e}', self.name))
            
            left_trig = 0
            right_trig = 0
            left_stick = 0

            self.send_arm_command()

            self.controller_state()

        controller.deactivate()

    def stop(self):
        self.running = False