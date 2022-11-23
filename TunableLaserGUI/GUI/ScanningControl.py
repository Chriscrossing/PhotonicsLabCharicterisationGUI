from multiprocessing import Manager
import time, logging
import numpy as np
from ThorlabsPM100 import ThorlabsPM100
#import pickle, pyvisa
import DAQMXclass as DQ
import TunableLaserControl as TLC


class Scanning:

    def __init__(self):
        logging.info("Init TF")
        #share vars.k
        self.phase = 0 
       
        

    
    def startScan(self,manager,WL,PWR):
        """
        Starts Scanning, since we're focusing on continous scan then this 
        process is contained in a while loop, therefore should be ran in a seperate 
        thread.
        """

        self.Manager = manager
        self.WL = WL
        self.PWR = PWR
        
        if manager['abort'] == False:
            print("Scanning Starting")
            
            if self.Manager['ScanMode'] == "Continous":
                self.continous()
            elif self.Manager['ScanMode'] == "Stepping":
                self.stepping()
            else:
                print("Select a scanning mode")
            print("Scanning Complete")
        else:
            print("Abort Flag Active")


    def VoltTodBm(self,volt):
        """
        conversion from volts to dBm
        """        
        volt = abs(volt)
            
        volt = np.nan_to_num(volt)
            
        m = self.Manager['Cal'][0]
        c = self.Manager['Cal'][1]
        return (m*volt + c)*1e6 # outputs in micro-Watts




    def FakeContinous_Sweep(self):
        """
        This is for debugging, just plots a sin curve with 
        changing phase forever.
        """
        
        while self.Manager['abort'] != True:
            
            volt = np.sin(np.array(self.WL) + self.phase,dtype=np.double) + 1.0
    
            self.PWR[:] = volt#self.VoltTodBm(volt)
            self.phase = self.phase + 0.05
            time.sleep(1)          
                            
            inFscan = 1

        self.Manager['Complete'] = True


    def continous(self):
        """
        continous scan:
        this function continously scans the laser. The fastest method.
        
        HARDWARE TRIGGERED
        This is the continous function, it will trigger the NI-DAQ to collect data
        when we recieve an signal from the arduino telling us that the forward scan 
        has started. 

        We do have the ability to detect forward and reverse scans however this is not implimented. 
        Also will probably have to trigger the NI-DAQ directly using the arduino for maximum accuracy,
        but this will be difficult to figure out how to to forward and reverse scans. 
        """


        samplingFreq = self.Manager['SampFreq']
        samples = len(self.WL[:])
        
        #"""
        ai = DQ.AIVoltageChan(ai_param=DQ.AIParameters(samplingFreq, samples, ['/dev1/ai1']), 
                    terminalConfig="DAQmx_Val_Diff", 
                    trigger=DQ.RisingTrigger('/dev1/PFI0')
                    )
        
        tlc = TLC.TLC()
        
        with tlc.connect() as TLS:
            #tlc.set_pwr(TLS,self.Manager['Power'])
            tlc.set_speed(TLS,self.Manager['TLSspd'])
            
            while self.Manager['abort'] != True:
                try:
                    tlc.set_wl(TLS,self.WL[0])
            
                    #Now set away DAQ
                    ai.start()
                    
                    #and set away TLS scanning to end wl
                    tlc.set_wl(TLS,self.WL[-1],wait=False)
                    
                    ai.wait(timeout=int(samples/samplingFreq) + 4)
                    
                    #grab data from daq and convert to dBm
                    data = self.VoltTodBm(np.array(ai.read()[:,0]))
                    
                    ai.stop()
                    
                    #set data array for plotting
                    self.PWR[:] = data
                except:
                    print("Probably trigger timout")  
                    time.sleep(0.1)
                    ai.stop()   

                self.Manager['ScanCount'] += 1
                    

             

        self.Manager['Complete'] = True
        
    def stepping(self):
        """
        Stepping Sweep
        
        This function moves the laser to a wavelength, takes a reading, then steps forward
        """


        samplingFreq = self.Manager['SampFreq']
        samples = self.Manager['Averages']
        
        #"""
        ai = DQ.AIVoltageChan(ai_param=DQ.AIParameters(samplingFreq, samples, ['/dev1/ai1']), 
                    terminalConfig="DAQmx_Val_Diff", 
                    trigger=None
                    )
        
        tlc = TLC.TLC()
        
        with tlc.connect() as TLS:
            #tlc.set_pwr(TLS,self.Manager['Power'])
            tlc.set_speed(TLS,int(100))
            
            while self.Manager['abort'] != True:
                
                for i in range(len(self.WL[:])):

                    try:
                        if self.Manager['abort'] == True:
                            break
                        
                        
                        tlc.set_wl(TLS,self.WL[i])
                        
                
                        #Now set away DAQ
                        ai.start()
                        
                        ai.wait(timeout=int(samples/samplingFreq) + 1)
                        
                        #grab data from daq and convert to dBm
                        data = self.VoltTodBm(np.average(np.array(ai.read()[:,0])))
                        
                        ai.stop()
                        
                        #set data array for plotting
                        self.PWR[i] = data
                    except:
                        print("Probably trigger timout")  
                        time.sleep(0.1)
                        ai.stop()   
                self.Manager['ScanCount'] += 1

        self.Manager['Complete'] = True


    