"""
This is a loopback test which uses the MCP23S17 to test the quick2wire.spi.SPIDevice class.

# For the loopback test, each pin on PORTA is connected to the PORTB pin opposite. Thus,
# GPA0 <-> GPB7
# GPA1 <-> GBP6
# ...
# GPA7 <-> GPB0
# The bit pattern input is therefore the output pattern reflected.

Note: this test does *not* depend on the quick2wire.mcp23s17 module, so that it can be
released independently
"""

from quick2wire.spi import *
import pytest

# MCP23S17 registers using bank=0
IODIRA=0x00
IODIRB=0x01
GPIOA=0x12
GPIOB=0x13
MCP23S17_BASE_ADDRESS = 0x40

ALL_OUTPUTS = 0x00
ALL_INPUTS = 0xFF

bits_out = [(1 << i) for i in range(0,8)]
bits_in = [(1 << (7 - i)) for i in range(0, 8)]
bits = zip(bits_out, bits_in)

address = MCP23S17_BASE_ADDRESS


@pytest.mark.hardware
@pytest.mark.loopback
@pytest.mark.spi
def test_loopback_bits():
    with SPIDevice(0, 0) as mcp23s17:
        prepare_to_send_from_a_to_b(mcp23s17)
        for (port_a, port_b) in bits:
            check_sending_from_a_to_b(mcp23s17, port_a, port_b)
        prepare_to_send_from_b_to_a(mcp23s17)
        for (port_b, port_a) in bits:
            check_sending_from_b_to_a(mcp23s17, port_b, port_a)

def prepare_to_send_from_a_to_b(mcp23s17):
    set_io_direction_a(mcp23s17, ALL_OUTPUTS) # Port A set to output
    set_io_direction_b(mcp23s17, ALL_INPUTS)  # Port B set to input

def check_sending_from_a_to_b(mcp23s17, port_a, port_b):
    write_register(mcp23s17, GPIOA, port_a)
    assert read_register(mcp23s17, GPIOB) == port_b

def prepare_to_send_from_b_to_a(mcp23s17):
    set_io_direction_a(mcp23s17, ALL_INPUTS)  # Port A set to input
    set_io_direction_b(mcp23s17, ALL_OUTPUTS) # Port B set to output

def check_sending_from_b_to_a(mcp23s17, port_b, port_a):
    write_register(mcp23s17, GPIOB, port_b)
    assert read_register(mcp23s17, GPIOA) == port_a

def set_io_direction_a(mcp23s17, b):
    write_register(mcp23s17, IODIRA, b)

def set_io_direction_b(mcp23s17, b):
    write_register(mcp23s17, IODIRB, b)

def write_register(mcp23s17, reg, b):
    mcp23s17.transaction(writing_bytes(address, reg, b))

def read_register(mcp23s17, reg):
    return ord(mcp23s17.transaction(writing_bytes(address+1, reg), reading(1))[0])
