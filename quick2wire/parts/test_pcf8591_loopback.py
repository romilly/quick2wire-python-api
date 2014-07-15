"""Loopback tests for the PCF8591 API

Topology:

 - connect AIN1 to ground
 - connect AIN2 to 3V3
 - connect AIN3 to AOUT
 - connect VREF to 3v3
 - connect AGND to ground
 - AIN0 is unused

"""

from time import sleep
from quick2wire.i2c import I2CMaster
from quick2wire.parts.pcf8591 import PCF8591, FOUR_SINGLE_ENDED, THREE_DIFFERENTIAL
import pytest


def setup_function(f):
    global i2c
    i2c = I2CMaster()


def teardown_function(f):
    i2c.close()


def assert_is_approx(expected, actual, delta=0.02):
    assert abs(actual - expected) <= delta


@pytest.mark.loopback
@pytest.mark.pcf8591
def test_pcf8591_loopback_single_ended():
    adc = PCF8591(i2c, FOUR_SINGLE_ENDED)
    input = adc.single_ended_input(3)
    
    with adc.output as output:
        for v in (i/255.0 for i in range(256)):
            output.value = v
            assert_is_approx(v, input.value)


@pytest.mark.loopback
@pytest.mark.pcf8591
def test_pcf8591_loopback_switching_channels():
    adc = PCF8591(i2c, FOUR_SINGLE_ENDED)
    p1 = adc.single_ended_input(1)
    p2 = adc.single_ended_input(2)
    
    for i in range(8):
        assert p1.value == 0.0
        assert p2.value == 1.0


@pytest.mark.loopback
@pytest.mark.pcf8591
def test_pcf8591_loopback_differential_vref_to_ain3():
    adc = PCF8591(i2c, THREE_DIFFERENTIAL)
    cmp_vref = adc.differential_input(2)
    
    with adc.output as output:
        for v in (i/255.0 for i in range(256)):
            output.value = v
            assert_is_approx(min(0.5, 1-v), cmp_vref.value)


@pytest.mark.loopback
@pytest.mark.pcf8591
def test_pcf8591_loopback_differential_gnd_to_ain3():
    adc = PCF8591(i2c, THREE_DIFFERENTIAL)
    cmp_gnd = adc.differential_input(1)
    
    with adc.output as output:
        for v in (i/255.0 for i in range(256)):
            output.value = v
            assert_is_approx(max(-0.5, -v), cmp_gnd.value)
