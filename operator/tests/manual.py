import serial
import struct
import math
from dualsense_controller import DualSenseController

UNKNOWN = 0;
MOTOR_COMMAND = 1;
ARM_COMMAND = 2;
INTAKE_COMMAND = 3;
ACTUATOR_COMMAND = 4;
ARM_BUTTON_COMMAND = 5;

class RobotControl():

    def __init__(self):
        device_infos = DualSenseController.enumerate_devices()
        if len(device_infos) == 0:
            print("No DualSense controller found.")
            return
        self.controller = DualSenseController()
        self.controller.btn_cross.on_down(self.send_intake_command_off)
        self.controller.btn_triangle.on_down(self.send_intake_command_on)
        self.controller.btn_circle.on_down(self.send_actuator_command)
        self.controller.activate()

        self.pico = serial.Serial('/dev/ttyUSB0', 115200)
    
    def send_right_trigger_motor_command(self):
        right_motor_speed = float(self.controller.right_trigger._get_value())
        left_motor_speed = float(self.controller.right_trigger._get_value())
        packet = MOTOR_COMMAND.to_bytes(1, "little")
        packet += bytearray(struct.pack( "<f", right_motor_speed))
        packet += bytearray(struct.pack( "<f", left_motor_speed))
        self.pico.write(packet)
    
    def send_left_trigger_motor_command(self):
        right_motor_speed = float(-self.controller.left_trigger._get_value())
        left_motor_speed = float(-self.controller.left_trigger._get_value())
        packet = MOTOR_COMMAND.to_bytes(1, "little")
        packet += bytearray(struct.pack( "<f", right_motor_speed))
        packet += bytearray(struct.pack( "<f", left_motor_speed))
        self.pico.write(packet)
    
    def send_stick_motor_command(self):
        right_motor_speed = float(self.controller.left_stick_x._get_value())
        left_motor_speed = float(-self.controller.left_stick_y._get_value())
        packet = MOTOR_COMMAND.to_bytes(1, "little")
        packet += bytearray(struct.pack( "<f", right_motor_speed))
        packet += bytearray(struct.pack( "<f", left_motor_speed))
        self.pico.write(packet)

    def send_arm_command(self):
        back_servo = float(self.controller.right_stick_x._get_value())
        front_servo = float(self.controller.right_stick_y._get_value())
        packet = ARM_COMMAND.to_bytes(1, "little")
        packet += bytearray(struct.pack( "<f", back_servo))
        packet += bytearray(struct.pack( "<f", front_servo))
        self.pico.write(packet)
    
    def send_intake_command_off(self):
        speed = 0.0
        packet = INTAKE_COMMAND.to_bytes(1, "little")
        packet += bytearray(struct.pack( "<f", speed))
        self.pico.write(packet)
    
    def send_intake_command_on(self):
        speed = 1.0
        packet = INTAKE_COMMAND.to_bytes(1, "little")
        packet += bytearray(struct.pack( "<f", speed))
        self.pico.write(packet)

    def send_actuator_command(self):
        id = 1
        packet = ACTUATOR_COMMAND.to_bytes(1, "little")
        packet += bytearray(struct.pack( "<f", id))
        self.pico.write(packet)

    def run(self):

        left_trig = 0.0
        right_trig = 0.0
        left_stick = 0.0

        while True:

            left_trig = self.send_left_trigger_motor_command()
            right_trig = self.send_right_trigger_motor_command()
            left_stick = self.send_stick_motor_command()

            if left_trig == 0 and right_trig == 0 and left_stick == 0:
                right_motor_speed = 0.0
                left_motor_speed = 0.0
                packet = MOTOR_COMMAND.to_bytes(1, "little")
                packet += bytearray(struct.pack( "<f", right_motor_speed))
                packet += bytearray(struct.pack( "<f", left_motor_speed))
                self.pico.write(packet)

            left_trig = 0.0
            right_trig = 0.0
            left_stick = 0.0

            self.send_arm_command()

        controller.deactivate()


if __name__ == "__main__":
    
    robot_control = RobotControl()
    robot_control.run()