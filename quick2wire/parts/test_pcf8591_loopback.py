
from time import sleep
from quick2wire.i2c import I2CMaster
from quick2wire.parts.pcf8591 import PCF8591, FOUR_SINGLE_ENDED
import pytest


# simple test for now - loops back analogue output to analogue input 1
ANALOGUE_IN = 1

@pytest.mark.loopback
@pytest.mark.pcf8591
def test_pcf8591_loopback():
    with I2CMaster() as i2c:
        adc = PCF8591(i2c, FOUR_SINGLE_ENDED)
        input = adc.input(ANALOGUE_IN)
        
        with adc.output as output:
            for i in range(256):
                v = i/255.0
                
                output.value = v
                
                assert abs(input.value - v) < 0.05
