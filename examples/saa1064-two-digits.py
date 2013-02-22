import quick2wire.i2c as i2c
from quick2wire.parts.saa1064 import SAA1064, STATIC_MODE
from time import sleep

saa1064 = SAA1064(i2c.I2CMaster(), digits=2)
saa1064.mode=STATIC_MODE
saa1064.brightness=0b01100000
saa1064.configure()

for y in range(10):
        saa1064.digit(0).value(y)
        for x in range(10):
                saa1064.digit(1).value(x)
                saa1064.write()
                sleep(0.1)