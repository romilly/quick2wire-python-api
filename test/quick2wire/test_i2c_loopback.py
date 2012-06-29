"""
This is a loopback test which uses the MCP23008 to test the quick2wire.i2c.I2CBus class.
The MCP23008 has eight GPIO pins called GP0 to GP7
for details, see the datasheet at http://ww1.microchip.com/downloads/en/DeviceDoc/21919d.pdf
Connect the GPIO pins in pairs as follows:
GP0 <-> GP4
GP1 <-> GP5
GP2 <-> GP6
GP3 <-> GP7

Note: this test does *not* depend on the quick2wire.mcp23008 module, so that it can be
released independently
"""

import quick2wire.i2c as i2c
import pytest

address = 0x20

# Registers
IODIR=0x00
GPIO=0x09


def write_register(bus, reg, b):
    bus.transaction(
        i2c.write_bytes(address, reg, b))
    
def read_register(bus, reg):
    return bus.transaction(
        i2c.write_bytes(address, reg),
        i2c.read(address, 1))[0][0]

def set_low_bits_as_output(bus):
    write_register(bus, IODIR, 0xF0)
    
def set_high_bits_as_output(bus):
    write_register(bus, IODIR, 0x0F)

def set_low_bits(bus, bitpattern):
    write_register(bus, GPIO, bitpattern & 0x0F)
    
def set_high_bits(bus, bitpattern):
    write_register(bus, GPIO, (bitpattern << 4) & 0xF0)

def check_low_bits(bus, bitpattern):
    assert bitpattern == (read_register(bus, GPIO) & 0x0F)

def check_high_bits(bus, bitpattern):
    assert bitpattern << 4 == (read_register(bus, GPIO) & 0xF0)


@pytest.mark.loopback
def test_mcp23008_loopback_via_i2c_bus_api():
    bitpatterns = [(1 << i) for i in range(0,4)]
    
    with i2c.I2CBus() as bus:
        set_low_bits_as_output(bus)
        for bitpattern in bitpatterns:
            set_low_bits(bus, bitpattern)
            check_high_bits(bus, bitpattern)
        
        set_high_bits_as_output(bus)
        for bitpattern in bitpatterns:
            set_high_bits(bus, bitpattern)
            check_low_bits(bus, bitpattern)
