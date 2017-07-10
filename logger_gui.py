#!/usr/bin/env python
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

import minimalmodbus
import serial
from time import strftime
import datetime
import thread
from tendo import singleton
from KY_001 import ky_001
mode = 0 # mode 0: test, mode 1: release

current1 = 0.0
current2 = 0.0

class lineEdit(QLineEdit):
    def __init__(self, parent = None):
        super(lineEdit, self).__init__(parent)
        self.setReadOnly(True)
        self.setFixedSize(100, 40)
        f = self.font()
        f.setPointSize(20)
        f.setBold(True)
        self.setFont(f)

class DynamicPlotter(QWidget):
    def __init__(self, sampleinterval = 0.1, timewindow = 10., size =(800,500), parent = None):
        super(DynamicPlotter, self).__init__(parent)
        self.current1 = 0.0
        self.current2 = 0.0
        self.dataCount = 1
        self.warnCount = 0
        self.lastWarnVal = 9999
        self.lastAvg = 7777
        # Data stuff
        self._interval = int(sampleinterval * 1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer1 = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.databuffer2 = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.databuffer_tmp = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y1 = np.zeros(self._bufsize, dtype = np.float)
        self.y2 = np.zeros(self._bufsize, dtype = np.float)
        self.thres = np.zeros(self._bufsize, dtype = np.float)
        self.temp = np.zeros(self._bufsize, dtype = np.float)
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
        self.curve1 = self.plt.plot(self.x, self.y1, pen=(255,0,0))
        self.curve2 = self.plt.plot(self.x, self.y2, pen=(0,255,0))
        self.thres_curve = self.plt.plot(self.x, self.thres, pen=(255,255,0))
        self.temp_curve = self.plt.plot(self.x, self.temp, pen=(0,0,255))

        # QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self._interval)

        self.verticalLayout = QVBoxLayout(self)
        # Label
        current_label1 = QLabel(self)
        current_label1.setText(u"過濾機電流：")
        self.verticalLayout.addWidget(current_label1)
        self.currentEdit1 = lineEdit(self)
        self.verticalLayout.addWidget(self.currentEdit1)
        
        current_label2 = QLabel(self)
        current_label2.setText(u"第6台電流：")
        self.verticalLayout.addWidget(current_label2)
        self.currentEdit2 = lineEdit(self)
        self.verticalLayout.addWidget(self.currentEdit2)
       
        temp_label = QLabel(self)
        temp_label.setText(u"目前溫度：")
        self.verticalLayout.addWidget(temp_label)
        self.tempEdit = lineEdit(self)
        self.verticalLayout.addWidget(self.tempEdit)

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
        self.temp_meter = ky_001(5)
    def set_data1(self, val):
        self.current1 = val
    def set_data2(self, val):
        self.current2 = val
    def get_data1(self):
        global current1
        return current1 
    def get_data2(self):
        global current2
        return current2 

    def update_plot(self):
        curr_val1 = self.get_data1()
        self.databuffer1.append(curr_val1)
        curr_val2 = self.get_data2()
        self.databuffer2.append(curr_val2)

        curr_temp = self.temp_meter.get_temp()
        self.databuffer_tmp.append(curr_temp)
        #print('curr_val: {}'.format(curr_val))
        self.currentEdit1.setText(str(curr_val1))
        self.currentEdit2.setText(str(curr_val2))
#self.avgEdit.setText('{:3.2f}'.format(currAvg))
        self.tempEdit.setText('{:2.2f}'.format(curr_temp))
        if curr_val1 < 80 and self.lastWarnVal >= 80:
            self.warnCount += 1
        self.lastWarnVal = curr_val1

        self.warnEdit.setText(str(self.warnCount))

        # incremental avg calculation
        # see:
        # https://ubuntuincident.wordpress.com/2012/04/25/calculating-the-average-incrementally/

        if self.lastAvg == 7777:
            self.lastAvg = curr_val1
        currAvg = self.lastAvg + (curr_val1 - self.lastAvg) / float(self.dataCount)
        
        self.avgEdit.setText('{:3.2f}'.format(currAvg))
        self.y1[:] = self.databuffer1
        self.y2[:] = self.databuffer2
        self.curve1.setData(self.x, self.y1)
        self.curve2.setData(self.x, self.y2)
        thres = np.empty(len(self.y1))
        thres.fill(80)
        self.thres_curve.setData(self.x, thres)
        
        self.temp_curve.setData(self.x, self.databuffer_tmp)
        self.dataCount += 1
        self.lastAvg = currAvg

        current_time = strftime("%Y/%m/%d %H:%M:%S")
        sys.stdout.write("{} {} {} {}\n".format(current_time, curr_val1, curr_temp, curr_val2))
        sys.stdout.flush()

def log_data(threadName):
    app = QApplication(sys.argv)
    m = DynamicPlotter(sampleinterval = 5, timewindow = 1800.)
    m.show()
    sys.exit(app.exec_())

qq = True

def read_data_from_current_meter(threadName):
    while True:
        try:
            global current1
            global current2
            global qq
            if mode == 1:
                if qq == True:
                    current1 = instrument1.read_register(30, 1) # Register number, number of decimals
                    qq = False
                else:
                    current2 = instrument2.read_register(30, 1) # Register number, number of decimals
                    qq = True
            else:
                time.sleep(1)
                current1 = randint(30, 120)
                current2 = randint(30, 120)
            #current1 = instrument.read_register(30, 1) # Register number, number of decimals
            #print("Current: {}".format(current1))
        except Exception as e:
            #print(e)
            pass


if __name__ == '__main__':
    #app = QApplication(sys.argv)

    # 30 minutes
    #m = DynamicPlotter(sampleinterval=5, timewindow=1800.)
    #m.show()
    if len(sys.argv) == 2:
        #print("Mode: {}".format(sys.argv[1]))
        global mode
        mode = int(sys.argv[1])
    if mode == 1:
        me = singleton.SingleInstance()

        mb = minimalmodbus
        mb.BAUDRATE = 4800
        mb.PARITY = 'N'
        mb.BYTESIZE = 8
        mb.STOPBITS = 1
        mb.TIMEOUT = 0.05


        instrument1 = mb.Instrument('/dev/ttyUSB0', 1) # port name, slave address
        #instrument1.mode = minimalmodbus.MODE_RTU
        
        instrument2 = mb.Instrument('/dev/ttyUSB0', 2) # port name, slave address
        #instrument2.mode = minimalmodbus.MODE_RTU
    

    #sys.exit(app.exec_())
    try:
        thread.start_new_thread(read_data_from_current_meter, ("thread1", ))
        thread.start_new_thread(log_data, ("thread2", ))
    except Exception as e:
        print(e)
    while(1):
        try:
            time.sleep(5)
        except Exception as e:
            print(e)
            break
