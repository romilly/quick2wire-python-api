"""Loopback tests for the LTC2631 DAC and LTC2309 ADC

Requires 1x LTC2309 and 1x LTC2631

Topology:

  * connect 2631 GND to 2309 CH0
  * connect 2631 Vout to 2309 CH1
  
"""

from quick2wire.i2c import I2CMaster
from quick2wire.parts.ltc2631 import LTC2631
from quick2wire.parts.ltc2309 import LTC2309
import pytest

DAC_ADDRESS = 0x10 # LTC2631
DAC_VARIANT = 'HZ12'
ADC_ADDRESS = 0x08 # LTC2309

#from time import sleep

def setup_function(f):
    global i2c
    i2c = I2CMaster()

def teardown_function(f):
    i2c.close()

def assert_is_approx(expected, actual, delta=0.02):
    assert abs(actual - expected) <= delta


# Only a very simple test is possible -- do we get a sane value back
# from the chip?
# @pytest.mark.loopback
# @pytest.mark.ltc2631
# def test_ltc2631_loopback_single_ended():
#     adc = LTC2631(i2c)
#     input = adc.single_ended_output
#     v = output.value
#     assert v >= 0.0
#     assert v < 1.0

# def exercise_ltc2631_loopback_single_ended():
#     with I2CMaster() as i2c:
#         adc = LTC2631(i2c)
#         input = adc.single_ended_input

#         for i in range(10):
#             print("{}: {}".format(i, input.value))
#             sleep(1)

#exercise_ltc2631_loopback_single_ended()

####

#setup_function(0)

# adc = LTC2631(i2c, 'HZ12', address=0x10)
# with adc.output as output:
#     for v in (1.0, 4.0, 2.0, 3.0):
#         output.set(v)
#         print('message sent: v={}'.format(v))
#         input('Type return...')
#     print('exiting')

@pytest.mark.loopback
@pytest.mark.ltc2309
@pytest.mark.ltc2631
def test_single_channel():
    adc = LTC2309(i2c, address=ADC_ADDRESS)
    dac = LTC2631(i2c, DAC_VARIANT, address=DAC_ADDRESS)

    with dac.output as out0, adc.single_ended_input(0) as in0, adc.single_ended_input(1) as in1:
        nvals = 10
        for v in (i*3.0/nvals for i in range(nvals)):
            print('v={}'.format(v))
            out0.value = v
            assert_is_approx(0.0, in0.value)
            assert_is_approx(v, in1.value)

# Differential channels are currently untested
# -- I need a different test harness for that.
# def test_differential_channel():
#     adc = LTC2309(i2c, address=ADC_ADDRESS)
#     dac = LTC2631(i2c, DAC_VARIANT, address=DAC_ADDRESS)

#     with dac.output as out0, adc.differential_input(0, negate=False) as in0:
#         nvals = 10
#         for v in (i*2.0/nvals for i in range(nvals)):
#             out0.value = v
#             #assert_is_approx(v, in0.value)
#             print('v={} -> {}'.format(v, in0.value))

#test_differential_channel()
