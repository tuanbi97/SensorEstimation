import socket
import time
import numpy as np
from PyQt4 import QtCore

class SensorStreamer:

    def __init__(self):
        self.listeners = []
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.lastCall = time.clock()

    def init_socket(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.serv = socket.socket()
        try:
            self.serv.bind((self.HOST, self.PORT))
            self.serv.listen(socket.SOMAXCONN)
            self.conn, self.addr = self.serv.accept()
        except KeyboardInterrupt:
            self.serv.close()
            exit(1)

    def update(self):
        #t = time.clock()
        #print(t - self.lastCall)
        #self.lastCall = t
        data = self.conn.recv(4096)
        chunk = data.split('\n')
        events = []
        for j in range(0, len(chunk) - 1):
            tmp = chunk[j]
            ax, ay, az, gx, gy, gz, id, nanoTime = [float(x) for x in tmp.split()]
            event = []
            event.append((ax, ay, az))
            event.append((gx, gy, gz))
            event.append((0, 0, 0)) #magnetic = 0
            event.append(id)
            event.append(nanoTime)
            events.append(event)
        self.notifyAll(events)

    def notifyAll(self, events):
        for i in range(0, len(self.listeners)):
            self.listeners[i].receive(np.array(events))

    def register(self, listener):
        self.listeners.append(listener)

    def start(self, delay=50, HOST = '', PORT = 5555):
        self.init_socket(HOST, PORT)
        self.timer.start(delay)
