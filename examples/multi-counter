#!/usr/bin/env python3

# demo will drive multiple MCP23017 devices at different addresses
# see http://quick2wire.com/2012/12/see-the-new-boards-at-work-with-blinken-bars/ for demo


from time import sleep
from itertools import cycle
import sys

import quick2wire.i2c as i2c
from quick2wire.parts.mcp23017 import Registers as MCP23017Registers
from quick2wire.parts.mcp23x17 import IODIRB, GPIO


offset = int(sys.argv[1]) if len(sys.argv) > 1 else 0
address = 0x20 + offset

with i2c.I2CMaster() as bus:
    chip = MCP23017Registers(bus, address)
    chip.reset()
    chip.write_register(IODIRB, 0x00)

    try:
        for count in cycle(range(256)):
            chip.write_banked_register(1, GPIO, count)
            sleep(0.1)
    finally:
        chip.reset()
