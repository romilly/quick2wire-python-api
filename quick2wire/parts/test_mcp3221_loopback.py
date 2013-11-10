"""Loopback attempts for the MCP3221

We do nothing in this test beyond checking that we can connect to the
chip and read a sane value from it.
"""

from quick2wire.i2c import I2CMaster
from quick2wire.parts.mcp3221 import MCP3221
import pytest

from time import sleep

def setup_function(f):
    global i2c
    i2c = I2CMaster()

# Only a very simple test is possible -- do we get a sane value back
# from the chip?
@pytest.mark.loopback
@pytest.mark.mcp3221
def test_mcp3221_loopback_single_ended():
    adc = MCP3221(i2c)
    input = adc.single_ended_input
    v = input.value
    assert v >= 0.0
    assert v < 1.0

def exercise_mcp3221_loopback_single_ended():
    with I2CMaster() as i2c:
        adc = MCP3221(i2c)
        input = adc.single_ended_input

        for i in range(10):
            print("{}: {}".format(i, input.value))
            sleep(1)

#exercise_mcp3221_loopback_single_ended()
