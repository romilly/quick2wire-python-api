__author__ = 'stuartervine'

from quick2wire import i2c
from quick2wire.parts.saa1064 import SAA1064
from quick2wire.parts.seven_segment_display import SevenSegmentDisplay
from time import sleep

saa1064 = SAA1064(i2c.I2CMaster(), digits=2)
saa1064.configure()

#TODO: Write a reset method.

sevenSegmentDisplay=SevenSegmentDisplay(saa1064)
sevenSegmentDisplay.display('1.5')
sleep(1)
sevenSegmentDisplay.display('9R')