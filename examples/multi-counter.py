#!/usr/bin/env python3

# demo will drive multiple MCP23017 devices at different addresses
# see http://quick2wire.com/2012/12/see-the-new-boards-at-work-with-blinken-bars/ for demo


import quick2wire.i2c as i2c
from time import sleep
from itertools import cycle
import sys

iodir_register_b = 0x01 # IODIRB, bank 0
gpio_register_b = 0x13 # GPIOB, bank 0

class PortExpander():
    def __init__(self, bus, address):
        self._bus = bus
        self._address = address

    def write_register(self, reg, b):
        self._bus.transaction(
            i2c.writing_bytes(self._address, reg, b))

    def set_iodir_b(self, b):
        self.write_register(iodir_register_b, b)

    def set_gpio_b(self, b):
        self.write_register(gpio_register_b, b)

offset = int(sys.argv[1]) if len(sys.argv) > 1 else 0
address = 0x20 + offset

with i2c.I2CMaster() as bus:
    pe = PortExpander(bus, address)
    pe.set_iodir_b(0x00)
    pe.set_gpio_b(0x00)
    try:
      for count in cycle(range(256)):
        pe.set_gpio_b(count)
        sleep(0.1)

    finally:
      pe.set_gpio_b(0x00)