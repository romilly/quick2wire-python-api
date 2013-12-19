"""Loopback attempts for the LTC2631

We do nothing in this test beyond checking that we can connect to the
chip and read a sane value from it.
"""

from quick2wire.i2c import I2CMaster
from quick2wire.parts.ltc2631 import LTC2631
#import pytest

from time import sleep

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

setup_function(0)

adc = LTC2631(i2c, 'HZ12', address=0x10)
with adc.output as output:
    for v in (1.0, 4.0, 2.0, 3.0):
        output.set(v)
        print('message sent: v={}'.format(v))
        input('Type return...')
    print('exiting')
