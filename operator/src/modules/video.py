import cv2
import sys
import socket
import numpy as np
import os
import time
import pickle
from PyQt6.QtCore import QThread, pyqtSignal
import modules.helpers as helpers

class VideoReceiver(QThread):
    image_received = pyqtSignal(np.ndarray)
    log_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('', helpers.VIDEO_PORT))
        self.name = 'Video Thread'
        self.running = True

    def run(self):
        self.log_update.emit(helpers.log(f'Thread initialized. Listening on {helpers.VIDEO_PORT}.', self.name))
        try:
            while self.running:
                data, addr = self.client_socket.recvfrom(65536)
                frame_data = np.frombuffer(data, dtype=np.uint8)
                frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
                self.image_received.emit(frame)
        except Exception as e:
            self.log_update.emit(helpers.log(f'Error receiving video: {e}', self.name))
            
    def stop(self):
        self.running = False
        self.client_socket.close()