import sys
import math
import socket
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from SensorStreamer import SensorStreamer
from SensorPlot import SensorPlot
from OpenGL.GL import *

class ViewAxis(gl.GLAxisItem):
    def __init__(self, width = 1, mvisible = True, alpha = 0.6):
        super(ViewAxis, self).__init__()
        self.width = width
        self.alpha = alpha
        self.mvisible = mvisible

    def paint(self):

        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glLineWidth(self.width)

        glBegin(GL_LINES)

        x, y, z = self.size()
        glColor4f(0, 0, 1, self.alpha * int(self.mvisible))  # z is green
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, z)

        glColor4f(0, 1, 0, self.alpha * int(self.mvisible))  # y is yellow
        glVertex3f(0, 0, 0)
        glVertex3f(0, y, 0)

        glColor4f(1, 0, 0, self.alpha * int(self.mvisible))  # x is blue
        glVertex3f(0, 0, 0)
        glVertex3f(x, 0, 0)
        glEnd()

        glLineWidth(1)

class CubeItem(gl.GLBoxItem):
    def __init__(self):
        super(CubeItem, self).__init__()
        self.setSize(x = 3, y = 5, z = 0.5)

    def receive(self, events):
        print (len(events))
        self.draw(events)

    def draw(self, events):
        for i in range(0, len(events)):
            event = events[i]
            orientation = [x * 180.0 / math.pi for x in event[4]]
            print(orientation)
            self.resetTransform()
            self.rotate(orientation[0], 1, 0, 0)
            self.rotate(orientation[1], 0, 1, 0)
            self.rotate(orientation[2], 0, 0, 1)

class CubeView(gl.GLViewWidget):
    def __init__(self, title = 'Untitled'):
        super(CubeView, self).__init__()
        self.title = title
        self.initUI(title)

    def initUI(self, title):
        self.opts['elevation'] = 0
        self.opts['azimuth'] = -90
        self.setWindowTitle(title)
        self.setGeometry(600, 110, 600, 600)

        self.ax = ViewAxis(width = 1, mvisible=True)
        self.ax.setSize(10, 10, 10)
        v = self.cameraPosition()
        self.ax.translate(v.x(), v.y() + 8, v.z())
        self.box = CubeItem()
        #self.box.setParentItem(self.ax)
        #
        # ax2 = ViewAxis(width = 4, mvisible=True)
        # ax2.translate(1.5, 2.5, 0.25)
        # ax2.setParentItem(self.box)

        self.addItem(self.ax)

        #self.box.translate(-1.5, -2.5, -0.25)

        streamer.register(self)

    def receive(self, events):
        print (len(events))
        self.draw(events)

    def draw(self, events):
        self.box.hide()
        self.box = CubeItem()
        self.box.translate(-1.5, -2.5, -0.25)

        ax2 = ViewAxis(width=4, mvisible=True)
        ax2.translate(1.5, 2.5, 0.25)
        ax2.setParentItem(self.box)

        for i in range(0, len(events)):
            event = events[i]
            orientation = [x * 180.0 / math.pi for x in event[4]]
            print(orientation)
            self.box.rotate(orientation[0], 1, 0, 0)
            self.box.rotate(orientation[1], 0, 1, 0)
            self.box.rotate(orientation[2], 0, 0, 1)

        self.box.setParentItem(self.ax)


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

streamer = SensorStreamer()
app = QtGui.QApplication(sys.argv)
w = Window()
w.show()

#streamer.start(40)

#Cube view
c = CubeView('Baseline')
c.show()

streamer.start(40)

sys.exit(app.exec_())
