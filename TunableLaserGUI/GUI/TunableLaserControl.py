from sqlite3 import connect
import numpy as np
import pyvisa


class TLC:
    
    def connect(self):
        rm = pyvisa.ResourceManager()
        res = rm.list_resources()
     
        TLS = rm.open_resource(  [i for i in res if i.startswith('GPIB')][0] )
        return TLS

    def reset(self):
        with self.connect() as TLS:
            TLS.write('*cls')
            print(TLS.query('*IDN?'))

    def set_pwr(self,TLS,pwr):
        string = 'P=' + str(pwr)
        TLS.write(string)
        TLS.query('P?')
        #sleep(0.1)                     #And this delay
        return

    def set_speed(self,TLS,speed):
        string = 'MOTOR_SPEED=' + str(speed)
        TLS.write(string)
        TLS.query('MOTOR_SPEED?')
        return 

    def set_wl(self,TLS,wavelength,wait=True):
        string = 'L=' + str(wavelength)
        #Set a WL
        TLS.write(string)
        #now query wavelength, this pauses the script until TLS get to WL
        if wait:
            TLS.query('L?') 
            return
        else:
            return

   