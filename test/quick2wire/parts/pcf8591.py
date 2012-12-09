from time import sleep
import pytest
import quick2wire.i2c as i2c
from quick2wire.parts.pcf8591 import PCF8591


# simple test for now - loops back analogue output to analogue input 1
ANALOGUE_IN = 1

@pytest.mark.loopback
@pytest.mark.mcp23017
def test_pcf8591_loopback():
    with i2c.I2CMaster() as master:
        chip = PCF8591(master)
        pin = chip.begin_analogue_read(ANALOGUE_IN)
        for output in range(256):
            chip.analogue_out(output)
            sleep(0.05)
            input = pin.read()
            assert abs(output - input) < 4
