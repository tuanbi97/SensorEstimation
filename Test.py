import socket
import sys
import time

import numpy as np
from matplotlib import animation

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

class SensorStream(FigureCanvas, animation.FuncAnimation):

    aZ = []
    ID = []
    xrange = 400
    yrange = 4
    cnt = 0

    def __init__(self, figsize):

        self.initialize_socket()

        self.fig = Figure(figsize=figsize)
        self.ax = self.fig.subplots()
        #print(str(self.fig.canvas))
        self.ax.axis([0, self.xrange, -self.yrange, self.yrange])
        self.line, = self.ax.plot(self.ID, self. aZ)
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
        chunk = data.split()
        #print(len(chunk))
        tmp1 = 0.0
        for j in range(0, len(chunk)):
            tmp = chunk[j]
            # print (tmp)
            tmp = float(tmp)
            self.cnt += 1
            if self.cnt % 2 == 0:
                self.aZ = np.append(self.aZ, tmp1)
                self.ID = np.append(self.ID, int(tmp))
                #print(tmp1, ' ', tmp)
                if int(tmp) > self.xrange:
                    self.aZ = self.aZ[1:len(self.aZ)]
                    self.ID = self.ID[1:len(self.ID)]
                    self.ax.axis([int(tmp) - self.xrange + 1, int(tmp), -self.yrange, self.yrange])
            else:
                tmp1 = tmp
        self.line.set_data(self.ID, self.aZ)
        return self.line,

class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        self.layout = QtWidgets.QVBoxLayout(self._main)

        self.sensorstream = SensorStream((10, 3))
        self.layout.addWidget(self.sensorstream)

        self.startButton = QtWidgets.QPushButton()


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    sys.exit(qapp.exec_())