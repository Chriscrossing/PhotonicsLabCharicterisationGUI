from ThorlabsPM100 import ThorlabsPM100, USBTMC
import time
import numpy as np
import time


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



inst = USBTMC()

print("printing usbtmc")
print(inst)

 



ThorMain = ThorlabsPM100(inst=inst)

ThorMain.sense.correction.wavelength = 1550
ThorMain.sense.average.count = 1

ndata = 200
data  = np.zeros(ndata)
error = np.zeros(ndata)

# 200 datapoints per second


with Timer("Timer"):

    for i in range(0,len(data)):
        try:
            data[i] = float(ThorMain.read)
        except:
            error[i] = 1


print("errors: " + str(error.sum()))
