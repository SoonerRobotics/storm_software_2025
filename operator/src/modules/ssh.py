from PyQt6.QtCore import QThread, pyqtSignal
import paramiko
import modules.helpers as helpers

class SSHTerminal(QThread):
    log_update = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.name = 'SSH Thread'
        self.host = helpers.HOST
        self.username = helpers.USERNAME
        self.password = helpers.PASSWORD
        self.command =  'cd /home/scr/storm_software_2025/robot/'
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.new_command = False
        self.running = True
    
    def run(self):
        self.log_update.emit(helpers.log(f'Thread initialized. Listening on port 22.', self.name))
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, look_for_keys=False)
            self.log_update.emit(helpers.log(f'Connected to {self.host}.', self.name))
            stdin, stdout, stderr = self.ssh.exec_command(self.command)
            while self.running:
                output = stdout.readline()
                if output:
                    self.log_update.emit(helpers.log(output.strip(), self.name))
                error = stderr.readline()
                if error:
                    self.log_update.emit(helpers.log(error.strip(), self.name))
                if stdout.channel.exit_status_ready() and not stdout.channel.recv_ready():
                    if self.new_command:
                        self.new_command = False
                        stdin, stdout, stderr = self.ssh.exec_command(self.command)
            self.ssh.close()
        except Exception as e:
            error_message = e.args[0] if e.args else str(e)
            self.log_update.emit(helpers.log(f"{error_message}", self.name))

    def send_command(self):
        command = self.main_window.command_input.text()
        self.main_window.command_input.clear()

        if command:
            self.command = command
            self.new_command = True