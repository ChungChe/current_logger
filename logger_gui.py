#from pyqtgraph.Qt import QtGui, QtCore
# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pyqtgraph as pg

import collections
from random import randint
import time
import math
import numpy as np
import sys

class lineEdit(QLineEdit):
    def __init__(self, parent = None):
        super(lineEdit, self).__init__(parent)
        self.setReadOnly(True)
        self.setFixedSize(100, 60)
class DynamicPlotter(QWidget):
    def __init__(self, sampleinterval = 0.1, timewindow = 10., size =(800,500), parent = None):
        super(DynamicPlotter, self).__init__(parent)
        self.dataCount = 1
        self.warnCount = 0
        self.lastWarnVal = 9999
        self.lastAvg = 7777
        # Data stuff
        self._interval = int(sampleinterval * 1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype = np.float)
        # PyQtGraph stuff
        #self.app = QApplication([])
        self.horizontalLayout = QHBoxLayout(self)
        self.win = pg.GraphicsWindow(title = "Current Viewer")
        self.horizontalLayout.addWidget(self.win)

        self.plt = self.win.addPlot(title = 'Current Viewer')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'Current', 'A')
        self.plt.setLabel('bottom', 'time', 's')
        self.curve = self.plt.plot(self.x, self.y, pen=(255,0,0))
        self.thres_curve = self.plt.plot(self.x, self.y, pen=(255,255,0))

        # QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self._interval)

        self.verticalLayout = QVBoxLayout(self)
        # Label
        current_label = QLabel(self)
        current_label.setText(u"目前電流：")
        self.verticalLayout.addWidget(current_label)
        self.currentEdit = lineEdit(self)
        self.verticalLayout.addWidget(self.currentEdit)
        
        warning_label = QLabel(self)
        warning_label.setText(u"低於警戒值次數：")
        self.verticalLayout.addWidget(warning_label) 
        self.warnEdit = lineEdit(self)
        self.verticalLayout.addWidget(self.warnEdit)
        
        avg_current = QLabel(self)
        avg_current.setText(u"平均電流：")
        self.verticalLayout.addWidget(avg_current)
        self.avgEdit = lineEdit(self)
        self.verticalLayout.addWidget(self.avgEdit)

        self.horizontalLayout.addLayout(self.verticalLayout)
    def get_data(self):
        #frequency = 0.5
        #noise = random.normalvariate(0., 1.)
        #new = 10.*math.sin(time.time()*frequency*2*math.pi) + noise
        
        return randint(0, 120)

    def update_plot(self):
        curr_val = self.get_data()
        self.databuffer.append(curr_val)
        print('curr_val: {}'.format(curr_val))
        self.currentEdit.setText(str(curr_val))

        if curr_val < 80 and self.lastWarnVal >= 80:
            self.warnCount += 1
        self.lastWarnVal = curr_val

        self.warnEdit.setText(str(self.warnCount))

        # incremental avg calculation
        # see:
        # https://ubuntuincident.wordpress.com/2012/04/25/calculating-the-average-incrementally/

        if self.lastAvg == 7777:
            self.lastAvg = curr_val
        currAvg = self.lastAvg + (curr_val - self.lastAvg) / float(self.dataCount)
        
        self.avgEdit.setText('{:3.2f}'.format(currAvg))
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)
        thres = np.empty(len(self.y))
        thres.fill(80)
        self.thres_curve.setData(self.x, thres)
        self.dataCount += 1
        self.lastAvg = currAvg

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 30 minutes
    m = DynamicPlotter(sampleinterval=5, timewindow=1800.)
    m.show()

    sys.exit(app.exec_())
