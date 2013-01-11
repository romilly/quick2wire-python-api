from contextlib import closing
from quick2wire.gpio import Pin
from quick2wire.helpers.display import AnalogueDisplay
import quick2wire.i2c as i2c
from quick2wire.parts.pcf8591 import PCF8591

with closing(i2c.I2CMaster()) as master:
    pcf = PCF8591(master)
    pins = [Pin(header_pin_number, Pin.Out) for header_pin_number in [11, 12, 13, 15, 16, 18, 22, 7]]
    display = AnalogueDisplay(64, *pins)
    pin = pcf.begin_analogue_read(0)
    while(True):
        display.display(pin.read())

