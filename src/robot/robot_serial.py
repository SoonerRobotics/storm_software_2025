from rtcbot.arduino import SerialConnection
import asyncio
import serial
import sys
import glob

class RobotSerial:

    def __init__(self):
        
        self.operator_sendQueue = []
        self.operator_receiveQueue = []
        self.selected_port = None
        self.ports = self.serial_ports()

        self.port_amount = len(self.ports)
        if self.port_amount > 0:
            self.selected_port = self.ports[0]

        self.conn = SerialConnection(self.selected_port)
    
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
    
    async def sendAndReceive(self):
        while True:
            if self.operator_receiveQueue:
                self.conn.put_nowait(self.operator_receiveQueue.pop(0))
            msg = await self.conn.get()
            self.operator_sendQueue.append(msg)
    
    def begin(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
        