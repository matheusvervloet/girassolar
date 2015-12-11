import pyupm_grove
import time

relay = pyupm_grove.GroveRelay(6)

while(1):
        relay.off()
        print '0'
        time.sleep(1)
        relay.on()
        print '1'
        time.sleep(1)
