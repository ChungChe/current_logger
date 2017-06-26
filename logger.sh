#!/usr/bin/env bash
echo "usb inserted at" `date` >> /var/log/usb_plug.log
sudo python /home/pi/current_logger/logger_gui.py 1 >> /var/log/current.log
