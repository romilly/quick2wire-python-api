"""Loopback tests for the PCF8591 API

Topology:

 - connect AOUT to AIN3
 - connect AIN1 to GND
 - connect AIN2 to VREF
 - AIN0 is unused

"""

from time import sleep
from quick2wire.i2c import I2CMaster
from quick2wire.parts.pcf8591 import PCF8591, FOUR_SINGLE_ENDED
import pytest


def before_function(f):
    global i2c
    i2c = I2CMaster()


def after_function(f):
    i2c.close()


def assert_is_approx(expected, value, delta=0.05):
    assert abs(value - expected) <= delta


@pytest.mark.loopback
@pytest.mark.pcf8591
def test_pcf8591_loopback_single_ended():
    adc = PCF8591(i2c, FOUR_SINGLE_ENDED)
    input = adc.single_ended_input(3)
    
    with adc.output as output:
        for i in range(256):
            v = i/255.0
            output.value = v
            assert_is_approx(v, input.value)


@pytest.mark.loopback
@pytest.mark.pcf8591
def test_pcf8591_loopback_differential():
    adc = PCF8591(i2c, THREE_DIFFERENTIAL)
    cmp_gnd = adc.differential_input(1)
    cmp_vref = adc.differential_input(2)
    
    with adc.output as output:
        for i in range(256):
            v = i/255.0
            output.value = v
            assert_is_approx(v, cmp_gnd.value)
            assert_is_approx(v-1, cmp_vref.value)
