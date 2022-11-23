import serial
import numpy as np
import time
import DAQMXclass as DQ
import matplotlib.pyplot as plt

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name,)
        self.dt = (time.time() - self.tstart)
        print('Elapsed: %s' % self.dt)


samplingFreq = int(100000)
samples = int(20/0.001)

with Timer("Timer"):

    ai = DQ.AIVoltageChan(ai_param=DQ.AIParameters(samplingFreq, samples, ['/dev1/ai1']), 
                terminalConfig="DAQmx_Val_Diff", 
                #trigger=RisingTrigger('/dev1/PFI0')
                )

    with serial.Serial('COM4', 9800, timeout=1) as ser:
        inFscan = 0 
        inRscan = 0
        for i in range(0,1000):
            line = ser.readline()
            #print(line)
            decoded = line.decode().split(",")
            
            if decoded[0] == "1" and inFscan == 0:
                print("Forward Scan  T: " + str(time.time()))
                ai.start()
                ai.wait()
                data = ai.read()
                print(type(data))
                print(np.shape(data[:,0]))
                ai.stop()
                
               
                
                inFscan = 1
            if decoded[0] == "0" and inFscan == 1:
                inFscan = 0
                
            if decoded[1] == "1" and inRscan == 0:
                print("Reverse Scan  T: "+ str(time.time()))
                ai.start()
                ai.wait()
                plt.plot(ai.read())
                ai.stop()
                plt.show()
                inRscan = 1
            if decoded[1] == "0" and inRscan == 1:
                inRscan = 0
                    

