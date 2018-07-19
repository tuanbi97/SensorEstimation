from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
class SensorPlot(pg.PlotWidget):

    def __init__(self, plottype=0, title='Untitled', yRange = [-16, 16], xRange = [0, 600]):
        super(SensorPlot, self).__init__()
        self.X = []
        self.Y = []
        self.Z = []
        self.maxRangeDisplay = 600
        self.plottype = plottype
        self.getPlotItem().setTitle(title)

        self.setRange(yRange = yRange, xRange = xRange)
        self.initialize()


    def initialize(self):
        self.pltX = self.plot(pen=QtGui.QPen(QtGui.QColor(255, 0, 0)))
        self.pltY = self.plot(pen=QtGui.QPen(QtGui.QColor(0, 255, 0)))
        self.pltZ = self.plot(pen=QtGui.QPen(QtGui.QColor(0, 0, 255)))

    def receive(self, events):
        print (len(events))
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