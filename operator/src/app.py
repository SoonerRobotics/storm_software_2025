import numpy as np
import time
import cv2
import sys
from art import text2art
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import QThread, pyqtSignal
from modules.controller import Controller
from modules.video import VideoReceiver
from modules.messages import RobotMessages

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