import math
import sys
import socket
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from SensorStreamer import SensorStreamer
from SensorPlot import SensorPlot
from pyqtgraph import Transform3D
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


class Transformer():
    @staticmethod
    def transform(events):
        angles = []
        for i in range(len(events)):
            Ex, Ey, Ez = events[i][1] #Mag
            Ax, Ay, Az = events[i][2] #Gra
            Hx = Ey * Az - Ez * Ay
            Hy = Ez * Ax - Ex * Az
            Hz = Ex * Ay - Ey * Ax
            normH = math.sqrt(Hx * Hx + Hy * Hy + Hz * Hz)
            invH = 1.0 / normH
            Hx *= invH
            Hy *= invH
            Hz *= invH
            normA = math.sqrt(Ax * Ax + Ay * Ay + Az * Az)
            invA = 1.0 / normA
            Ax *= invA
            Ay *= invA
            Az *= invA
            Mx = Ay * Hz - Az * Hy
            My = Az * Hx - Ax * Hz
            Mz = Ax * Hy - Ay * Hx
            angle = (math.atan2(-Hy, My), math.asin(Ay), math.atan2(-Ax, Az))
            angles.append([math.degrees(x) for x in angle])
        return angles

class BoxItem(gl.GLMeshItem):
    def __init__(self, size=[1, 1, 1]):
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

    def receive(self, events):
        # print(len(events))
        angles = Transformer.transform(events)
        self.draw(angles)

    def draw(self, angles):
        for i in range(0, len(angles)):
            orientation = angles[i]
            #print(orientation)
            v, rm = self.getRotation(orientation)
            self.ax.setTransform(rm)

    def mrotate(self, angle, x, y, z):
        tr = Transform3D()
        tr.rotate(angle, x, y, z)
        return tr

    def getRotation(self, angles):
        v = []
        # rotationMatrix = self.mrotate(angles[0], 0, 0, 1) * self.mrotate(angles[1], 1, 0, 0) * self.mrotate(angles[2], 0, 1, 0) #* self.mrotate(angles[1], 1, 0, 0)# * self.mrotate(angles[0], 0, 0, 1)
        rotationMatrix = self.mrotate(angles[0], 0, 0, 1) * self.mrotate(angles[1], 1, 0, 0) * self.mrotate(angles[2], 0, 1, 0)
        # test Transform
        for i in range(0, len(self.verts)):
            vertex = self.verts[i]
            vertex = np.append(vertex, 1)
            vr = QtGui.QVector4D(vertex[0], vertex[1], vertex[2], vertex[3])
            vr = rotationMatrix * vr
            v.append([vr.x(), vr.y(), vr.z()])
        return np.array(v), rotationMatrix

    def translate(self, dx, dy, dz, local=False):
        self.ax.translate(dx, dy, dz, local)


class CubeView(gl.GLViewWidget):
    def __init__(self, title='Untitled'):
        super(CubeView, self).__init__()
        self.title = title
        self.initUI(title)

    def initUI(self, title):
        self.opts['elevation'] = 0
        self.opts['azimuth'] = -90
        self.setWindowTitle(title)
        self.setGeometry(1000, 110, 600, 600)

        self.ax = ViewAxis(width=1, alpha=0.6, mvisible=True)
        self.ax.setSize(10, 10, 10)

        v = self.cameraPosition()
        self.box = BoxItem(size=[1.2, 2, 0.3])

        self.addItem(self.box.ax)
        self.addItem(self.ax)

        streamer.register(self.box)

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()

    def initUI(self):

        layout = QtGui.QGridLayout()
        layout.setSpacing(20)
        self.setLayout(layout)
        self.setGeometry(300, 110, 600, 600)

        self.p1 = SensorPlot(0, 'Accelerometer', yRange = [-16, 16])
        self.p2 = SensorPlot(1, 'Magnetometer', yRange = [-100, 100])
        self.p3 = SensorPlot(2, 'Gravity', yRange= [-30, 30])

        streamer.register(self.p1)
        streamer.register(self.p2)
        streamer.register(self.p3)

        layout.addWidget(self.p1, 0, 0)
        layout.addWidget(self.p2, 1, 0)
        layout.addWidget(self.p3, 2, 0)

streamer = SensorStreamer()
app = QtGui.QApplication(sys.argv)

#Sensor views
w = Window()
w.show()

#Cube view
c = CubeView()
c.show()

streamer.start(40)
sys.exit(app.exec_())
