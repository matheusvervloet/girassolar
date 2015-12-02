import pyupm_servo as upmservo
import time

servo = upmservo.ES08A(3)

print servo.getMaxPulseWidth()
print servo.getMinPulseWidth()
print servo.getPeriod()

while(1):
        servo.setAngle(90)
        time.sleep(3)

        servo.setAngle(130)
        time.sleep(3)

        servo.setAngle(90)
        time.sleep(3)
