import socket
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

def init():
    ID = []
    aZ = []
    line.set_data(ID, aZ)
    return line,


def animate(i):
    global aZ
    global ID
    global tmp1
    global check
    data = conn.recv(4096)
    chunk = data.split()
    #print(len(chunk))
    for j in range(0, len(chunk)):
        tmp = chunk[j]
        #print (tmp)
        tmp = float(tmp)
        check += 1
        if check % 2 == 0:
            aZ = np.append(aZ, tmp1)
            ID = np.append(ID, int(tmp))
            print (tmp1, ' ', tmp)
            if int(tmp) > xrange:
                aZ = aZ[1:len(aZ)]
                ID = ID[1:len(ID)]
                plt.axis([int(tmp) - xrange + 1, int(tmp), -yrange, yrange])
        else:
            tmp1 = tmp
    line.set_data(ID, aZ)

    #print(str(len(ID)))
    return line,

HOST = ''
PORT = 5555
BUFSIZE = 4096

serv = socket.socket()
try:
    serv.bind((HOST, PORT))
    serv.listen(socket.SOMAXCONN)
    conn, addr = serv.accept()
except KeyboardInterrupt:
    print ("KeyboardInterrupt")
    serv.close()
    exit(1)

f = open('test.txt', 'w')
c = 0
aX = []
aY = []
aZ = []
ID = []

tmp1 = 0.0
oldid = -1

xrange = 400
yrange = 4
color = 'b'
fig = plt.figure()
ax = plt.axes(xlim=(0, xrange), ylim=(-yrange, yrange))
line, = ax.plot(ID, aZ)

check = 0

anim = animation.FuncAnimation(fig, animate, init_func=init, interval=10, blit=True)
plt.show()

serv.close()
conn.close()
