import pickle
import pandas as pd
import numpy as np
import h5py


for i in range(1,3):
    with open("../temp/curve_"+str(i)+".pkl", 'rb') as pickle_file:
        
        dataDict = pickle.load(pickle_file)
                      
        Vars = (list(dataDict['Variables'].items()))
        WL   = (dataDict['Wl'])
        PWR  = (dataDict['PWR'])
        
        with h5py.File("test.h5","w") as f:
            grp  = f.create_group("curve_"+str(i))
            #dset = grp.create_dataset("Vars",Vars)
            dset = grp.create_dataset("WL",WL,dtype='f')
            dset = grp.create_dataset("PWR",PWR,dtype='f')
        
with h5py.File("test.h5","r") as f:
    print(list(f.keys()))
        
