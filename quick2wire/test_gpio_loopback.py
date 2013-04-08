"""Loopback tests for the GPIO pins

Topology:

 - connect P2 to P3
 - connect P4 to P5
 - P0 and P1 are left free to be jumpered to the LED and button
 - P6 and P7 are reserved for testing I2C and SPI interrupts
"""

from quick2wire.gpio import pins, pi_header_1, In, Out
from time import sleep
import pytest


def inverse(topology):
    return [(b,a) for (a,b) in topology]


@pytest.mark.loopback
@pytest.mark.gpio
def test_gpio_loopback():
    assert_outputs_seen_at_corresponding_inputs(pins, [(0,1), (2,3), (4,5)])


@pytest.mark.loopback
@pytest.mark.gpio
def test_gpio_loopback_by_header_pin():
    assert_outputs_seen_at_corresponding_inputs(pi_header_1, [(11,12), (13,15), (16,18)])


def assert_outputs_seen_at_corresponding_inputs(pin_bank, topology):
    for (op, ip) in topology:
        assert_output_seen_at_input(pin_bank, op, ip)
    
    for (op, ip) in inverse(topology):
        assert_output_seen_at_input(pin_bank, op, ip)


def assert_output_seen_at_input(pin_bank, op, ip):
  with pin_bank.pin(op, direction=Out) as output_pin,\
       pin_bank.pin(ip, direction=In) as input_pin:
    for value in [1, 0, 1, 0]:
      output_pin.value = value
      assert input_pin.value == value
