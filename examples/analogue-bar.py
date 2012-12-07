from time import sleep
from contextlib import closing
from quick2wire.gpio import Pin
import quick2wire.i2c as i2c

from quick2wire.parts.pcf8591 import PCF8591

ANALOGUE_IN = 0

def display(pins, value):
    for count in range(8):
        pins[count].value = 1 if value < 8 * count else 0

with closing(i2c.I2CMaster()) as master:
    pcf = PCF8591(master)
    pins = [Pin(header_pin_number, Pin.Out) for header_pin_number in [11, 12, 13, 15, 16, 18, 22, 7]]
    pin = pcf.begin_analogue_read(ANALOGUE_IN)
    while(True):
        display(pins, pin.read())

