import math
import numpy as np
import struct

import time


class TR_IMUFilter:
    def __init__(self):
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0

        self.exInt = 0.0
        self.eyInt = 0.0
        self.ezInt = 0.0

        self.twoKp = 2.0 * 2.0
        self.twoKi = 2.0 * 0.005

        self.integralFBx = 0.0
        self.integralFBy = 0.0
        self.integralFBz = 0.0

        self.lastUpdate = time.clock()
        self.now = 0

    def processingEvent(self, event):
        self.accelX, self.accelY, self.accelZ = event[0]
        self.gyroX, self.gyroY, self.gyroZ, = event[1]
        self.magX, self.magY, self.magZ = event[2]

        return self.getYPR()

    def getEuler(self):
        q = self.getQuaternion()
        angles = np.zeros(3)
        angles[0] = math.atan2(2 * q[1] * q[2] - 2 * q[0] * q[3], 2 * q[0] * q[0] + 2 * q[1] * q[1] - 1) * 180 / math.pi
        angles[1] = -math.asin(2 * q[1] * q[3] + 2 * q[0] * q[2]) * 180 / math.pi
        angles[2] = math.atan2(2 * q[2] * q[3] - 2 * q[0] * q[1], 2 * q[0] * q[0] + 2 * q[3] * q[3] - 1) * 180 / math.pi
        return angles

    def getQuaternion(self):

        self.now = time.clock()
        self.sampleFreq = 1.0 / (self.now - self.lastUpdate)
        self.lastUpdate = self.now;

        self.updateAHRS(self.gyroX * math.pi / 180, self.gyroY * math.pi / 180, self.gyroZ * math.pi / 180, self.accelX, self.accelY, self.accelZ, self.magX, self.magY, self.magZ)
        return [self.q0, self.q1, self.q2, self.q3]

    def getYPR(self):
        q = self.getQuaternion()
        gx = 2 * (q[1] * q[3] - q[0] * q[2])
        gy = 2 * (q[0] * q[1] + q[2] * q[3])
        gz = q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3]

        angles = np.zeros(3)
        angles[2] = math.atan(gy / math.sqrt(gx * gx + gz * gz)) * 180 / math.pi
        angles[1] = math.atan(gx / math.sqrt(gy * gy + gz * gz)) * 180 / math.pi
        angles[0] = math.atan2(2 * q[1] * q[2] - 2 * q[0] * q[3], 2 * q[0] * q[0] + 2 * q[1] * q[1] - 1) * 180 / math.pi
        return angles

    def updateAHRS(self, gx, gy, gz, ax, ay, az, mx, my, mz):
        recipNorm = 0.0
        halfex = 0.0
        halfey = 0.0
        halfez = 0.0
        qa = 0.0
        qb = 0.0
        qc = 0.0

        q0q0 = self.q0 * self.q0
        q0q1 = self.q0 * self.q1
        q0q2 = self.q0 * self.q2
        q0q3 = self.q0 * self.q3
        q1q1 = self.q1 * self.q1
        q1q2 = self.q1 * self.q2
        q1q3 = self.q1 * self.q3
        q2q2 = self.q2 * self.q2
        q2q3 = self.q2 * self.q3
        q3q3 = self.q3 * self.q3

        if (mx != 0.0) and (my != 0.0) and (mz != 0.0):
            recipNorm = self.invSqrt(mx * mx + my * my + mz * mz);
            mx *= recipNorm;
            my *= recipNorm;
            mz *= recipNorm;
    
            hx = 2.0 * (mx * (0.5 - q2q2 - q3q3) + my * (q1q2 - q0q3) + mz * (q1q3 + q0q2))
            hy = 2.0 * (mx * (q1q2 + q0q3) + my * (0.5 - q1q1 - q3q3) + mz * (q2q3 - q0q1))
            bx = math.sqrt(hx * hx + hy * hy)
            bz = 2.0 * (mx * (q1q3 - q0q2) + my * (q2q3 + q0q1) + mz * (0.5 - q1q1 - q2q2))
    
            halfwx = bx * (0.5 - q2q2 - q3q3) + bz * (q1q3 - q0q2)
            halfwy = bx * (q1q2 - q0q3) + bz * (q0q1 + q2q3)
            halfwz = bx * (q0q2 + q1q3) + bz * (0.5 - q1q1 - q2q2)
    
            halfex = (my * halfwz - mz * halfwy)
            halfey = (mz * halfwx - mx * halfwz)
            halfez = (mx * halfwy - my * halfwx)

        if (ax != 0.0) and (ay != 0.0) and (az != 0.0):
            recipNorm = self.invSqrt(ax * ax + ay * ay + az * az);
            ax *= recipNorm
            ay *= recipNorm
            az *= recipNorm

            halfvx = q1q3 - q0q2
            halfvy = q0q1 + q2q3
            halfvz = q0q0 - 0.5 + q3q3

            halfex += (ay * halfvz - az * halfvy)
            halfey += (az * halfvx - ax * halfvz)
            halfez += (ax * halfvy - ay * halfvx)

        if (halfex != 0.0) and (halfey != 0.0) and (halfez != 0.0):
            if (self.twoKi > 0.0) :
                self.integralFBx += self.twoKi * halfex * (1.0 / self.sampleFreq)
                self.integralFBy += self.twoKi * halfey * (1.0 / self.sampleFreq)
                self.integralFBz += self.twoKi * halfez * (1.0 / self.sampleFreq)
                gx += self.integralFBx
                gy += self.integralFBy
                gz += self.integralFBz
            else :
                self.integralFBx = 0.0
                self.integralFBy = 0.0
                self.integralFBz = 0.0

            gx += self.twoKp * halfex;
            gy += self.twoKp * halfey;
            gz += self.twoKp * halfez;

        gx *= (0.5 * (1.0 / self.sampleFreq))
        gy *= (0.5 * (1.0 / self.sampleFreq))
        gz *= (0.5 * (1.0 / self.sampleFreq))
        qa = self.q0
        qb = self.q1
        qc = self.q2
        self.q0 += (-qb * gx - qc * gy - self.q3 * gz);
        self.q1 += (qa * gx + qc * gz - self.q3 * gy);
        self.q2 += (qa * gy - qb * gz + self.q3 * gx);
        self.q3 += (qa * gz + qb * gy - qc * gx);

        recipNorm = self.invSqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3);
        self.q0 *= recipNorm;
        self.q1 *= recipNorm;
        self.q2 *= recipNorm;
        self.q3 *= recipNorm;

    def invSqrt(self, number):
        threehalfs = 1.5
        x2 = number * 0.5
        y = number

        packed_y = struct.pack('f', y)
        i = struct.unpack('i', packed_y)[0]  # treat float's bytes as int
        i = 0x5f3759df - (i >> 1)  # arithmetic with magic number
        packed_i = struct.pack('i', i)
        y = struct.unpack('f', packed_i)[0]  # treat int's bytes as float

        y = y * (threehalfs - (x2 * y * y))  # Newton's method
        return y