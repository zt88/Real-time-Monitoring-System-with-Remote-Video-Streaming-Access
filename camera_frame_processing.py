#Modified by smartbuilds.io
#Date: 27.09.20
#Desc: This scrtipt script..
import cv2
import numpy as np

# Pi-camera:
# from imutils.video.pivideostream import PiVideoStream

import imutils
import time
from datetime import datetime
import numpy as np

class VideoCamera(object):
    def __init__(self, flip = False, file_type  = ".jpg", photo_string= "stream_photo"):
        # Pi-camera:
        # self.vs = PiVideoStream(resolution=(1920, 1080), framerate=30).start()
        # self.vs = PiVideoStream().start()

        # computer camera
        self.vs = cv2.VideoCapture(0)
        self.flip = flip # Flip frame vertically
        self.file_type = file_type # image type i.e. .jpg
        self.photo_string = photo_string # Name to save the photo
        time.sleep(2.0)

    def __del__(self):
        # self.vs.stop()
        pass

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.flip_if_needed(self.vs.read())
        # ret, jpeg = cv.imencode(self.file_type, frame)
        # self.previous_frame = jpeg
        # return jpeg.tobytes()
        frame = cv2.resize(frame, (1280, 960))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray


    # Take a photo, called by camera button
    def take_picture(self):
        frame = self.flip_if_needed(self.vs.read())
        ret, image = cv2.imencode(self.file_type, frame)
        today_date = datetime.now().strftime("%m%d%Y-%H%M%S") # get current time
        cv2.imwrite(str(self.photo_string + "_" + today_date + self.file_type), frame)
