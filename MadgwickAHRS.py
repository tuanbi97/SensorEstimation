import struct
import math
import time


class MadgwickAHRS:

    def __init__(self, withMagnetic = False):
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.beta = 0.1
        self.lastUpdate = -1
        self.invSampleFreq = 0
        self.withMagnetic = withMagnetic
        
    def reset(self):
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.beta = 0.1
        self.lastUpdate = -1
        self.invSampleFreq = 0
        self.withMagnetic = False

    def processingEvent(self, event):
        ax, ay, az = event[0]
        gx, gy, gz = event[1]
        mx, my, mz = event[2]
        if self.lastUpdate == -1:
            self.lastUpdate = event[4]
        self.invSampleFreq = (event[4] - self.lastUpdate) / 1000000000
        self.lastUpdate = event[4]
        if self.withMagnetic == False:
            self.MadgwickAHRSupdateIMU(gx, gy, gz, ax, ay, az)
        else:
            self.MadgwickAHRSupdate(gx, gy, gz, ax, ay, az, mx, my, mz)
        angles = self.Quaternion2YPR()
        return angles

    def Quaternion2YPR(self):

        # roll = math.atan2(2 * (self.q0 * self.q1 + self.q2 * self.q3), self.q0**2 - self.q1**2 - self.q2**2 + self.q3**2)
        # pitch = -math.asin(2 * (self.q1 * self.q3 - self.q0 * self.q2))
        # yaw = math.atan2(2 * (self.q1 * self.q2 + self.q0 * self.q3), self.q0**2 + self.q1**2 - self.q2**2 - self.q3**2)

        roll = math.atan2(2 * (self.q0 * self.q1 + self.q2 * self.q3),
                          2*self.q0 ** 2 - 1 + 2*self.q3 ** 2)
        pitch = -math.asin(2 * (self.q1 * self.q3 - self.q0 * self.q2))
        yaw = math.atan2(2 * (self.q1 * self.q2 + self.q0 * self.q3),
                         2*self.q0 ** 2 + 2*self.q1 ** 2 - 1)

        return [yaw * 180 / math.pi, pitch * 180 / math.pi, roll * 180 / math.pi]

    def MadgwickAHRSupdate(self, gx, gy, gz, ax, ay, az, mx, my, mz):

        qDot1 = 0.5 * (-self.q1 * gx - self.q2 * gy - self.q3 * gz)
        qDot2 = 0.5 * (self.q0 * gx + self.q2 * gz - self.q3 * gy)
        qDot3 = 0.5 * (self.q0 * gy - self.q1 * gz + self.q3 * gx)
        qDot4 = 0.5 * (self.q0 * gz + self.q1 * gy - self.q2 * gx)

        if not ((ax == 0.0) and (ay == 0.0) and (az == 0.0)):

            # Normalise accelerometer measurement
            recipNorm = self.invSqrt( ax * ax + ay * ay + az * az )
            ax *= recipNorm
            ay *= recipNorm
            az *= recipNorm

            # Normalise magnetometer measurement
            recipNorm = self.invSqrt( mx * mx + my * my + mz * mz )
            mx *= recipNorm
            my *= recipNorm
            mz *= recipNorm

            # Auxiliary variables to avoid repeated arithmetic
            _2q0mx = 2.0 * self.q0 * mx
            _2q0my = 2.0 * self.q0 * my
            _2q0mz = 2.0 * self.q0 * mz
            _2q1mx = 2.0 * self.q1 * mx
            _2q0 = 2.0 * self.q0
            _2q1 = 2.0 * self.q1
            _2q2 = 2.0 * self.q2
            _2q3 = 2.0 * self.q3
            _2q0q2 = 2.0 * self.q0 * self.q2
            _2q2q3 = 2.0 * self.q2 * self.q3
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

            # Reference direction of Earth's magnetic field
            hx = mx * q0q0 - _2q0my * self.q3 + _2q0mz * self.q2 + mx * q1q1 + _2q1 * my * self.q2 + _2q1 * mz * self.q3 - mx * q2q2 - mx * q3q3
            hy = _2q0mx * self.q3 + my * q0q0 - _2q0mz * self.q1 + _2q1mx * self.q2 - my * q1q1 + my * q2q2 + _2q2 * mz * self.q3 - my * q3q3
            _2bx = math.sqrt(hx * hx + hy * hy)
            _2bz = -_2q0mx * self.q2 + _2q0my * self.q1 + mz * q0q0 + _2q1mx * self.q3 - mz * q1q1 + _2q2 * my * self.q3 - mz * q2q2 + mz * q3q3
            _4bx = 2.0 * _2bx
            _4bz = 2.0 * _2bz

            # Gradient decent algorithm corrective step
            s0 = -_2q2 * (2.0 * q1q3 - _2q0q2 - ax) + _2q1 * (2.0 * q0q1 + _2q2q3 - ay) - _2bz * self.q2 * (_2bx * (0.5 - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mx) + (-_2bx * self.q3 + _2bz * self.q1) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - my) + _2bx * self.q2 * (_2bx * (q0q2 + q1q3) + _2bz * (0.5 - q1q1 - q2q2) - mz)
            s1 = _2q3 * (2.0 * q1q3 - _2q0q2 - ax) + _2q0 * (2.0 * q0q1 + _2q2q3 - ay) - 4.0 * self.q1 * (1 - 2.0 * q1q1 - 2.0 * q2q2 - az) + _2bz * self.q3 * (_2bx * (0.5 - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mx) + (_2bx * self.q2 + _2bz * self.q0) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - my) + (_2bx * self.q3 - _4bz * self.q1) * (_2bx * (q0q2 + q1q3) + _2bz * (0.5 - q1q1 - q2q2) - mz)
            s2 = -_2q0 * (2.0 * q1q3 - _2q0q2 - ax) + _2q3 * (2.0 * q0q1 + _2q2q3 - ay) - 4.0 * self.q2 * (1 - 2.0 * q1q1 - 2.0 * q2q2 - az) + (-_4bx * self.q2 - _2bz * self.q0) * (_2bx * (0.5 - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mx) + (_2bx * self.q1 + _2bz * self.q3) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - my) + (_2bx * self.q0 - _4bz * self.q2) * (_2bx * (q0q2 + q1q3) + _2bz * (0.5 - q1q1 - q2q2) - mz)
            s3 = _2q1 * (2.0 * q1q3 - _2q0q2 - ax) + _2q2 * (2.0 * q0q1 + _2q2q3 - ay) + (-_4bx * self.q3 + _2bz * self.q1) * (_2bx * (0.5 - q2q2 - q3q3) + _2bz * (q1q3 - q0q2) - mx) + (-_2bx * self.q0 + _2bz * self.q2) * (_2bx * (q1q2 - q0q3) + _2bz * (q0q1 + q2q3) - my) + _2bx * self.q1 * (_2bx * (q0q2 + q1q3) + _2bz * (0.5 - q1q1 - q2q2) - mz)
            recipNorm = self.invSqrt(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3)
            s0 *= recipNorm
            s1 *= recipNorm
            s2 *= recipNorm
            s3 *= recipNorm

            qDot1 -= self.beta * s0
            qDot2 -= self.beta * s1
            qDot3 -= self.beta * s2
            qDot4 -= self.beta * s3

        self.q0 += qDot1 * self.invSampleFreq
        self.q1 += qDot2 * self.invSampleFreq
        self.q2 += qDot3 * self.invSampleFreq
        self.q3 += qDot4 * self.invSampleFreq

        recipNorm = self.invSqrt(self.q0 * self.q0 + self.q1 * self.q1 + self.q2 * self.q2 + self.q3 * self.q3)
        self.q0 *= recipNorm
        self.q1 *= recipNorm
        self.q2 *= recipNorm
        self.q3 *= recipNorm

    def MadgwickAHRSupdateIMU(self, gx, gy, gz, ax, ay, az):

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
        self.q0 += qDot1 * self.invSampleFreq
        self.q1 += qDot2 * self.invSampleFreq
        self.q2 += qDot3 * self.invSampleFreq
        self.q3 += qDot4 * self.invSampleFreq

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

