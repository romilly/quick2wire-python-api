from quick2wire import i2c
from quick2wire.parts.saa1064 import SAA1064
from quick2wire.parts.seven_segment_display import SevenSegmentDisplay

__author__ = 'stuartervine'

saa1064 = SAA1064(i2c.I2CMaster(), digits=2)
saa1064.configure()

SevenSegmentDisplay(saa1064).display('1.5')
