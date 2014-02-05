__author__ = 'stuartervine'

from quick2wire import i2c
from quick2wire.parts.saa1064 import SAA1064
from quick2wire.parts.seven_segment_display import SevenSegmentDisplay
from time import sleep

saa1064 = SAA1064(i2c.I2CMaster(), digits=4)
sevenSegmentDisplay=SevenSegmentDisplay(saa1064)

sevenSegmentDisplay.display('1.5')
sleep(1)
sevenSegmentDisplay.display('100R')
sleep(1)

for i in range(9999):
    sevenSegmentDisplay.display(i)
