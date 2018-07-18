import sys
import socket
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from SensorStreamer import SensorStreamer
from SensorPlot import SensorPlot

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()

    def initUI(self):
        layout = QtGui.QGridLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        p1 = SensorPlot(0)
        p2 = SensorPlot(1)
        p3 = SensorPlot(2)

        streamer.register(p1)
        streamer.register(p2)
        streamer.register(p3)

        layout.addWidget(p1, 0, 0)
        layout.addWidget(p2, 1, 0)
        layout.addWidget(p3, 2, 0)
        streamer.start(5)


streamer = SensorStreamer()
app = QtGui.QApplication(sys.argv)
w = Window()
w.show()

sys.exit(app.exec_())
