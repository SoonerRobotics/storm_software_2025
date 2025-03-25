import logging
import time

HOST = '127.0.0.1' # Robot's IP
VIDEO_PORT = 5000
CONTROLLER_PORT = 5001
MESSAGE_PORT = 5002
USERNAME = 'braden'
PASSWORD = '6242002'
DARK_THEME = """
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

def log_config():
    sys.path.insert(0, '/home/braden/storm_software_2025/') # Swap this with your own path.
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'operator.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def log(message, name):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    formatted = f'[{timestamp}] [{name}] - {message}\n'
    logging.info(f'[{name}] - {message}')
    return formatted