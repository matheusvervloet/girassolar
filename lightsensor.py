import mraa
import time

while 1:
#Le o valor do light sensor e imprime o valor com um delay de 0.2 segundos
	lightSensor = mraa.Aio(0)
	print (lightSensor.read())
	time.sleep(0.2)	