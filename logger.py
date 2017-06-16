#!/usr/bin/env python
import minimalmodbus
import serial
import time
from time import strftime
import datetime
import thread
import sys
from tendo import singleton

from logger_gui import *
from random import randint

me = singleton.SingleInstance()

mb = minimalmodbus
mb.BAUDRATE = 4800
mb.PARITY = 'N'
mb.BYTESIZE = 8
mb.STOPBITS = 1
mb.TIMEOUT = 0.05

current = 0.0

instrument = mb.Instrument('/dev/ttyUSB0', 1) # port name, slave address
instrument.mode = minimalmodbus.MODE_RTU

def print_data(threadName):
    m = DynamicPlotter(sampleinterval = 5, timewindow = 1800.)
    m.show()
    sys.exit(app.exec_())

    global current

    while True:
        global current
        time.sleep(5)
        current_time = strftime("%Y/%m/%d %H:%M:%S")
        sys.stdout.write("{} {}\n".format(current_time, current))
        sys.stdout.flush()

def read_data_from_current_meter(threadName):
    while True:
        try:
            global current
            time.sleep(1)
            current = randint(30, 120)
            #current = instrument.read_register(30, 1) # Register number, number of decimals
            #print("Current: {}".format(current))
        except Exception as e:
            #print(e)
            pass

try:
    thread.start_new_thread(read_data_from_current_meter, ("thread1", ))
    thread.start_new_thread(print_data, ("thread2", ))
except Exception as e:
    print(e)
while(1):
    time.sleep(60)
    pass
