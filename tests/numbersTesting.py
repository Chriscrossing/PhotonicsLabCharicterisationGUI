import numpy as np


resolution = 0.01
startWL = 1540
endWL   = 1550
delta   = endWL - startWL

dpps = 200



dpts = delta/resolution

runtime = dpts/dpps 



step = delta/dpts

wavelengths = np.arange(
                        startWL,
                        endWL+step,
                        step
                        )

TLSspd = dpps*resolution
resolution = 0.01

print(TLSspd*resolution)