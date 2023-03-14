from PySide2 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

import sys
import logging

import numpy as np
import threading, multiprocessing
import pickle
import pandas as pd
import os

#import PizoStageControl as Pizo

class APP(QtWidgets.QWidget):
    
    def __init__(self):
        
        import plotting as myPLT
        import WorkerHandler as myWH
        super(APP, self).__init__()

        
        #Initialise Modules  
        self.myPlt = myPLT.WdgPlot()

        self.timer = None
        
        self.Handler = myWH.Handler(self.myPlt,self)

        self.Stage = None #Pizo.Stage()

        #main Vars
        self.ThreadCount = False

        #self.go()
        
        #Initialise UI
        self.initUI()
        

    def inputField(self,label,function):
        label = QtWidgets.QLabel(label)
        label.setFixedWidth(150)
        textfield = QtWidgets.QLineEdit()
        textfield.setFixedWidth(150)
        textfield.returnPressed.connect(function)
        Obj = QtWidgets.QHBoxLayout()
        Obj.addWidget(label)
        Obj.addWidget(textfield)
        return Obj,textfield,label
        
        
    def initUI(self):
        
        #Define Button objects
        self.StartButton = QtWidgets.QHBoxLayout()
        self.startButton = QtWidgets.QPushButton("Start Scan / saveTemp")
        self.startButton.setFixedWidth(150)
        self.startButton.clicked.connect(self.start)
        self.StartButton.addWidget(self.startButton)
        

        self.ClearButton = QtWidgets.QHBoxLayout()
        self.clearbutton = QtWidgets.QPushButton("Clear Plot")
        self.clearbutton.setFixedWidth(150)
        self.clearbutton.clicked.connect(self.clearplt)
        
        self.ClearButton.addWidget(self.clearbutton)
        #self.ClearButton.addStretch()
        
        
        self.abortButton = QtWidgets.QPushButton("Stop/Abort")
        self.abortButton.setFixedWidth(100)
        self.abortButton.clicked.connect(self.abort)

        self.StartButton.addWidget(self.abortButton)

        self.saveData = QtWidgets.QPushButton("Save Data")
        self.saveData.clicked.connect(self.Handler.savedata)
        self.saveData.setFixedWidth(200)

        self.lastButton = QtWidgets.QHBoxLayout()
        self.lastButton.addWidget(self.saveData)
        
        saveDefaults = QtWidgets.QPushButton("Save Defaults")
        saveDefaults.setFixedWidth(150)
        reloadDefaults = QtWidgets.QPushButton("Reload Saved")
        reloadDefaults.setFixedWidth(150)

        self.Defaults = QtWidgets.QHBoxLayout()
        self.Defaults.addWidget(reloadDefaults)
        self.Defaults.addWidget(saveDefaults)

        self.RadioButtons = QtWidgets.QHBoxLayout()
        self.Continous = QtWidgets.QRadioButton("Continous")
        self.Stepping = QtWidgets.QRadioButton("Stepping")
        
        self.Continous.clicked.connect(self.switch_cont)
        self.Stepping.clicked.connect(self.switch_step)
        
        self.RadioButtons.addWidget(self.Continous)
        self.RadioButtons.addWidget(self.Stepping)

        #Define Input objects

        status = QtWidgets.QHBoxLayout()
        
        status.addWidget(QtWidgets.QLabel("Status: "))
        Status = QtWidgets.QLabel()
        Status.setFixedWidth(150)
        
        status.addWidget(Status)
        status.addStretch()

        self.Status = status,Status
        
                
        self.Filename = self.inputField("Filename:",None)
        self.User = self.inputField("User:",None)

        self.Start_WL = self.inputField("Start (nm):",None)
        self.End_WL = self.inputField("End (nm):",None)

        self.Step = self.inputField("Step (nm):",None)
        self.Power = self.inputField("Power (mW):",None)
        
        self.SampFreq = self.inputField("Sampling Freq(kHz):",None)
        self.TLSspd = self.inputField("Scan Speed (nm/s):",None)
        
        self.EffectiveRes = self.inputField("Effective Res (pm):",None)
        
        
        
        """
        Thorlabs Sensitivity Dropdown menu 
        """
        
        DropDownLab = QtWidgets.QLabel("PM Sensitivity:")
        DropDownLab.setFixedWidth(150)
        
        self.Dropdown1 = QtWidgets.QComboBox()
        self.Dropdown1.addItem("63mW")
        self.Dropdown1.addItem("6.3mW")
        self.Dropdown1.addItem("630uW")
        self.Dropdown1.addItem("63uW")
        self.Dropdown1.addItem("6.3uW")
        self.Dropdown1.addItem("630nW")
        self.Dropdown1.currentIndexChanged.connect(self.SetCalibration)
        
        self.Calinput =  QtWidgets.QHBoxLayout() 
        self.Calinput.addWidget(DropDownLab)
        self.Calinput.addWidget(self.Dropdown1)

        """
        Nanostepping stage controls
        """

        up = QtWidgets.QToolButton()
        up.setArrowType(QtCore.Qt.UpArrow)
        up.clicked.connect(self.PizoUp)
        QtWidgets.QShortcut(QtGui.QKeySequence("up"), up, self.PizoUp)

        down = QtWidgets.QToolButton()
        down.setArrowType(QtCore.Qt.DownArrow)
        down.clicked.connect(self.PizoDown)
        QtWidgets.QShortcut(QtGui.QKeySequence("down"), up, self.PizoDown)

        self.stepSize = self.inputField("Step Size (um)",None)
        
        self.stepSize[1].returnPressed.connect(self.PizoEnterPressed)

        arrows = QtWidgets.QHBoxLayout()
        arrows.addLayout(self.stepSize[0])
        arrows.addWidget(up)
        arrows.addWidget(down)

        self.Nanostep = QtWidgets.QVBoxLayout()
        self.Nanostep.addWidget(QtWidgets.QLabel("Nanostep Stage Control:"))
        self.Nanostep.addLayout(arrows)


           
        # Instructions label
        
        def newline(obj,text):
            label = QtWidgets.QLabel()
            label.setWordWrap(True)
            label.setText(text)
            obj.addWidget(label)
            
            
        self.Instructions = QtWidgets.QVBoxLayout()
        newline(self.Instructions,"Step 1: TLS defaults to 100nm/s scan speed, keep in mind the max data speed is 100kHz.")
        newline(self.Instructions,"Step 2: Set TLS away on a repeat scan, use dlam = 0 and dt = 0.2s")
        newline(self.Instructions,"Step 3: Input the same scan settings into this GUI and choose a resolution")
        
        #Organising Layout

        #box 1 buttons
        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addLayout(self.RadioButtons)
        vbox1.addLayout(self.Defaults)
        vbox1.addLayout(self.Calinput)
        vbox1.addLayout(self.Start_WL[0])
        vbox1.addLayout(self.End_WL[0])
        vbox1.addLayout(self.TLSspd[0])
        vbox1.addLayout(self.SampFreq[0])
        vbox1.addLayout(self.EffectiveRes[0])
        vbox1.addLayout(self.StartButton)
        vbox1.addLayout(self.ClearButton)
        vbox1.addLayout(self.Instructions)
        vbox1.addStretch()
        vbox1.addLayout(self.Nanostep)
        vbox1.addStretch()
        vbox1.addLayout(self.User[0])
        vbox1.addLayout(self.Filename[0])
        vbox1.addLayout(self.lastButton)
        #vbox1.addLayout(self.CalWL[0])


        #initialise Figure
        Figure = self.myPlt
        #Figure.setFixedWidth(1000)  # variable plz

        #combine all boxes
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(Figure)
        hbox1.addLayout(vbox1)

        
        MasterVbox = QtWidgets.QVBoxLayout()
        MasterVbox.addLayout(hbox1)
        MasterVbox.addLayout(self.Status[0])
        
        self.setLayout(MasterVbox)    
        
        self.setGeometry(200, 200, 1600, 900)
        self.setWindowTitle('TunableLaserGUI')    
        print("showing GUI")
        self.show()
        print("Done showing")

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message',
            "Are you sure?", QtWidgets.QMessageBox.Yes | 
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.abort()
            event.accept()
        else:
            event.ignore()        

    def reset_vars(self):
        self.ThreadCount = False
        self.Handler.Variables['abort'] = False
        self.Handler.Variables['Complete'] = False
        self.Handler.Variables['Pause'] = False
        
        if self.timer != None:
            self.timer.stop()
            self.statusTimer.stop()


        #self.PWMfreq.setText(str(self.LC.freq))
        #self.Duty.setText(str(self.LC.duty)

    def switch_cont(self):
        self.Handler.Variables['ScanMode'] = 'Continous'
        self.SampFreq[2].setText("Sampling Freq(kHz):")
        self.TLSspd[2].setText("Scan Speed (nm/s):")
        self.EffectiveRes[2].setText("Effective Res (pm):")

    def switch_step(self):
        self.Handler.Variables['ScanMode'] = 'Stepping'
        self.SampFreq[2].setText("Step size (pm):")
        self.TLSspd[2].setText("Samples per step:")
        self.EffectiveRes[2].setText("Scan Repeats:")
        
        
    def PizoEnterPressed(self):
        self.Stage.step = 0.06667*float(self.stepSize[1].text())
        print("set step to:", self.Stage.step)
        
    def PizoUp(self):
        print("moving up")
        self.Stage.up()
        #self.Handler.Variables['Single'] = True 
        #self.start()

    def PizoDown(self):
        print("moving down")
        self.Stage.down()
        #self.Handler.Variables['Single'] = True 
        #self.start()



    def read_inputs(self):
        
        if self.Handler.Variables['ScanMode'] == "Continous":
        

            self.Handler.Variables['filename']      = self.Filename[1].text()
            self.Handler.Variables['user']          = self.User[1].text()
            self.Handler.Variables['Start_WL']      = float(self.Start_WL[1].text())
            self.Handler.Variables['End_WL']        = float(self.End_WL[1].text())
            self.Handler.Variables['SampFreq']      = int(self.SampFreq[1].text())*1000 # convert to Hz
            self.Handler.Variables['TLSspd']        = float(self.TLSspd[1].text())
            #self.Handler.Variables['WLoffset']      = float(self.Offset[1].text())/1000
            
            print("Continous")
            sampFreq   = self.Handler.Variables['SampFreq']
            TLSspd     = self.Handler.Variables['TLSspd']
            startWL    = self.Handler.Variables['Start_WL']
            endWL      = self.Handler.Variables['End_WL']
            delta      = endWL - startWL

            dpts       = int(delta*(sampFreq/TLSspd))

            step = delta/dpts
            self.EffectiveRes[1].setText(str(step*1000))

            wavelengths = np.linspace(
                                    startWL,
                                    endWL,
                                    dpts
                                    )

            self.Handler.Variables['Ndata']   = len(wavelengths)

            # round to 3dp as TLS will freak out with more dp.
            #not needed here??
            #wavelengths = np.round(wavelengths,decimals=3)

            print(wavelengths)
            #Init multiprocessing arrays
            
            self.Handler.WL = multiprocessing.Array('f',wavelengths)
            self.Handler.PWR = {
                "T":multiprocessing.Array('f',np.zeros(self.Handler.Variables['Ndata'],dtype=float))
                }
            
        elif self.Handler.Variables['ScanMode'] == "Stepping":
            
            
            
            self.Handler.Variables['filename']      = self.Filename[1].text()
            self.Handler.Variables['user']          = self.User[1].text()
            self.Handler.Variables['Start_WL']      = float(self.Start_WL[1].text())
            self.Handler.Variables['End_WL']        = float(self.End_WL[1].text())
            self.Handler.Variables['Step']      = float(self.SampFreq[1].text())/1000 
            self.Handler.Variables['Averages']      = int(self.TLSspd[1].text())
            self.Handler.Variables['Repeats']       = int(self.EffectiveRes[1].text())


            wavelengths = np.arange(
                                self.Handler.Variables['Start_WL'],
                                self.Handler.Variables['End_WL']+self.Handler.Variables['Step'],
                                self.Handler.Variables['Step']
                                )

            self.Handler.Variables['Ndata']   = len(wavelengths)

            # round to 3dp as TLS will freak out with more dp.
            wavelengths = np.round(wavelengths,decimals=3)

            #print(wavelengths)
            #Init multiprocessing arrays
            
            self.Handler.WL = multiprocessing.Array('f',wavelengths)
            self.Handler.PWR = {} 
            self.Handler.std = {} 
            self.Handler.PWR["T"] = multiprocessing.Array('f',np.zeros(self.Handler.Variables['Ndata'],dtype=float))
            self.Handler.PWR["R"] = multiprocessing.Array('f',np.zeros(self.Handler.Variables['Ndata'],dtype=float)) 
            self.Handler.std["T"] = multiprocessing.Array('f',np.zeros(self.Handler.Variables['Ndata'],dtype=float))
            self.Handler.std["R"] = multiprocessing.Array('f',np.zeros(self.Handler.Variables['Ndata'],dtype=float))

        else:
            print("Scanmode not selected")



        

    def info(self,title):
        print(title)
        print('module name:', __name__)
        print('parent process:', os.getppid())
        print('process id:', os.getpid())


    def start(self):

        if self.ThreadCount == False:
            
            #reset variables and print to log 
            self.reset_vars()
            with self.Handler.lock:
                self.read_inputs()

            lims = [min(self.Handler.WL),max(self.Handler.WL)]
            # increase curve num per T and R
            self.myPlt.curveNUM += 1 
            # add some new curves with names based off transmission and reflection
            for item in self.Handler.PWR:
                self.myPlt.addCurve(lims,item)
            

            logging.info("Starting Loop")
            self.status_handler("Starting")

            #Make a csv (or add to an existing csv) and input starting values
            

            #Print to log and set threadcount to True (stop multiple runs)
            self.ThreadCount = True
            

            self.Handler.mainWatch()

            

            #Start GUI update timer
            self.timer = pg.QtCore.QTimer(self)
            self.timer.timeout.connect(self.Handler.update)
            self.timer.start(100)

            self.statusTimer = pg.QtCore.QTimer(self)
            self.statusTimer.timeout.connect(self.scanStatusUpdate)
            self.statusTimer.start(200)

            
            
            
        else:
            #if already running, instead just add a new curve, saving the old onn stored
            #in memory ready for saving to file
            
            #print("In Scan -> Else")
            self.abort()
            self.Handler.update()
            self.start()

    def SetCalibration(self):
        idx = self.Dropdown1.currentIndex()

        calArray = np.array([0.0316575511,-0.0000126141123,0.00314278794,0.000000937223181,0.000317032328,0.000000841507518,0.000031994015,-0.000000093578136,0.00000315652491,-2.07959957E-09,0.000000318418212,9.15660877E-09])
        
        self.Handler.Variables['Cal'] = calArray[2*idx:2*idx+2]
        print(self.Handler.Variables['Cal'])

    

    def WL_Status(self,WL):
        self.status_handler("WL: " + str(WL))

    def clearplt(self):
        self.myPlt.removeALL()
        self.status_handler("Data Cleared")

        
    def finished_scan(self):
        self.status_handler("Scan Complete")
        self.Handler.Variables['abort'] = True
        self.ThreadCount = False
        self.Handler.tempSave()

    def abort(self):
        try:
            self.Handler.tempSave()
        except:
            print("No Data to save")

        
        self.status_handler("Aborted")
        self.Handler.Variables['abort'] = True
        self.ThreadCount = False
        self.Handler.Variables['ScanCount'] = 0
        
    def scanStatusUpdate(self):
        self.status_handler(self.Handler.Variables['ScanCount'])
            


    def status_handler(self,value):
        #logging.info(str(value))
        self.Status[1].setText(str(value))


if __name__ ==  '__main__':
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    #logging.basicConfig(format='%(asctime)s %(message)s',filename='../Logs/Main.log',level=logging.INFO)


    app = QtWidgets.QApplication(sys.argv)
    ex = APP()
    sys.exit(app.exec_())