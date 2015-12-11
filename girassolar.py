import mraa
import time

import sys, signal, atexit

import pyupm_i2clcd as upmlcd

import pyupm_grove

import pyupm_uln200xa as upmstepper
DIR_CW = upmstepper.ULN200XA.DIR_CW
DIR_CCW = upmstepper.ULN200XA.DIR_CCW

lcd = upmlcd.Jhd1313m1(0, 0x3E, 0x62)
lcd.setColor(0, 0, 0)

relay = pyupm_grove.GroveRelay(6)

lightSensor = mraa.Aio(3)

solarPanel = mraa.Aio(0)

def buttonISR(arg):
        global mode
        if(mode == 0):
                mode = 1
        else:
                mode = 0

mode = 0
button = mraa.Gpio(4)
button.dir(mraa.DIR_IN)
button.isr(mraa.EDGE_FALLING, buttonISR, buttonISR)

stepper = upmstepper.ULN200XA(96, 8, 9, 10, 11)
stepper.setSpeed(30) #30 rpm

position = 0

# Register exit handlers

# This lets you run code on exit
def exitHandler():
        stepper.release()
        print "Exiting"
        sys.exit(0)
atexit.register(exitHandler)

def writeLcd(text, line):
        lcd.setCursor(line, 0)
        lcd.write(text)

def step(steps):
        global position
        writeData('position.data', position)
        if(position < 15 and steps >= 0):
                stepper.setDirection(DIR_CW)
                stepper.stepperSteps(steps)
                position += steps
                time.sleep(0.2)
        elif(position > -15 and steps < 0):
                stepper.setDirection(DIR_CCW)
                stepper.stepperSteps(-steps)
                position += steps
                time.sleep(0.2)
        else:
            print 'Reached maximum steps (' + str(position) + ').'

def readPanel():
        reading = round(solarPanel.read()/205.0, 2)
        writeLcd('Panel: ' + str(reading) + 'V ', 1)
        writeData('panel.data', reading)
        return reading

def readLight():
        reading = lightSensor.read()
        writeLcd('Light: ' + str(reading), 0)
        writeData('light.data', reading)
        readPanel()
        return reading

def standby():
        global relay, lcd, stepper
        writeData('status.data', 'off')
        relay.off()
        lcd.clear()
        lcd.setColor(0, 0, 0)
        step(-position)
        stepper.release()


def activate():
        global relay, lcd
        writeData('status.data', 'on')
        relay.on()
        lcd.setColor(255, 255, 255)

def writeData(filename, data):
        f = open(filename, 'w')
        f.write(str(data))
        f.close()

while(1):
        if(mode == 0):
                standby()
                while(mode == 0):
                        time.sleep(0.1)

        activate()
        firstValue = readLight()

        # enquanto a leitura do sensor de luz nao variar, ficamos parados
        reading = readLight()
        while(reading > firstValue - 5 and reading < firstValue + 5 and mode == 1 ):
            reading = readLight()
            time.sleep(0.5)


        # busca a posicao da luz
        stable = False
        while(not stable and mode == 1):
            reading = readLight()

            step(3)
            clockReading = readLight()
            step(-6)
            counterReading = readLight()

            if(clockReading > reading + 3):
                step(6)
            elif(counterReading < reading + 3):
                step(3)
                stable = True
