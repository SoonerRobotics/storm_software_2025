import cv2
import sys
import socket
import numpy as np
import logging
import pygame
import os
import time
from art import text2art
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import QThread, pyqtSignal

sys.path.insert(0, '/home/braden/storm_software_2025/') # Swap this with your own path.
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'operator.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

HOST = '127.0.0.1' # Robot's IP
VIDEO_PORT = 5000
MESSAGE_PORT = 5001

def log(message, name):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    formatted = f'[{timestamp}] [{name}] - {message}\n'
    logging.info(f'[{name}] - {message}')
    return formatted

class RobotMessages(QThread):
    robot_update = pyqtSignal(str)
    log_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind((HOST, MESSAGE_PORT))
        self.right_sonar = 0
        self.left_sonar = 0
        self.back_sonar = 0
        self.infrared = "None"
        self.name = 'RobotMessages Thread'
        self.running = True

    def robot_state(self, conn):
        state = "Robot State: "
        if conn == 0:
            state += "Disconnected\n\n"
        else:
            state += "Connected\n\n"
        sensors = {
            'Right Sonar': self.right_sonar,
            'Left Sonar': self.left_sonar,
            'Back Sonar': self.back_sonar,
            'Infrared': self.infrared
        }
        for key, value in sensors.items():
            state += f'{key}: {value}\n'
        self.robot_update.emit(state)

    def run(self):
        self.log_update.emit(log(f'Thread initialized. Listening on port {MESSAGE_PORT}.', self.name))
        self.robot_state(0)
        while self.running:
            try:
                data, addr = self.client_socket.recvfrom(1024)
                message = data.decode('utf-8')
                self.log_update.emit(log(f'Received data from {addr}: {data}', self.name))
                self.robot_state(1)
            except Exception as e:
                self.log_update.emit(log(f'Error receiving data: {e}', self.name))
                self.robot_state(0)

    def stop(self):
        self.running = False

class Controller(QThread):

    MOTOR_COMMAND = 0x01
    ARM_COMMAND = 0x02
    ACTUATOR_COMMAND = 0x03

    '''
        Format of State Updates

        'A Button: {boolean}'
        'B Button: {boolean}'
        'X Button: {boolean}'
        'Y Button: {boolean}'
        'Left Bumper: {boolean}'
        'Right Bumper: {boolean}'
        'Start Button: {boolean}'
        'Select Button: {boolean}'
        'Left Stick: {float}, {float}'
        'Right Stick: {float}, {float}'
        'DPad: {up, down, left, right}'
        'Left Trigger: {float}'
        'Right Trigger: {float}'
    '''
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
                'LB': 0,
                'RB': 0,
                'Start': 0,
                'Select': 0
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

        else:
            state = "Controller State: Connected\n"
            buttons = {
                'A': self.joystick.get_button(0),
                'B': self.joystick.get_button(1),
                'X': self.joystick.get_button(2),
                'Y': self.joystick.get_button(3),
                'LB': self.joystick.get_button(4),
                'RB': self.joystick.get_button(5),
                'Start': self.joystick.get_button(7),
                'Select': self.joystick.get_button(6)
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

        state += "\n"
        for button, value in buttons.items():
            state += f'{button} Button: {value}\n'
        for stick, value in sticks.items():
            state += f'{stick} Stick: {value[0]}, {value[1]}\n'
        for direction, value in dpad.items():
            state += f'{direction} DPad: {value}\n'
        for trigger, value in triggers.items():
            state += f'{trigger} Trigger: {value}\n'

        self.controller_update.emit(state)
    
    def run(self):
        
        self.log_update.emit(log(f'Controller thread initialized. Sending on port {MESSAGE_PORT}.', self.name))

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

class VideoReceiver(QThread):
    image_received = pyqtSignal(np.ndarray)
    log_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind((HOST, VIDEO_PORT))
        self.name = 'Video Thread'
        self.running = True

    def run(self):
        self.log_update.emit(log(f'Thread initialized. Receiving on {VIDEO_PORT}.', self.name))
        try:
            while self.running:
                size_data = self.client_socket.recv(4)
                if not size_data:
                    break
                size = int.from_bytes(size_data, byteorder='big')
                
                buffer = b""
                while len(buffer) < size:
                    buffer += self.client_socket.recv(size - len(buffer))
                frame = np.frombuffer(buffer, dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                if frame is not None:
                    self.image_received.emit(frame)
        except Exception as e:
            self.log_update.emit(log(f'Error receiving video: {e}', self.name))
            
    def stop(self):
        self.running = False
        self.client_socket.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.show()

        self.video = VideoReceiver()
        self.video.image_received.connect(self.update_frame)
        self.video.log_update.connect(self.update_log)

        self.robot = RobotMessages()
        self.robot.robot_update.connect(self.update_robot)
        self.robot.log_update.connect(self.update_log)

        self.controller = Controller()
        self.controller.controller_update.connect(self.update_controller)
        self.controller.log_update.connect(self.update_log)

        self.robot.start()
        self.video.start()
        self.controller.start()

    def init_ui(self):
        self.setWindowTitle('TBD Operator Interface')
        self.setGeometry(100, 100, 1920, 1080)

        main_layout = QHBoxLayout()

        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        left_panel.setContentsMargins(0, 0, 0, 0)

        controller_info_box = QGroupBox("Controller Info")
        controller_info_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controller_info_layout = QVBoxLayout()

        self.controller_state = QLabel()
        self.controller_state.setFont(QFont("Courier New", 13))
        self.controller_state.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        controller_info_layout.addWidget(self.controller_state)
        controller_info_box.setLayout(controller_info_layout)

        robot_info_box = QGroupBox("Robot Info")
        robot_info_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        robot_info_layout = QVBoxLayout()

        self.robot_state = QLabel()
        self.robot_state.setFont(QFont("Courier New", 13))
        self.robot_state.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        robot_info_layout.addWidget(self.robot_state)
        robot_info_box.setLayout(robot_info_layout)
        robot_info_box.setFixedHeight(200)

        self.scr_image = QLabel()
        self.scr_image.setFixedSize(275, 150)
        self.scr_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap("/home/braden/storm_software_2025/operator/assets/SCR_Gear_23_Wide_White_on_Transparent.png")
        self.scr_image.setPixmap(pixmap)
        self.scr_image.setScaledContents(True)

        self.storm_image = QLabel()
        self.storm_image.setFixedSize(203, 175)
        self.storm_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap("/home/braden/storm_software_2025/operator/assets/STORMLogo.png")
        self.storm_image.setPixmap(pixmap)
        self.storm_image.setScaledContents(True)

        left_panel.addWidget(controller_info_box, stretch=1)
        left_panel.addWidget(robot_info_box, stretch=1)
        left_panel.addWidget(self.scr_image, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.storm_image, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)

        right_panel = QVBoxLayout()

        self.video_panel = QLabel(self)
        self.video_panel.setFixedSize(1280, 720)
        
        blue_image = np.zeros((self.video_panel.height(), self.video_panel.width(), 3), dtype=np.uint8)
        blue_image[:] = (0, 0, 255)  # Fill with blue color
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "Offline"
        text_size = cv2.getTextSize(text, font, 2, 2)[0]
        text_x = (blue_image.shape[1] - text_size[0]) // 2
        text_y = (blue_image.shape[0] + text_size[1]) // 2
        cv2.putText(blue_image, text, (text_x, text_y), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        h, w, ch = blue_image.shape
        bytes_per_line = ch * w
        qImg = QImage(blue_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_panel.setPixmap(QPixmap.fromImage(qImg))

        right_panel.addStretch(1)
        right_panel.addWidget(self.video_panel, alignment=Qt.AlignmentFlag.AlignCenter)
        right_panel.addStretch(1)

        self.log_display = QTextEdit(self)
        self.log_display.setFont(QFont("Courier New", 8))
        self.log_display.setReadOnly(True)
        self.log_display.setPlainText(f"{text2art("T B D  O p e r a t o r  I n t e r f a c e")}\nDate: {QDate.currentDate().toString()}\nTime: {QTime.currentTime().toString()}\n")

        right_panel.addWidget(self.log_display)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 3)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qImg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_panel.setPixmap(QPixmap.fromImage(qImg))

    def update_robot(self, state):
        self.robot_state.setText(state)
    
    def update_controller(self, state):
        self.controller_state.setText(state)

    def update_log(self, log):
        self.log_display.append(log)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    dark_style = """
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QTextEdit, QLineEdit {
            background-color: #3c3f41;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QPushButton {
            background-color: #555555;
            border: 1px solid #888888;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #777777;
        }
        QPushButton:pressed {
            background-color: #999999;
        }
        QMenuBar, QMenu {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMenu::item:selected {
            background-color: #555555;
        }
    """
    app.setStyleSheet(dark_style)
    window = MainWindow()
    sys.exit(app.exec())