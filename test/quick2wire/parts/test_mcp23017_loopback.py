
import quick2wire.i2c as i2c
from quick2wire.parts.mcp23x17 import *
from quick2wire.parts.mcp23017 import Registers as MCP23017Registers
import pytest



# Simplest test - pins of bank 0 connected to corresponding pin of bank 1
Topology = [((0,i), (1,i)) for i in range(8)]

def inverse(topology):
    return [(b,a) for (a,b) in topology]

def bit(n):
    return 1 << n

@pytest.mark.loopback
@pytest.mark.mcp23017
def test_mcp23017_loopback_via_registers():
    with i2c.I2CMaster() as master:
        chip = MCP23017Registers(master, 0x20)
        
        chip.reset()
        check_connectivity(chip, Topology)
        
        chip.reset()
        check_connectivity(chip, inverse(Topology))


def check_connectivity(chip, topology):
    iodira, iodirb = iodir_values(topology)
    
    chip.write_register(IODIRA, iodira)
    chip.write_register(IODIRB, iodirb)
    
    for (outbank, outpin), (inbank, inpin) in topology:
        chip.write_banked_register(outbank, GPIO, bit(outpin))
        assert chip.read_banked_register(inbank, GPIO) == bit(inpin)


def iodir_values(topology):
    iodirs = [0xFF,0xFF]
    for (bank1, pin1), (bank2, pin2) in topology:
        iodirs[bank1] &= ~bit(pin1)
    return iodirs
