import quick2wire.i2c as i2c
from quick2wire.parts.mcp23017 import Registers as MCP23017Registers, MCP23017
from quick2wire.parts.mcp23017 import deferred_read, deferred_write, In, Out
from quick2wire.parts.mcp23x17 import IODIRA, IODIRB, GPIO
import pytest



# Simplest test - pins of bank 0 connected to corresponding pin of bank 1
Topology = [((0,i), (1,i)) for i in range(8)]

def inverse(topology):
    return [(b,a) for (a,b) in topology]

def bit(n):
    return 1 << n
    

def check_mcp23017_loopback(chip_class, checker):
    with i2c.I2CMaster() as master:
        chip = chip_class(master, 0x20)        
        
        chip.reset()
        checker(chip, Topology)
        
        chip.reset()
        checker(chip, inverse(Topology))


@pytest.mark.loopback
@pytest.mark.mcp23017
def test_loopback_via_registers():
    check_mcp23017_loopback(MCP23017Registers, check_connectivity_via_registers)


@pytest.mark.loopback
@pytest.mark.mcp23017
def test_loopback_via_pins():
    check_mcp23017_loopback(MCP23017, check_connectivity_via_pins)


@pytest.mark.loopback
@pytest.mark.mcp23017
def test_loopback_via_pins_deferred():
    check_mcp23017_loopback(MCP23017, check_connectivity_via_pins_deferred)



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


def check_connectivity_via_pins(chip, topology):
    for (outb, outp), (inb, inp) in topology:
        with chip[outb][outp] as outpin, chip[inb][inp] as inpin:
            outpin.direction = Out
            inpin.direction = In
            
            for v in [1,0,1,0]:
                outpin.value = v
                assert inpin.value == v



def check_connectivity_via_pins_deferred(chip, topology):
    for (outb, outp), (inb, inp) in topology:
        chip.reset()
        
        with chip[outb][outp] as outpin, chip[inb][inp] as inpin:
            inpin.direction = In
            outpin.direction = Out
            
            chip[outb].write_mode = deferred_write
            chip[inb].read_mode = deferred_read
            
            for v in [1,0,1,0]:
                outpin.value = v
                
                assert inpin.value != v
                
                outpin.bank.write()
                assert inpin.value != v
                
                inpin.bank.read()
                assert inpin.value == v
                
