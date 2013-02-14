from quick2wire.i2c import I2CMaster
from quick2wire.gpio import pins, In, Out, I2C_INTERRUPT
from quick2wire.parts.mcp23017 import MCP23017, deferred_read
from quick2wire.parts.test_mcp23017_loopback import Topology, inverse
import pytest



@pytest.mark.loopback
@pytest.mark.mcp23017
@pytest.mark.gpio
def test_mcp23017_interrupts():
    i2c_int = pins.pin(I2C_INTERRUPT, direction=In)
    
    with i2c_int, I2CMaster() as i2c:
        chip = MCP23017(i2c)
        chip.reset(interrupt_polarity=1)
        
        check_interrupts(chip, i2c_int, Topology)
        check_interrupts(chip, i2c_int, inverse(Topology))



def check_interrupts(chip, int_pin, topology):
    for (outb, outp), (inb, inp) in topology:
        outbank = chip.bank(outb)
        outpin = outbank.pin(outp)
        
        inbank = chip.bank(inb)
        inpin = inbank.pin(inp)
        
        inbank.read_mode = deferred_read
        
        with outpin, inpin:
            outpin.direction = Out
            inpin.direction = In
            inpin.enable_interrupts()
            
            for v in [1,0,1,0]:
                outpin.value = v
                
                assert int_pin.value == 1
                
                inbank.read()
                
                assert int_pin.value == 0
                assert inpin.value == v
                
