import numpy as np
import pyvisa
import time

def connect():
        rm = pyvisa.ResourceManager()
        res = rm.list_resources()
     
        TLS = rm.open_resource(  [i for i in res if i.startswith('GPIB')][0] )
        return TLS

def TLS_reset():
    with connect() as TLS:
        TLS.write('*cls')
        print(TLS.query('*IDN?'))

def TLS_set_pwr(TLS,pwr):
    string = 'P=' + str(pwr)
    TLS.write(string)
    TLS.query('P?')
    #sleep(0.1)                     #And this delay
    return

def TLS_set_wl(TLS,wavelength):
    string = 'L=' + str(wavelength)
    #Set a WL
    TLS.write(string)
    #now query wavelength, this pauses the script until TLS get to WL
    TLS.query('L?') 
    return 

def TLS_set_speed(TLS,speed):
    string = 'MOTOR_SPEED=' + str(speed)
    TLS.write(string)
    TLS.query('MOTOR_SPEED?')
    return


#probably put this function in the scanning control file
def TLSscan(startWL,endWL,pwr,spd):
    with connect() as TLS:
        #set variables
        TLS_set_pwr(TLS,pwr)
        TLS_set_speed(TLS,spd)
        #Set wavelength to start
        TLS_set_wl(TLS,startWL)
        time.sleep(1)
        #Now set away DAQ
        TLS_set_wl(TLS,endWL)
        
TLSscan(1500,1600,1,50)