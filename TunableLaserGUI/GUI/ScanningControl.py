from multiprocessing import Manager
import time, logging
import numpy as np
from ThorlabsPM100 import ThorlabsPM100
#import pickle, pyvisa
import DAQMXclass as DQ
import TunableLaserControl as TLC
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

    def measure(self,samples):
        return np.array([self.D.read for _ in range(samples)])*1e6

    def disconnect(self):
        self.pivisa_device.close()

        


class Scanning:

    def __init__(self):
        logging.info("Init TF")
        #share vars.k
        self.phase = 0 

        self.T_Detector = 'USB0::0x1313::0x8078::P0016482::INSTR'
        self.R_Detector = 'USB0::0x1313::0x8078::P0036985::INSTR'


        

    
    def startScan(self,manager,WL,PWR,std):
        """
        Starts Scanning, since we're focusing on continous scan then this 
        process is contained in a while loop, therefore should be ran in a seperate 
        thread.
        """

        self.Manager = manager
        self.WL = WL
        self.PWR = PWR
        self.std = std
        
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

        #pmT = PM100D(self.T_Detector)

        #pmT.beep()
        #pmT.set_bandwidth(BW="Hi")



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
                #try:
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
                self.PWR["T"][:] = data

                #except:
                #    print("Probably trigger timout")  
                #    time.sleep(0.1)
                #    ai.stop()   

                self.Manager['ScanCount'] += 1
                    

             

        self.Manager['Complete'] = True
        
    
    
    
    def stepping(self):
        """
        Stepping Sweep
        
        This function moves the laser to a wavelength, takes a reading, then steps forward
        """


        samples = self.Manager['Averages']
        
        pmT = PM100D(self.T_Detector)
        pmR = PM100D(self.R_Detector)
        power_meters = {
            "T":pmT,
            "R":pmR
            }

        for pm in power_meters:
            power_meters[pm].beep()
            power_meters[pm].set_auto_range()
            power_meters[pm].set_bandwidth("Hi")
            power_meters[pm].set_ave_count(20)
            #power_meters[pm].sense.correction.wavelength = 1550

        tlc = TLC.TLC()

        while self.Manager['abort'] != True:
            with tlc.connect() as TLS:
                for i in range(len(self.WL[:])):

                    if self.Manager['abort'] == True:
                        break
                    
                    
                    tlc.set_wl(TLS,self.WL[i])
                    
                    #grab data from pm100d
                    Tmes = pmT.measure(samples)
                    Rmes = pmR.measure(samples)
                
                    
                    #set data array for plotting
                    self.PWR["T"][i] = np.mean(Tmes)
                    self.std["T"][i] = np.std(Tmes)
                    
                    self.PWR["R"][i] = np.mean(Rmes)
                    self.std["R"][i] = np.std(Rmes)
                    

                    #print(self.PWR["T"][0:5])
                    #print(self.std["T"][0:5])
                self.Manager['ScanCount'] += 1

                #only do one scan per button click
                self.Manager['abort'] = True
                for pm in power_meters:
                    power_meters[pm].system.beeper.immediate()

        self.Manager['Complete'] = True


    