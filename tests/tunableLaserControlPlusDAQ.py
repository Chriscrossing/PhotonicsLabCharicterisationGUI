import numpy as np
import pyvisa
import time
import DAQMXclass as DQ
import matplotlib.pyplot as plt


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

def TLS_set_wl(TLS,wavelength,wait=True):
    string = 'L=' + str(wavelength)
    #Set a WL
    TLS.write(string)
    #now query wavelength, this pauses the script until TLS get to WL
    if wait:
        TLS.query('L?') 
        return
    else:
        return

def TLS_set_speed(TLS,speed):
    string = 'MOTOR_SPEED=' + str(speed)
    TLS.write(string)
    TLS.query('MOTOR_SPEED?')
    return


#probably put this function in the scanning control file
def TLSscan(startWL,endWL,pwr,spd):
    
    samplingFreq = 100000
    samples      = 100000
    
    ai = DQ.AIVoltageChan(ai_param=DQ.AIParameters(samplingFreq, samples, ['/dev1/ai0']), 
                terminalConfig="DAQmx_Val_Diff", 
                trigger=DQ.RisingTrigger('/dev1/PFI0')
                )
    
    with connect() as TLS:
        #set variables
        for i in range(2):
            TLS_set_pwr(TLS,pwr)
            TLS_set_speed(TLS,spd)
            #Set wavelength to start
            TLS_set_wl(TLS,startWL)
            
            #Now set away DAQ
            ai.start()
            
            TLS_set_wl(TLS,endWL,wait=False)
            ai.wait(timeout=int(samples/samplingFreq) + 4)
            data = np.array(ai.read()[:,0])
            ai.stop()
            
        
TLSscan(1500,1600,1,50)