from __future__ import with_statement
import logging
#import cv2

logger = logging.getLogger("arduino.server")
from tornado.gen import coroutine
from concurrent.futures import ThreadPoolExecutor
import datetime
import time
import threading

import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from service.models import Settings

MAX_WORKERS = 4
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)


def take_photos():
    """ This will be executed in `executor` pool. """

    logger.info("Taking photos")
    image_list = list()
    capture = cv2.VideoCapture(0)
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 280)
    capture.set(cv2.cv.CV_CAP_PROP_SATURATION, 0.2)

    for i in range(3):
        time.sleep(2)
        ret, im = capture.read()
        img_file = '/media/usb/images/{}-test-{}.png'.format(datetime.datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S.%f"), i)
        cv2.imwrite(img_file, im)
        image_list.append(img_file)
    
    del(capture)

    return image_list


def send_mail(image_list):
    logger.info("Sending mail... with photos: {}".format(image_list))
    msg = MIMEMultipart()
    msg['Subject'] = '{} Motion detected...'.format(datetime.datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S.%f"))
    msg['From'] = "iothomechris@gmail.com"
    msg['To'] = "xpapazaf@gmail.com"
    msg.preamble = 'Home Monitoring...'
    for file in image_list:
        # Open the files in binary mode.  Let the MIMEImage class automatically
        # guess the specific image type.
        try:
            with open(file, 'rb') as fd:
                img = MIMEImage(fd.read(), _subtype="png")
                msg.attach(img)
        except Exception as e: # parent of IOError, OSError *and* WindowsError where available
            logger.error(e, exc_info=True)

    try:

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.set_debuglevel(True)
        s.starttls()
        s.login('iothomechris@gmail.com', '10th0m3chr1s')
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()
        logger.info("Email sent")
    except Exception as e:
        logger.error(e, exc_info=True)


def do():
    try:
        logger.info("will send photos now")
        #photos = take_photos()
        #send_mail(photos)
    except Exception as e:
        logger.error(e, exc_info=True)


@coroutine
def temperature_handler(device, temperature):
    log_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + "\t" + temperature + "\n"
    with open("/media/pi/RPI/raspberry/temperature.log", "a") as myfile:
        myfile.write(log_data)


@coroutine
def humidity_handler(device, humidity):
    log_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + "\t" + humidity + "\n"
    with open("/media/pi/RPI/raspberry/humidity.log", "a") as myfile:
        myfile.write(log_data)


@coroutine
def motion_handler(device, motion):
    if motion == "1":
        # check if motion detection is enabled
        motion = Settings.select().where(Settings.key == 'motion').get()

        if motion and motion.value == 'on':
            yield executor.submit(do)
