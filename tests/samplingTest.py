import numpy as np
import matplotlib.pyplot as plt
import time
import nidaqmx


def secs():
    return (time.time())





#freq = 100.00 # Hz
#T = (1/freq)

Datapoints = int(5)
data = np.zeros(Datapoints)

Tall = secs()


with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    data = task.stream_readers()
        

totalT = (secs()-Tall)

print(data)
print("Runtime:" + str(totalT))

#print(data['t_0'])