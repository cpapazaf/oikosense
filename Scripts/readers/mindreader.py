#!/usr/bin/python
# -*- coding: ascii -*-
"""Mind reader
"""

import datetime
import sys
import time

from Scripts import mindwave


def main(device):
    
    headset = mindwave.Headset(device)
    time.sleep(2)
    
    headset.connect()
    print("Connecting...")
    
    while headset.status != 'connected':
        time.sleep(0.5)
        if headset.status == 'standby':
            headset.connect()
            print("Retrying connect...")
    print("Connected.")
    
    while True:
        if headset.listener.last_time:
            if headset.listener.last_time < time.time() - 5:
                print("frozen")
                headset.serial_close()
                break
        log_line = 'attention:%r\tmeditation:%r\traw_value:%r' % (
            headset.attention, headset.meditation, headset.raw_value)
        print(log_line)
        sys.stdout.flush()
        log_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + "\t" + log_line + "\n"
        with open("/media/usb/raspberry/mindwave.log", "a") as mood_file:
            mood_file.write(log_data)
        time.sleep(3)

if __name__ == '__main__':
    
    if sys.platform == 'win32':
        device = 'COM9'
    else:
        device = '/dev/ttyUSB0'
    while True: 
        main(device)
