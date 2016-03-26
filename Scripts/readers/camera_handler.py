import cv2
import logging

logger = logging.getLogger("arduino.server")

class VideoCapture(object):

    def get(self):
        logger.debug('Getting capture Object')
        return self.capture

    def __init__(self):
        #enable video capture
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
        self.capture.set(cv2.cv.CV_CAP_PROP_SATURATION,0.2)
        logger.debug('Setting capture object')
 
        super(VideoCapture, self).__init__()

