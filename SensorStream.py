import socket
import sys
import time

import numpy as np
from matplotlib import animation

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt4agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

class SensorStream(FigureCanvas, animation.FuncAnimation):

    aX = []
    aY = []
    aZ = []
    gX = []
    gY = []
    gZ = []
    mX = []
    mY = []
    mZ = []
    ID = []
    xrange = 400
    yrange = 10
    cnt = 0

    def __init__(self, figsize):

        self.initialize_socket()

        self.fig = Figure(figsize=figsize)
        self.AS = self.fig.subplots(3, 1)

        self.p1 = self.AS[0]
        self.p2 = self.AS[1]
        self.p3 = self.AS[2]

        #print(str(self.fig.canvas))
        self.p1.axis([0, self.xrange, -self.yrange, self.yrange])
        self.p2.axis([0, self.xrange, -self.yrange, self.yrange])
        self.p3.axis([0, self.xrange, -self.yrange, self.yrange])

        self.line1, = self.p1.plot(self.ID, self.aX, color='r')
        self.line2, = self.p2.plot(self.ID, self.aY, color ='g')
        self.line3, = self.p3.plot(self.ID, self.aZ, color='b')
        FigureCanvas.__init__(self, self.fig)
        animation.FuncAnimation.__init__(self, fig = self.fig, func = self.animate, interval = 10, blit=True)

    def initialize_socket(self):
        self.HOST = ''
        self.PORT = 5555
        self.BUFSIZE = 4096

        self.serv = socket.socket()
        try:
            self.serv.bind((self.HOST, self.PORT))
            self.serv.listen(socket.SOMAXCONN)
            self.conn, self.addr = self.serv.accept()
        except :
            self.serv.close()
            exit(1)

    def animate(self, i):
        data = self.conn.recv(4096)
        chunk = data.split('\n')
        for j in range(0, len(chunk) - 1):
            tmp = chunk[j]
            ax, ay, az, gx, gy, gz, mx, my, mz, id = [float(x) for x in tmp.split()]
            print (ax, ' ', ay, ' ', az, ' ', gx, ' ', gy, ' ', gz, ' ', mx, ' ', my, ' ', mz, ' ', id)
            self.aX = np.append(self.aX, ax)
            self.aY = np.append(self.aY, ay)
            self.aZ = np.append(self.aZ, az)

            self.gX = np.append(self.gX, gx)
            self.gY = np.append(self.gY, gy)
            self.gZ = np.append(self.gZ, gz)

            self.mX = np.append(self.mX, mx)
            self.mY = np.append(self.mY, my)
            self.mZ = np.append(self.mZ, mz)
            self.ID = np.append(self.ID, int(id))
            if id > self.xrange:
                self.aX = self.aX[1:len(self.aX)]
                self.aY = self.aY[1:len(self.aY)]
                self.aZ = self.aZ[1:len(self.aZ)]

                self.gX = self.gX[1:len(self.gX)]
                self.gY = self.gY[1:len(self.gY)]
                self.gZ = self.gZ[1:len(self.gZ)]

                self.mX = self.mX[1:len(self.mX)]
                self.mY = self.mY[1:len(self.mY)]
                self.mZ = self.mZ[1:len(self.mZ)]

                self.ID = self.ID[1:len(self.ID)]
                self.p1.axis([id - self.xrange + 1, id, -self.yrange, self.yrange])
                self.p2.axis([id - self.xrange + 1, id, -self.yrange, self.yrange])
                self.p3.axis([id - self.xrange + 1, id, -self.yrange, self.yrange])

        self.line1.set_data(self.ID, self.aX)
        self.line2.set_data(self.ID, self.aY)
        self.line3.set_data(self.ID, self.aZ)

        return self.line1, self.line2, self.line3,

class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)

        self.sensorstream = SensorStream((10, 8))
        self.layout.addWidget(self.sensorstream)

        self.startButton = QtWidgets.QPushButton()


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    sys.exit(qapp.exec_())