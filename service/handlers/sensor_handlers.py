from __future__ import with_statement
from tornado.gen import coroutine
from tornado.options import options
from concurrent.futures import ThreadPoolExecutor
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from service.models import Settings
from os.path import join
import smtplib
import datetime
import time
import threading
import logging

logger = logging.getLogger("arduino.server")

MAX_WORKERS = 4
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

'''
def take_photos():
    """ This will be executed in `executor` pool. """
    import cv2
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
'''

def send_mail(image_list):
    logger.info("Sending mail...")
    msg = MIMEMultipart()
    msg['Subject'] = '{} Motion detected...'.format(datetime.datetime.utcnow().strftime("%Y-%m-%d-%H:%M:%S.%f"))
    msg['From'] = options["mail_from"]
    msg['To'] = options["mail_to"]
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
        s.login(options["mail_login_uname"], options["mail_login_passwd"])
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()
        logger.info("Email sent")
    except Exception as e:
        logger.error(e, exc_info=True)


def notify():
    try:
        #photos = take_photos()
        #send_mail(photos)
        send_mail([])
    except Exception as e:
        logger.error(e, exc_info=True)


@coroutine
def temperature_handler(device, temperature):
    log_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + "\t" + temperature + "\n"
    with open(join(options["storage_location"], "temperature.log"), "a") as myfile:
        myfile.write(log_data)


@coroutine
def humidity_handler(device, humidity):
    log_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") + "\t" + humidity + "\n"
    with open(join(options["storage_location"], "humidity.log"), "a") as myfile:
        myfile.write(log_data)


@coroutine
def motion_handler(device, motion):
    if motion == "1":
        # check if motion detection is enabled
        motion = Settings.select().where(Settings.key == 'motion').get()

        if motion and motion.value == 'on':
            yield executor.submit(notify)
