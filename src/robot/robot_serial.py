from rtcbot import MostRecentSubscription
import logging
import serial
import sys
import glob
import threading

class RobotSerial:

    log = logging.getLogger("storm.RobotSerial")

    def __init__(self):
        
        self.listen_thread = None
        self.write_thread = None
        self.operator_sendQueue = []
        self.operator_receiveQueue = []
        self.selected_port = None
        self.ports = self.serial_ports()

        self.port_amount = len(self.ports)
        if self.port_amount > 0:
            self.selected_port = self.ports[0]
        self.pico = serial.Serial(port=self.selected_port, baudrate=115200)

        super().__init__(MostRecentSubscription, self.log, loop=None)
    
    def serial_ports(self):
    
        ports = ["-----"]
        if sys.platform.startswith('win'):
            ports += ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports += glob.glob('/dev/tty[A-za-a]*')
        elif sys.platform.startswith('darwin'):
            ports += glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        
        return result
    
    def listenSerialThread(self):
        while(True):
            if self.pico.in_waiting() > 0:
                data = self.pico.readLine()
                self._put_nowait(data)


    def writeSerialThread(self):
        while (True):
            if self.operator_receiveQueue:
                data = self.operator_receiveQueue.pop(0)
                self.pico.write(data)

    
    def begin(self):

        listen_serial_thread = threading.Thread(target=self.listenSerialThread, daemon=True)
        write_serial_thread = threading.Thread(target=self.writeSerialThread, daemon=True)

        listen_serial_thread.start()
        write_serial_thread.start()

        listen_serial_thread.join()
        write_serial_thread.join()


robot = RobotSerial()
robot.begin()