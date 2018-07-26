import struct
import math
import time


class MadgwickAHRS:

    def __init__(self):
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.beta = 0.1
        self.lastUpdate = time.clock()

    def processingEvent(self, event):
        ax, ay, az = event[0]
        gx, gy, gz = event[1]
        self.MadgwickAHRSupdateIMU(gx, gy, gz, ax, ay, az)
        angles = self.Quaternion2YPR()
        return angles

    def Quaternion2YPR(self):

        roll = math.atan2(2 * (self.q0 * self.q1 + self.q2 * self.q3), self.q0**2 - self.q1**2 - self.q2**2 + self.q3**2)
        pitch = -math.asin(2 * (self.q1 * self.q3 - self.q0 * self.q2))
        yaw = math.atan2(2 * (self.q1 * self.q2 + self.q0 * self.q3), self.q0**2 + self.q1**2 - self.q2**2 - self.q3**2)

        return [yaw * 180 / math.pi, pitch * 180 / math.pi, roll * 180 / math.pi]

    def MadgwickAHRSupdateIMU(self, gx, gy, gz, ax, ay, az):

        t = time.clock()
        sampleFreq = 1 / (t-self.lastUpdate)
        self.lastUpdate = t

        # Rate of change of quaternion from gyroscope
        qDot1 = 0.5 * (-self.q1 * gx - self.q2 * gy - self.q3 * gz)
        qDot2 = 0.5 * (self.q0 * gx + self.q2 * gz - self.q3 * gy)
        qDot3 = 0.5 * (self.q0 * gy - self.q1 * gz + self.q3 * gx)
        qDot4 = 0.5 * (self.q0 * gz + self.q1 * gy - self.q2 * gx)


        # Compute feedback only if accelerometer measurement valid (avoids NaN in accelerometer normalisation)
        if not ((ax == 0.0) and (ay == 0.0) and (az == 0.0)):

            # Normalise accelerometer measurement

            recipNorm = self.invSqrt(ax * ax + ay * ay + az * az)
            ax1 = ax*recipNorm
            ay1 = ay*recipNorm
            az1 = az*recipNorm

            # Auxiliary variables to avoid repeated arithmetic
            _2q0 = 2.0 * self.q0
            _2q1 = 2.0 * self.q1
            _2q2 = 2.0 * self.q2
            _2q3 = 2.0 * self.q3
            _4q0 = 4.0 * self.q0
            _4q1 = 4.0 * self.q1
            _4q2 = 4.0 * self.q2
            _8q1 = 8.0 * self.q1
            _8q2 = 8.0 * self.q2
            q0q0 = self.q0 * self.q0
            q1q1 = self.q1 * self.q1
            q2q2 = self.q2 * self.q2
            q3q3 = self.q3 * self.q3

            # Gradient decent algorithm corrective step

            s0 = (_4q0 * q2q2) + (_2q2 * ax1) + (_4q0 * q1q1) -( _2q1 * ay1)
            s1 = _4q1 * q3q3 - _2q3 * ax1 + 4.0 * q0q0 * self.q1 -( _2q0 * ay1) - _4q1 + (_8q1 * q1q1) +( _8q1 * q2q2) +( _4q1 * az1)
            s2 = (4.0 * q0q0* self.q2) + _2q0 * ax1 + _4q2 * q3q3 -( _2q3 * ay1) - _4q2 + (_8q2 * q1q1) + (_8q2 * q2q2) +( _4q2 * az1)
            s3 = (4.0 * q1q1* self.q3)- _2q1 * ax1 + 4.0 * q2q2 * self.q3 - _2q2 * ay1
            recipNorm = self.invSqrt(s0**2+s1**2+s2**2+s3**2) # normalise step magnitude
            s0a = s0*recipNorm
            s1a = s1*recipNorm
            s2a = s2*recipNorm
            s3a = s3*recipNorm

            # Apply feedback step
            qDot1 -= self.beta * s0a
            qDot2 -= self.beta * s1a
            qDot3 -= self.beta * s2a
            qDot4 -= self.beta * s3a

        # Integrate rate of change of quaternion to yield quaternion
        self.q0 += qDot1 *(1.0 / sampleFreq)
        self.q1 += qDot2 *(1.0 / sampleFreq)
        self.q2 += qDot3 * (1.0 / sampleFreq)
        self.q3 += qDot4 * (1.0 / sampleFreq)

        # Normalise quaternion
        recipNorm = self.invSqrt(self.q0**2+self.q1**2+self.q2**2+self.q3**2)

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

