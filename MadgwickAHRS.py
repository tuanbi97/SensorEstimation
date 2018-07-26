class MadgwickAHRS:

    def __init__(self):
        self.q0 = 1.0
        self.q1 = 0.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.beta = 1.0

    def MadgwickAHRSupdateIMU(self, gx, gy, gz, ax, ay, az):

        sampleFreq = 50.0

        float recipNorm;
        float s0, s1, s2, s3;
        float s0a, s1a, s2a, s3a;
        float az1,ay1,ax1;
        float qDot1, qDot2, qDot3, qDot4;
        float _2q0, _2q1, _2q2, _2q3, _4q0, _4q1, _4q2 ,_8q1, _8q2, q0q0, q1q1, q2q2, q3q3;

        # Rate of change of quaternion from gyroscope
        qDot1 = 0.5 * (-self.q1 * gx - self.q2 * gy - self.q3 * gz)
        qDot2 = 0.5 * (self.q0 * gx + self.q2 * gz - self.q3 * gy)
        qDot3 = 0.5 * (self.q0 * gy - self.q1 * gz + self.q3 * gx)
        qDot4 = 0.5 * (self.q0 * gz + self.q1 * gy - self.q2 * gx)


        # Compute feedback only if accelerometer measurement valid (avoids NaN in accelerometer normalisation)
        if not ((ax == 0.0) and (ay == 0.0) and (az == 0.0)):

            # Normalise accelerometer measurement

            recipNorm = invSqrt(ax * ax + ay * ay + az * az);
            ax1 = ax*recipNorm;
            ay1 = ay*recipNorm;
            az1 = az*recipNorm;

            # Auxiliary variables to avoid repeated arithmetic
            _2q0 = 2.0 * self.q0;
            _2q1 = 2.0 * self.q1;
            _2q2 = 2.0 * self.q2;
            _2q3 = 2.0 * self.q3;
            _4q0 = 4.0 * self.q0;
            _4q1 = 4.0 * self.q1;
            _4q2 = 4.0 * self.q2;
            _8q1 = 8.0 * self.q1;
            _8q2 = 8.0 * self.q2;

            # Gradient decent algorithm corrective step

            s0 = (_4q0 * self.q2**2) + (_2q2 * ax1) + (_4q0 * self.q1**2) -( _2q1 * ay1);
            s1 = _4q1 * self.q3**2 - _2q3 * ax1 + 4.0 * self.q0**2 * self.q1 -( _2q0 * ay1) - _4q1 + (_8q1 * self.q1**2) +( _8q1 * self.q2**2) +( _4q1 * az1);
            s2 = (4.0 * self.q0**2* self.q2) + _2q0 * ax1 + _4q2 * self.q3**2 -( _2q3 * ay1) - _4q2 + (_8q2 * self.q1**2) + (_8q2 * self.q2**2) +( _4q2 * az1);
            s3 = (4.0 * self.q1**2* self.q3)- _2q1 * ax1 + 4.0 * self.q2**2 * self.q3 - _2q2 * ay1;
            recipNorm = self.invSqrt(s0**2+s1**2+s2**2+s3**2) # normalise step magnitude
            s0a = s0*recipNorm;
            s1a = s1*recipNorm;
            s2a = s2*recipNorm;
            s3a = s3*recipNorm;

            # Apply feedback step
            qDot1 -= self.beta * s0a;
            qDot2 -= self.beta * s1a;
            qDot3 -= self.beta * s2a;
            qDot4 -= self.beta * s3a;

        # Integrate rate of change of quaternion to yield quaternion
        self.q0 += qDot1 *(1.0 / sampleFreq)
        self.q1 += qDot2 *(1.0 / sampleFreq)
        self.q2 += qDot3 * (1.0 / sampleFreq)
        self.q3 += qDot4 * (1.0 / sampleFreq)

        # Normalise quaternion
        qp01=self.q0**2+self.q1**2
        qp23=self.q2**2+self.q3**2
        recipNorm = self.invSqrt(qp01+qp23)

        q0x = self.q0*recipNorm;
        q1x = self.q1*recipNorm;
        q2x = self.q2*recipNorm;
        q3x = self.q3*recipNorm;
