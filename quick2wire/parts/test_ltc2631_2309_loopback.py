"""Loopback tests for the LTC2631 DAC and LTC2309 ADC

Requires 1x LTC2309 and 1x LTC2631

Topology:

  * connect 2631 GND to 2309 CH3
  * connect 2631 Vout to 2309 CH2

You may need to adjust the DAC_ADDRESS, DAC_VARIANT and ADC_ADDRESS
constants below, depending on the chips available.
  
"""

from quick2wire.i2c import I2CMaster
from quick2wire.parts.ltc2631 import LTC2631
from quick2wire.parts.ltc2309 import LTC2309
import pytest

DAC_ADDRESS = 0x10 # LTC2631
DAC_VARIANT = 'HZ12'
ADC_ADDRESS = 0x08 # LTC2309

from time import sleep

def setup_function(f):
    global i2c
    i2c = I2CMaster()

def teardown_function(f):
    i2c.close()

def assert_is_approx(expected, actual, delta=0.02):
    assert abs(actual - expected) <= delta


####

#setup_function(0)

@pytest.mark.loopback
@pytest.mark.ltc2309
@pytest.mark.ltc2631
def test_single_channel():
    adc = LTC2309(i2c, address=ADC_ADDRESS)
    dac = LTC2631(i2c, DAC_VARIANT, address=DAC_ADDRESS)

    with dac.output as out0, adc.single_ended_input(2) as in2, adc.single_ended_input(3) as in3:
        nvals = 10
        for v in (i*3.0/nvals for i in range(nvals)):
            print('v={}'.format(v))
            out0.value = v
            assert_is_approx(v, in2.value)
            assert_is_approx(0.0, in3.value)

@pytest.mark.loopback
@pytest.mark.ltc2309
@pytest.mark.ltc2631
def test_differential_channel():
    adc = LTC2309(i2c, address=ADC_ADDRESS)
    dac = LTC2631(i2c, DAC_VARIANT, address=DAC_ADDRESS)

    with dac.output as out0, adc.differential_input(1) as in1:
        nvals = 10
        for v in (i*2.0/nvals for i in range(nvals, 0, -1)):
            out0.value = v
            # we must do an extra read here, and thus trigger a
            # conversion with the new value
            in1.get()           
            assert_is_approx(v, in1.value)
