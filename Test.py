import sys
import math
import socket
import time

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph import Transform3D
from MadgwickAHRS import MadgwickAHRS
from MahonyAHRS import MahonyAHRS
from SensorStreamer import SensorStreamer
from OpenGL.GL import *


class ViewAxis(gl.GLAxisItem):
    def __init__(self, width=1, mvisible=True, alpha=0.6):
        super(ViewAxis, self).__init__()
        self.width = width
        self.alpha = alpha
        self.mvisible = mvisible

    def paint(self):
        self.setupGLState()

        if self.antialias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glLineWidth(self.width)

        glBegin(GL_LINES)

        x, y, z = self.size()
        glColor4f(0, 0, 1, self.alpha * int(self.mvisible))  # z is blue
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, z)

        glColor4f(0, 1, 0, self.alpha * int(self.mvisible))  # y is green
        glVertex3f(0, 0, 0)
        glVertex3f(0, y, 0)

        glColor4f(1, 0, 0, self.alpha * int(self.mvisible))  # x is red
        glVertex3f(0, 0, 0)
        glVertex3f(x, 0, 0)
        glEnd()

        glLineWidth(1)

class CubeView(gl.GLViewWidget):
    def __init__(self, title='Untitled'):
        super(CubeView, self).__init__()
        self.title = title
        self.initUI(title)

    def initUI(self, title):
        self.opts['elevation'] = 0
        self.opts['azimuth'] = -90
        self.setWindowTitle(title)
        self.setGeometry(1000, 100, 600, 600)

        self.ax = ViewAxis(width=1, alpha=0.6, mvisible=True)
        self.ax.setSize(10, 10, 10)

        v = self.cameraPosition()
        self.box = BoxItem(size=[1.2, 2, 0.3])

        self.addItem(self.box.ax)
        self.addItem(self.ax)

        streamer.register(self.box)

class Transformer():

    def __init__(self):
        self.filter = MadgwickAHRS()
        #self.filter = MahonyAHRS()

    def transform(self, events):

        angles = []
        #angles.append(self.filter.processingEvent(events[len(events) - 1]))
        for i in range(0, len(events)):
            angles.append(self.filter.processingEvent(events[i]))
        return angles

class BoxItem(gl.GLMeshItem):
    def __init__(self, size=[1, 1, 1]):
        self.cX = 0
        self.cY = 0
        self.cZ = 0
        self.verts = []
        tz = -1
        for x in range(-1, 2, 2):
            for y in range(-1, 2, 2):
                tz *= -1
                for z in range(-1, 2, 2):
                    self.verts.append([x * size[0], y * size[1], tz * z * size[2]])

        self.mfaces = []
        self.mcolors = []
        self.listColor = [(230, 25, 75, 0), (60, 180, 75, 0), (255, 225, 25, 0), (0, 130, 200, 0), (245, 130, 48, 0),
                          (145, 30, 180, 0)]
        self.listColor = [(1.0 * np.array(x)) / 255 for x in self.listColor]

        c = 0
        for i in range(0, 5, 4):
            self.mfaces.append([i, i + 1, i + 2])
            self.mfaces.append([i + 2, i + 3, i])
            self.mcolors.append(self.listColor[c])
            self.mcolors.append(self.listColor[c])
            c += 1

        for i in range(0, 4):
            self.mfaces.append([i, (i + 1) % 4, i + 4])
            self.mfaces.append([i + 4, (i + 1) % 4 + 4, (i + 1) % 4])
            self.mcolors.append(self.listColor[c])
            self.mcolors.append(self.listColor[c])
            c += 1

        self.verts = np.array(self.verts)
        self.mfaces = np.array(self.mfaces)
        self.mcolors = np.array(self.mcolors)

        super(BoxItem, self).__init__(vertexes=self.verts,
                                      faces=self.mfaces,
                                      faceColors=self.mcolors,
                                      smooth=False,
                                      drawEdges=False,
                                      drawFaces=True)

        self.ax = ViewAxis(width=1, mvisible=True)
        self.ax.setSize(4, 4, 4)
        self.setParentItem(self.ax)

        self.transformer = Transformer()

    def receive(self, events):
        # print(len(events))
        self.draw(events)

    def draw(self, events):
        angles = self.transformer.transform(events)
        for i in range(0, len(angles)):
            orientation = angles[i]
            #v, rm = self.getRotation(orientation)
            rm = self.getRotation(orientation)
            v = events[i][0]
            v = np.append(v, 1)
            vr = QtGui.QVector4D(v[0], v[1], v[2], v[3])
            vr = rm * vr
            #print(vr)
            dt = self.transformer.filter.invSampleFreq
            linVelx = vr.x() * dt
            linVely = vr.y() * dt
            linVelz = (vr.z() - 9.81) * dt
            self.cX = self.cX + linVelx
            self.cY = self.cY + linVely
            self.cZ = self.cZ + linVelz
            px = self.cX * dt
            py = self.cY * dt
            pz = self.cZ * dt
            print(px, ' ', py, ' ', pz)

            tm = QtGui.QMatrix4x4(1, 0, 0, px, 0, 1, 0, py, 0, 0, 1, pz, 0, 0, 0, 1)
            self.ax.setTransform(tm)

    def mrotate(self, angle, x, y, z):
        tr = Transform3D()
        tr.rotate(angle, x, y, z)
        return tr

    def getRotation(self, angles):
        v = []
        #rotationMatrix = self.mrotate(angles[0], 0, 0, 1) * self.mrotate(angles[1], 1, 0, 0) * self.mrotate(angles[2], 0, 1, 0)
        rotationMatrix = self.mrotate(angles[0], 0, 0, 1) * self.mrotate(angles[1], 0, 1, 0) * self.mrotate(angles[2], 1, 0, 0)
        # test Transform
        # for i in range(0, len(self.verts)):
        #     vertex = self.verts[i]
        #     vertex = np.append(vertex, 1)
        #     vr = QtGui.QVector4D(vertex[0], vertex[1], vertex[2], vertex[3])
        #     vr = rotationMatrix * vr
        #     v.append([vr.x(), vr.y(), vr.z()])
        # return np.array(v), rotationMatrix
        return rotationMatrix

    def translate(self, dx, dy, dz, local=False):
        self.ax.translate(dx, dy, dz, local)

class SensorPlot(pg.PlotWidget):
    def __init__(self, plottype=0, needTr = False, title='Untitled', yRange = [-16, 16], xRange = [0, 600]):
        super(SensorPlot, self).__init__()
        self.transformer = Transformer()
        self.X = []
        self.Y = []
        self.Z = []
        self.maxRangeDisplay = 600
        self.plottype = plottype
        self.getPlotItem().setTitle(title)

        self.setRange(yRange=yRange, xRange=xRange)
        self.needTr = needTr
        self.initialize()

    def initialize(self):
        self.pltX = self.plot(pen=QtGui.QPen(QtGui.QColor(255, 0, 0)))
        self.pltY = self.plot(pen=QtGui.QPen(QtGui.QColor(0, 255, 0)))
        self.pltZ = self.plot(pen=QtGui.QPen(QtGui.QColor(0, 0, 255)))

    def mrotate(self, angle, x, y, z):
        tr = Transform3D()
        tr.rotate(angle, x, y, z)
        return tr

    def sensorTransform(self, events, angle, plottype):
        #print(1)
        rotationMatrix = self.mrotate(angle[0], 0, 0, 1) * self.mrotate(angle[1], 0, 1, 0) * self.mrotate(angle[2], 1, 0, 0)
        for i in range(0, len(events)):
            v = events[i][plottype]
            v = np.append(v, 1)
            vr = QtGui.QVector4D(v[0], v[1], v[2], v[3])
            vr = rotationMatrix * vr
            events[i][plottype] = [vr.x(), vr.y(), vr.z()]

    def receive(self, events):
        if self.needTr:
            angles = self.transformer.transform(events)
            self.sensorTransform(events, angles[0], self.plottype) #one angle

        self.draw(events)

    def draw(self, events):
        for i in range(len(events)):
            event = events[i]
            self.X.append(event[self.plottype][0])
            self.Y.append(event[self.plottype][1])
            self.Z.append(event[self.plottype][2])
            id = int(event[3])
            if id > self.maxRangeDisplay:
                self.X = self.X[1:len(self.X)]
                self.Y = self.Y[1:len(self.Y)]
                self.Z = self.Z[1:len(self.Z)]
                self.setRange(xRange = [id - self.maxRangeDisplay + 1, id])
        self.pltX.setData(y = self.X, x = range(id - len(self.X) + 1, id + 1))
        self.pltY.setData(y = self.Y, x = range(id - len(self.Y) + 1, id + 1))
        self.pltZ.setData(y = self.Z, x = range(id - len(self.Z) + 1, id + 1))

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()

    def initUI(self):

        layout = QtGui.QGridLayout()
        layout.setSpacing(20)
        self.setLayout(layout)
        self.setGeometry(200, 100, 800, 800)

        self.p1 = SensorPlot(0, False, 'Acceleration', yRange = [-16, 16])
        self.p2 = SensorPlot(0, True, 'Transformed Acceleration', yRange = [-16, 16])

        streamer.register(self.p1)
        streamer.register(self.p2)

        layout.addWidget(self.p1, 0, 0)
        layout.addWidget(self.p2, 1, 0)

streamer = SensorStreamer()
app = QtGui.QApplication(sys.argv)

w = Window()
w.show()
# Cube view
c = CubeView('Baseline')
c.box.transformer.filter = MadgwickAHRS(False)
#c.box.transformer.filter = MahonyAHRS(False)
c.show()

streamer.start(40, PORT = 5556)

sys.exit(app.exec_())
