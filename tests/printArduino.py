import time, serial
import numpy as np


Arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)


while 1:
    val = Arduino.readline()[:-2].decode()
    print(val)
    time.sleep(0.02)