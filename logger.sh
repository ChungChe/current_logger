#!/usr/bin/env bash
echo "usb inserted at" `date` >> /var/log/usb_plug.log
python /home/pi/current_logger/logger_gui.py >> /var/log/current.log
