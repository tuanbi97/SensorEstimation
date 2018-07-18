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
            if len(self.X) > self.maxRangeDisplay:
                self.setRange(xRange = [len(self.X) - self.maxRangeDisplay + 1, len(self.X)])

        self.pltX.setData(y = self.X, x = range(0, len(self.X)))
        self.pltY.setData(y = self.Y, x = range(0, len(self.Y)))
        self.pltZ.setData(y = self.Z, x = range(0, len(self.Z)))