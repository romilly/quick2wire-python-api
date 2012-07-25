"""
This is a loopback test which uses the MCP23008 to test the quick2wire.i2c.I2CMaster class.
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
IOPOL=0x01
IOCON = 0x05
GPIO=0x09


def write_register(master, reg, b):
    master.transaction(
        i2c.writing_bytes(address, reg, b))
    
def read_register(master, reg):
    return master.transaction(
        i2c.writing_bytes(address, reg),
        i2c.reading(address, 1))[0][0]

def set_low_bits_as_output(master):
    write_register(master, IODIR, 0xF0)
    
def set_high_bits_as_output(master):
    write_register(master, IODIR, 0x0F)

def set_low_bits(master, bitpattern):
    write_register(master, GPIO, bitpattern & 0x0F)
    
def set_high_bits(master, bitpattern):
    write_register(master, GPIO, (bitpattern << 4) & 0xF0)

def check_low_bits(master, bitpattern):
    assert bitpattern == (read_register(master, GPIO) & 0x0F)

def check_high_bits(master, bitpattern):
    assert bitpattern << 4 == (read_register(master, GPIO) & 0xF0)


@pytest.mark.loopback
def test_mcp23008_loopback_via_i2c_master_api():
    bitpatterns = [(1 << i) for i in range(0,4)]
    
    with i2c.I2CMaster() as master:
        set_low_bits_as_output(master)
        for bitpattern in bitpatterns:
            set_low_bits(master, bitpattern)
            check_high_bits(master, bitpattern)
        
        set_high_bits_as_output(master)
        for bitpattern in bitpatterns:
            set_high_bits(master, bitpattern)
            check_low_bits(master, bitpattern)


@pytest.mark.loopback
def test_mcp23008_multibyte_reads():
    with i2c.I2CMaster() as master:
        # Ensure sequential addressing mode is on
        write_register(master, IOCON, 0x00)
        
        write_register(master, IODIR, 0xFF)
        write_register(master, IOPOL, 0xAA)
        
        # Read two bytes, the IODIR register and, thanks to sequential
        # addressing mode, the next register, IOPOL
        iodir_state, iopol_state = master.transaction(
            i2c.writing_bytes(address, IODIR),
            i2c.reading(address, 2))[0]
    
        assert iodir_state == 0xFF
        assert iopol_state == 0xAA


@pytest.mark.loopback
def test_mcp23008_multibyte_writes():
    with i2c.I2CMaster() as master:
        # Ensure sequential addressing mode is on
        write_register(master, IOCON, 0x00)
        
        # Write two bytes, the IODIR register and, thanks to
        # sequential addressing mode, the next register, IOPOL
        master.transaction(
            i2c.writing_bytes(address, IODIR, 0xFF, 0xAA))
        
        iodir_state = read_register(master, IODIR)
        iopol_state = read_register(master, IOPOL)
        
        assert iodir_state == 0xFF
        assert iopol_state == 0xAA

