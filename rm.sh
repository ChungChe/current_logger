#!/usr/bin/env bash
echo "usb removed at" `date` >> /var/log/usb_plug.log
ps aux | grep root | grep logger.py | awk '{print $2}' | xargs kill
