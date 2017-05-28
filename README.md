# current_logger
* Record current value from DCbox current meter with QinHeng CH341 (RS485-USB) connector

Move logger.rules to /etc/udev/rules.d/

Move logger.sh and rm.sh to /tmp/

    logger.sh: record current value into /var/log/current.log
    rm.sh: kill the process after the usb is removed

The status of usb's insertion or removal will listed in /var/log/usb_plug.log
