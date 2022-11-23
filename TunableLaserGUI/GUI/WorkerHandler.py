from PySide2 import QtCore
from copyreg import pickle
import numpy as np
import time
import multiprocessing
#import pandas as pd
import csv
import pickle
import pandas as pd
import os
from datetime import date

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
        
        
class Handler:
    """
    Manager spawened as a thread asie the main pyside gui thread, 
    this allows for a thread to be controlling data collection while 
    the gui elements remain responsive. 

    """
    def __init__(self,myPlt,main):#,mainAPP,myPlt):
        if __name__ == "WorkerHandler":
            import ScanningControl as SC
            
            #initialise all variables.
            self.abort = False
            #self.main = mainAPP
            self.ScanningControl = SC.Scanning()
            self.plt   = myPlt
            self.main  = main
            
            
            manager = multiprocessing.Manager()

            #use the lock whenever changine any of the below variables.
            
            self.lock      = multiprocessing.Lock()
                       
            self.WL  = None
            self.PWR =  None

            self.Variables = manager.dict()
            self.Variables['ScanMode'] = 'Continous'
            self.Variables['ScanCount'] = 0
            self.Variables['Complete'] = False
            self.Variables['Pause']    = False
            self.Variables['Current_WL'] = 0.0
            self.Variables['abort'] = False
            self.Variables['filename'] = 'Default'
            self.Variables['user'] = 'Default'
            self.Variables['debug'] = False
            self.Variables['Power'] = 1
            self.Variables['Step'] = 1
            self.Variables['Ndata'] = None
            self.Variables['Cal'] = np.array([0.0316575511,-0.0000126141123])
            self.Variables['WLoffset'] = 0.0
            self.Variables['CalMode'] = False
        else:
            print("WH nope")
    
    
    def update(self):
        """
        Update function called by the pyside2 timer function, this checks the stop
        conditions and updates the pyqtgraph. 
        """

        if self.Variables['Complete'] == True:
            self.main.finished_scan()
            self.ScanControl.join()
            self.main.reset_vars()
        elif self.Variables['abort'] == True:
            self.main.finished_scan()
            self.ScanControl.join()
            self.main.reset_vars()
        else:
            #with Timer("Plot Update"):
            with self.lock:
                #APPLY WL OFFSET
                self.plt.update(self.WL,self.PWR)
                
    
    def mainWatch(self):
        """
        Start the child process that collects data, passing it into the multiprocessing shared variables
        """

        #self.info("mainWatch")
        #Inisitialse Child Processes
        self.ScanControl = multiprocessing.Process(target=self.ScanningControl.startScan, 
                                                args=(self.Variables,self.WL,self.PWR,)
                                                )
        #Start Child Processes
        self.ScanControl.start()
        
        


    def tempSave(self):
        """
        Every time a new curve is made, the previous one is saved as a .pkl file in 
        the temp directory, ready to be compiled into one csv at the end.
        """

        
        tosave = {
            "Variables":dict(self.Variables),
            "Wl":np.array(self.WL[:]),
            "PWR":np.array(self.PWR[:])
        }

        with open("../temp/curve_" + str(self.plt.curveNUM) + ".pkl", 'wb') as file:
            pickle.dump(tosave,file)

        print("Saved Temp Data")


    def savedata(self):
        """
        This function should compile all the temporary pickled curves into one csv.
        """

        self.main.read_inputs()

        if self.Variables['filename'] == '':
            filename = "Default"
        else:
            filename = self.Variables['filename']

        if self.Variables['user'] == '':
            user = 'Default'
        else:
            user = self.Variables['user']
 
        workingDir = '../data/' + user + '/' + str(date.today()) + '/'
        file = workingDir + filename + ".csv" # diffirentiate from other packages
		
        try:
            os.makedirs(workingDir)
        except:
            print('AlreadyDir')


        data = pd.DataFrame([])
        for k,v in self.plt.curveDict.items():
            with open("../temp/"+str(k)+".pkl", 'rb') as pickle_file:
                
                dataDict = pickle.load(pickle_file)
                      
                Vars = (list(dataDict['Variables'].items()))
                WL   = (dataDict['Wl'])
                PWR  = (dataDict['PWR'])

                print(str(k)+ ": " + str(len(WL)))
                
                if k == "curve_1":
                    data = pd.DataFrame(
                        np.row_stack(
                            [Vars,np.column_stack([WL, PWR])]),
                        dtype=object
                        )
                else:
                    dtemp = pd.DataFrame(
                        np.row_stack(
                            [Vars,np.column_stack([WL, PWR])]),
                        dtype=object
                        )
                    data = pd.concat([data, dtemp], axis=1)
                    #data = data.merge(dtemp,how='left', left_on='Column1', right_on='ColumnA')


        print(data)
            

        try:    
            data.to_csv(file) 
            print("Saved Successfully")
            self.main.status_handler("Saved")
        except:
            print("Save Unsuccesful")  
            self.main.status_handler("Save Unsuccesful")
