import pyupm_i2clcd as upmlcd
import mraa
import time

//inicializa lcd
lcd = upmlcd.Jhd1313m1(0, 0x3E, 0x62)
//inicializa sensor de luz
lightSensor = mraa.Aio(0)

while(1):
        //faz a leitura do sensor de luz
        lightReading = lightSensor.read()

        //imprime o valor da leitura no lcd
        lcd.setCursor(0, 0)
        lcd.write('Light:' + str(lightReading))

        time.sleep(0.2)
