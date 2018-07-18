import sys
import socket
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from SensorStreamer import SensorStreamer
from SensorPlot import SensorPlot

class CubeView(gl.GLViewWidget):
    def __init__(self):
        super(CubeView, self).__init__()

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()

    def initUI(self):

        layout = QtGui.QGridLayout()
        layout.setSpacing(20)
        self.setLayout(layout)

        self.p1 = SensorPlot(0, 'Accelerometer', yRange = [-16, 16])
        self.p2 = SensorPlot(1, 'Gyroscope', yRange = [-10, 10])
        self.p3 = SensorPlot(2, 'Magnetometer', yRange= [-60, 100])

        streamer.register(self.p1)
        streamer.register(self.p2)
        streamer.register(self.p3)

        layout.addWidget(self.p1, 0, 0)
        layout.addWidget(self.p2, 1, 0)
        layout.addWidget(self.p3, 2, 0)

        streamer.start(50)

streamer = SensorStreamer()
app = QtGui.QApplication(sys.argv)
w = Window()
w.show()

sys.exit(app.exec_())
