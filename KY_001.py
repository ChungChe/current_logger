# coding=utf-8
# needed modules will be imported and initialised
import glob
import time
from time import sleep
from time import strftime
import RPi.GPIO as GPIO

class ky_001:
    def __init__(self, sleep_time = 5):
        self.sleep_time = sleep_time

        # add 
        #       dtoverlay=w1-gpio,gpiopin=4
        # to /boot/config.txt then reboot
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Initialise, the sensor will be read "blind"
        self.get_device_str()
    # /sys/bus/w1/devices/28-00005fc7961/w1_slave 
    def get_device_file(self): 
        base_dir = '/sys/bus/w1/devices/'
        while True:
            try:
                device_folder = glob.glob(base_dir + '28*')[0]
                break
            except IndexError:
                sleep(0.5)
                continue
        device_file = device_folder + '/w1_slave'
        return device_file 
 
    # cat /sys/bus/w1/devices/28-00005fc7961/w1_slave 
    def get_device_str(self):
        device_file = self.get_device_file()
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def get_sleep_time(self):
        return self.sleep_time
 
    def get_temp(self):
        lines = self.get_device_str()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.get_device_str()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
 
if __name__ == "__main__":
    k = ky_001(5)
    try:
        while True:
            current_time = strftime("%Y/%m/%d %H:%M:%S")
            print("{} {}".format(current_time, k.get_temp()))
            time.sleep(k.get_sleep_time())
     
    except KeyboardInterrupt:
        GPIO.cleanup()
