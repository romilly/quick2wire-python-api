
import quick2wire.i2c as i2c
from quick2wire.parts.mcp23x17 import *
from quick2wire.parts.mcp23017 import Registers as MCP23017Registers, MCP23017
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
        check_connectivity_via_registers(chip, Topology)
        
        chip.reset()
        check_connectivity_via_registers(chip, inverse(Topology))


def check_connectivity_via_registers(chip, topology):
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


@pytest.mark.loopback
@pytest.mark.mcp23017
def test_mcp23017_loopback_via_pins():
    with i2c.I2CMaster() as master:
        chip = MCP23017(master, 0x20)
        
        chip.reset()
        check_connectivity_via_pins(chip, Topology)
        
        chip.reset()
        check_connectivity_via_pins(chip, inverse(Topology))


def check_connectivity_via_pins(chip, topology):
    for (outb, outp), (inb, inp) in topology:
        with chip[outb][outp] as outpin, chip[inb][inp] as inpin:
            outpin.direction = Out
            inpin.direction = In
            
            for v in [0,1,0,1]:
                outpin.value = v
                assert inpin.value == v
