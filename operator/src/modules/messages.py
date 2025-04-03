import socket
import numpy as np
import struct
from PyQt6.QtCore import QThread, pyqtSignal
import modules.helpers as helpers

class RobotMessages(QThread):
    
    robot_update = pyqtSignal(str)
    log_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('', helpers.MESSAGE_PORT))
        self.right_sonar = 0
        self.left_sonar = 0
        self.back_sonar = 0
        self.infrared = "None"
        self.name = 'Messages Thread'
        self.running = True

    def robot_state(self, conn):
        state = "Robot State: "
        if conn == 0:
            state += "Disconnected\n\n"
        else:
            state += "Connected\n\n"
        sensors = {
            'Right Sonar': f'{self.right_sonar} mm',
            'Left Sonar': f'{self.left_sonar} mm',
            'Back Sonar': f'{self.back_sonar} mm',
            'Infrared': self.infrared
        }
        for key, value in sensors.items():
            state += f'{key}: {value}\n'
        self.robot_update.emit(state)

    def run(self):
        self.log_update.emit(helpers.log(f'Thread initialized. Listening on port {helpers.MESSAGE_PORT}.', self.name))
        self.robot_state(0)
        while self.running:
            try:
                data, addr = self.client_socket.recvfrom(1024)
                message_type = data[0]
                if message_type == 1:
                    if len(data) >= 3:
                        sonar_id = chr(data[1])
                        if sonar_id == 'R':
                            self.right_sonar = data[2]
                        elif sonar_id == 'L':
                            self.left_sonar = data[2]
                        elif sonar_id == 'B':
                            self.back_sonar = data[2]
                elif message_type == 2:
                    if len(data) >= 3:
                        infrared = struct.unpack("!H", data[1:3])[0]
                self.log_update.emit(helpers.log(f'Received data from {addr}: {data}', self.name))
                self.robot_state(1)
            except Exception as e:
                self.log_update.emit(helpers.log(f'Error receiving data: {e}', self.name))
                self.robot_state(0)

    def stop(self):
        self.running = False