import sys
import cv2

import pyrealsense2 as rs
import numpy as np
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

class VideoStream(QtCore.QThread):

    def run(self):
        pipe = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        profile = pipe.start(config)
        try:
            while (True):
                frames = pipe.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                images = np.hstack((color_image, depth_colormap))

                # Show images
                cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('RealSense', images)
                cv2.waitKey(1)

                # print(np.shape(color_image))
            # for f in frames:
            #     print(f.profile)
        finally:
            pipe.stop()

app = QtGui.QApplication(sys.argv)
th = VideoStream()
th.start()
sys.exit(app.exec_())