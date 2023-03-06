import numpy as np
from ThorlabsPM100 import ThorlabsPM100
import pyvisa as visa
import math

class PM100D:
    def __init__(self,Detector):
        self.rm = visa.ResourceManager()
        self.pivisa_device = self.rm.open_resource(Detector, timeout=3) 
        self.D = ThorlabsPM100(inst=self.pivisa_device)

        max_sense = self.D.sense.power.dc.range.maximum_upper 
        min_sense = self.D.sense.power.dc.range.minimum_upper
        n_sense = math.floor(math.log(max_sense/min_sense,10)) + 1
        self.Sense = np.zeros(n_sense+1)
        self.Sense[0] = np.format_float_scientific(max_sense, unique=False, precision=3)
        self.Sense[-1] = 0

        for i in range(0,n_sense-1):
            self.Sense[i+1] = np.format_float_scientific(self.Sense[i]/10,precision=3)

    
    def beep(self):
        self.D.system.beeper.immediate()
        
    def set_auto_range(self):   
        self.D.sense.power.dc.range.auto = "ON"
        
    def set_manual_range(self,range):
        #self.D.sense.power.dc.range.auto = "OFF"
        self.D.sense.power.dc.range.upper = range

    def set_bandwidth(self,BW=""):
        if BW == "Hi":
            self.D.input.pdiode.filter.lpass.state = 0
        elif BW =="Lo":
            self.D.input.pdiode.filter.lpass.state = 1
        else:
            print("BW not specified")

    def set_ave_count(self,averages):
        self.D.sense.average.count = int(averages)


    def disconnect(self):
        self.pivisa_device.close()


T = PM100D('USB0::0x1313::0x8078::P0016482::INSTR')

import time
for val in T.Sense:
    print(val)
    T.set_manual_range(val)
    time.sleep(1)

