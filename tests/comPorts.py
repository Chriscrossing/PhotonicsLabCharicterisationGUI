import serial.tools.list_ports
com = list(serial.tools.list_ports.comports())


pidvid = (4104,6770)

for i in com:
    if (i.pid,i.vid) == pidvid:
        print(str(i.name))
    