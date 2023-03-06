import pyvisa
import numpy as np
from ThorlabsPM100 import ThorlabsPM100


rm = pyvisa.ResourceManager()

pmT = rm.open_resource('USB0::0x1313::0x8078::P0016482::INSTR', timeout=10) 
pmR = rm.open_resource('USB0::0x1313::0x8078::P0036985::INSTR', timeout=10)

power_meters = {
            "T":ThorlabsPM100(inst=pmT),
            "R":ThorlabsPM100(inst=pmR)
            }


print("Transmission:")
print(power_meters["T"].read)

print("Reflection:")
print(power_meters["R"].read)
