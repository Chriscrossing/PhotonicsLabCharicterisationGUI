from pipython.pidevice.gcscommands import GCSCommands
from pipython.pidevice.gcsmessages import GCSMessages
from pipython.pidevice.interfaces.piserial import PISerial
import serial.tools.list_ports

import sys

  
class Stage:
    
    step = 0

    def move(self,distance):
        com = list(serial.tools.list_ports.comports())
        pidvid = (4104,6770)
        for i in com:
            if (i.pid,i.vid) == pidvid:
                comport = str(i.name)
        
        """Connect controller via first serial port with 115200 baud."""
        if sys.platform in ('linux', 'linux2', 'darwin'):
            port = '/dev/ttyUSB0' #for FTDI-USB connections
        else:
            port = comport
        with PISerial(port=port, baudrate=9600) as gateway:
            print('interface: {}'.format(gateway))
            messages = GCSMessages(gateway)
            pidevice = GCSCommands(messages)
            print('connected: {}'.format(pidevice.qIDN().strip()))
            pidevice.OSM(1,distance)
        print('moving',distance)

    def down(self):
        step = -1*self.step
        print("Moving down (Step = "+ str(step) + ")")
        self.move(step)

    def up(self):
        step = 1*self.step
        print("Moving up (Step = "+ str(step) + ")")
        self.move(step)