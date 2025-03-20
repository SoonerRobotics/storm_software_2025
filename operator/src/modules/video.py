import cv2
import sys
import socket
import numpy as np
import os
import time
from PyQt6.QtCore import QThread, pyqtSignal
from .helpers import log, log_config, HOST, VIDEO_PORT

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
        self.log_update.emit(log(f'Thread initialized. Listening on {VIDEO_PORT}.', self.name))
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