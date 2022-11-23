from threading import current_thread
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from PySide2 import QtWidgets
from scipy import signal


class WdgPlot(QtWidgets.QWidget):
    def __init__(self,parent=None):
        """
        Initialise plotting variables, i've got a colours variable there too with the matplotlib
        default colours in order to alternate colours as more scans are collected.
        """

        super(WdgPlot, self).__init__(parent)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=False)

        self.win = pg.GraphicsLayoutWidget(show=True)
        self.win.setWindowTitle('pyqtgraph example: Scrolling Plots')

        self.win.nextRow()
        self.p1 = self.win.addPlot()
        self.p1.showGrid(x=True, y=True)
        
        self.p1.enableAutoRange('x', False)
        self.p1.enableAutoRange('y', True)
        
        
        self.colours = [
             u'#1f77b4',
             u'#ff7f0e', 
             u'#2ca02c', 
             u'#d62728', 
             u'#9467bd', 
             u'#8c564b', 
             u'#e377c2', 
             u'#7f7f7f', 
             u'#bcbd22', 
             u'#17becf'
             ]
        
        # Use automatic downsampling and clipping to reduce the drawing load
        #self.p1.setDownsampling(mode='peak')
        self.p1.setClipToView(True)

        self.curveNUM = 0
        self.curveDict = {}
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.win)

    def addCurve(self,lims):
        """
        I'm storing curves in a dictionary, this function adds a new curve and increments 
        curveNUM by +1, this means the previous curve is retained on screen. 
        """
        self.curveNUM += 1
        
        self.curveDict["curve_" + str(self.curveNUM)] = self.p1.plot(
                                                                    pen=pg.mkPen(color=self.colours[self.curveNUM % 9], 
                                                                    width=3
                                                                    )
                                                                    )
        self.p1.setXRange(lims[0],lims[1])

    def removeALL(self):
        """
        Clears figure, connected to the clear plot button.
        """
        self.p1.clear()
        self.curveDict = {}
        self.curveNUM = 0 

    def update(self,WL,PWR):
        """
        figure update function, updates the plot from the given WL and PWR arrays.
        """

        #resample data down to max of 10k datapoints for pyqt optimisation
        current_dpts = len(WL[:])
        
        
        if current_dpts > 10000:
            dpts = 10000
            wl = np.linspace(min(WL[:]),max(WL[:]),dpts)
            pwr = signal.resample(PWR[:],dpts)
        else:
            wl = WL[:]
            pwr = PWR[:]
            
        
        
        data = np.transpose(np.array([wl,pwr]))
        
        
        self.curveDict["curve_"+str(self.curveNUM)].setData(data)
