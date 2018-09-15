import struct
import math
import time


class MahonyAHRS:

    def __init__(self, withMagnetic = False):
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.twoKp = 2.0 * 0.5
        self.twoKi = 2.0 * 0.0
        self.integralFBx = 0.0
        self.integralFBy = 0.0
        self.integralFBz = 0.0
        self.lastUpdate = -1
        self.invSampleFreq = 0
        self.withMagnetic = withMagnetic

    def processingEvent(self, event):
        ax, ay, az = event[0]
        gx, gy, gz = event[1]
        mx, my, mz = event[2]
        if self.lastUpdate == -1:
            self.lastUpdate = event[4]
            return
        self.invSampleFreq = event[4] - self.lastUpdate
        self.lastUpdate = event[4]
        if (self.withMagnetic):
            self.MahonyAHRSupdate(gx, gy, gz, ax, ay, az, mx, my, mz)
        else:
            self.MahonyAHRSupdateIMU(gx, gy, gz, ax, ay, az)
        angles = self.Quaternion2YPR()
        return angles

    def Quaternion2YPR(self):

        roll = math.atan2(2 * (self.q0 * self.q1 + self.q2 * self.q3), self.q0**2 - self.q1**2 - self.q2**2 + self.q3**2)
        pitch = -math.asin(2 * (self.q1 * self.q3 - self.q0 * self.q2))
        yaw = math.atan2(2 * (self.q1 * self.q2 + self.q0 * self.q3), self.q0**2 + self.q1**2 - self.q2**2 - self.q3**2)

        return [yaw * 180 / math.pi, pitch * 180 / math.pi, roll * 180 / math.pi]

    def MahonyAHRSupdate(self, gx, gy, gz, ax, ay, az, mx, my, mz):

        if not ((ax == 0.0) and (ay == 0.0) and (az == 0.0)):

            recipNorm = self.invSqrt(ax * ax + ay * ay + az * az)
            ax *= recipNorm
            ay *= recipNorm
            az *= recipNorm

            recipNorm = self.invSqrt(mx * mx + my * my + mz * mz)
            mx *= recipNorm
            my *= recipNorm
            mz *= recipNorm

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

            hx = 2.0 * (mx * (0.5 - q2q2 - q3q3) + my * (q1q2 - q0q3) + mz * (q1q3 + q0q2))
            hy = 2.0 * (mx * (q1q2 + q0q3) + my * (0.5 - q1q1 - q3q3) + mz * (q2q3 - q0q1))
            bx = math.sqrt(hx * hx + hy * hy)
            bz = 2.0 * (mx * (q1q3 - q0q2) + my * (q2q3 + q0q1) + mz * (0.5 - q1q1 - q2q2))

            halfvx = q1q3 - q0q2
            halfvy = q0q1 + q2q3
            halfvz = q0q0 - 0.5 + q3q3
            halfwx = bx * (0.5 - q2q2 - q3q3) + bz * (q1q3 - q0q2)
            halfwy = bx * (q1q2 - q0q3) + bz * (q0q1 + q2q3)
            halfwz = bx * (q0q2 + q1q3) + bz * (0.5 - q1q1 - q2q2)

            halfex = (ay * halfvz - az * halfvy) + (my * halfwz - mz * halfwy)
            halfey = (az * halfvx - ax * halfvz) + (mz * halfwx - mx * halfwz)
            halfez = (ax * halfvy - ay * halfvx) + (mx * halfwy - my * halfwx)

            if (self.twoKi > 0.0):
                self.integralFBx += self.twoKi * halfex * (1.0 / self.sampleFreq)
                self.integralFBy += self.twoKi * halfey * (1.0 / self.sampleFreq)
                self.integralFBz += self.twoKi * halfez * (1.0 / self.sampleFreq)
                gx += self.integralFBx
                gy += self.integralFBy
                gz += self.integralFBz
            else:
                self.integralFBx = 0.0
                self.integralFBy = 0.0
                self.integralFBz = 0.0

            gx += self.twoKp * halfex
            gy += self.twoKp * halfey
            gz += self.twoKp * halfez

        gx *= (0.5 * (1.0 / self.sampleFreq))
        gy *= (0.5 * (1.0 / self.sampleFreq))
        gz *= (0.5 * (1.0 / self.sampleFreq))
        qa = self.q0
        qb = self.q1
        qc = self.q2
        self.q0 += (-qb * gx - qc * gy - self.q3 * gz)
        self.q1 += (qa * gx + qc * gz - self.q3 * gy)
        self.q2 += (qa * gy - qb * gz + self.q3 * gx)
        self.q3 += (qa * gz + qb * gy - qc * gx)

        recipNorm = self.invSqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3)
        self.q0 *= recipNorm
        self.q1 *= recipNorm
        self.q2 *= recipNorm
        self.q3 *= recipNorm

    def MahonyAHRSupdateIMU(self, gx, gy, gz, ax, ay, az):

        if not ((ax == 0.0) and (ay == 0.0) and (az == 0.0)) :

            recipNorm = self.invSqrt(ax * ax + ay * ay + az * az)
            ax *= recipNorm
            ay *= recipNorm
            az *= recipNorm

            halfvx = self.q1 * self.q3 - self.q0 * self.q2
            halfvy = self.q0 * self.q1 + self.q2 * self.q3
            halfvz = self.q0 * self.q0 - 0.5 + self.q3 * self.q3

            halfex = (ay * halfvz - az * halfvy)
            halfey = (az * halfvx - ax * halfvz)
            halfez = (ax * halfvy - ay * halfvx)

            if self.twoKi > 0.0 :
                self.integralFBx += self.twoKi * halfex * self.invSampleFreq
                self.integralFBy += self.twoKi * halfey * self.invSampleFreq
                self.integralFBz += self.twoKi * halfez * self.invSampleFreq
                gx += self.integralFBx
                gy += self.integralFBy
                gz += self.integralFBz
            else:
                integralFBx = 0.0
                integralFBy = 0.0
                integralFBz = 0.0

            gx += self.twoKp * halfex
            gy += self.twoKp * halfey
            gz += self.twoKp * halfez

        gx *= (0.5 * self.invSampleFreq)
        gy *= (0.5 * self.invSampleFreq)
        gz *= (0.5 * self.invSampleFreq)
        qa = self.q0
        qb = self.q1
        qc = self.q2
        self.q0 += (-qb * gx - qc * gy - self.q3 * gz)
        self.q1 += (qa * gx + qc * gz - self.q3 * gy)
        self.q2 += (qa * gy - qb * gz + self.q3 * gx)
        self.q3 += (qa * gz + qb * gy - qc * gx)

        recipNorm = self.invSqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3)
        self.q0 *= recipNorm
        self.q1 *= recipNorm
        self.q2 *= recipNorm
        self.q3 *= recipNorm

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

