import tornado.gen
import logging
import datetime

logger = logging.getLogger("arduino.server")

@tornado.gen.coroutine
def read_sensors(arduino_humidity):
    import time
    from time import gmtime, strftime
    
    humidity_data = arduino_humidity.readline().rstrip()
    #heartbeat_data = arduino_heartbeat.readline().rstrip()
    if humidity_data:
        log_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + "\t" + humidity_data  + "\n"
        with open("/media/usb/raspberry/hum-temp.log", "a") as myfile:
            myfile.write(log_data)
            logger.debug(log_data)

    
