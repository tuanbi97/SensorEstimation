import os
import sys
import cv2
import time
from scipy import io

import pyrealsense2 as rs
import numpy as np
from PyQt4 import QtGui, QtCore

class VideoStream(QtCore.QThread):

    isCancelled = True

    def run(self):
        pipe = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        profile = pipe.start(config)
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow('RealSense', 100, 90)
        try:
            while (True):
                if self.isCancelled:
                    continue
                # print(self.isCancelled)
                frames = pipe.wait_for_frames()
                ctime = time.clock()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                #print(frames.get_capture_time())
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                io.savemat(self.saveDir + '/depth_%05d.mat' % self.frameId, {'depth': depth_image, 'sTime': ctime})

                # Stack both images vertically
                images = np.vstack((color_image, depth_colormap))

                # Show images
                cv2.imshow('RealSense', images)
                #cv2.imwrite(self.saveDir + '/rgb_%05d.png' % self.frameId, color_image)
                cv2.waitKey(1)
                self.frameId += 1
        finally:
            pipe.stop()
            # self.terminate()

    def record(self, saveDir):
        self.saveDir = saveDir
        if not os.path.exists(self.saveDir):
            os.mkdir(saveDir)
        self.isCancelled = False
        self.frameId = 0

    def stop(self):
        self.isCancelled = True