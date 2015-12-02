import pyupm_i2clcd as upmlcd

lcd = upmlcd.Jhd1313m1(0, 0x3E, 0x62)

lcd.serCursor(1,0)

lcd.write('Hello world!')
