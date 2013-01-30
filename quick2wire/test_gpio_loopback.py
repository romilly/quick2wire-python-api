
from quick2wire.gpio import pi_header_1, gpio_breakout, In, Out
from time import sleep
import pytest


def inverse(topology):
    return [(b,a) for (a,b) in topology]


@pytest.mark.loopback
@pytest.mark.gpio
def test_gpio_loopback():
    assert_outputs_seen_at_corresponding_inputs(
        gpio_breakout, 
        [(i,i+4) for i in range(4)])


@pytest.mark.loopback
@pytest.mark.gpio
def test_gpio_loopback_by_header_pin():
    assert_outputs_seen_at_corresponding_inputs(
        pi_header_1, 
        [(11,16), (12,18), (13,22), (15,7)])



def assert_outputs_seen_at_corresponding_inputs(pin_bank, topology):
    for (op, ip) in topology:
        assert_output_seen_at_input(pin_bank, op, ip)
    
    for (op, ip) in inverse(topology):
        assert_output_seen_at_input(pin_bank, op, ip)


def assert_output_seen_at_input(pin_bank, op, ip):
    output_pin = pin_bank.pin(op, direction=Out)
    input_pin = pin_bank.pin(ip, direction=In)
    
    with output_pin, input_pin:
        for value in [1, 0, 1, 0]:
            output_pin.value = value
            assert input_pin.value == value
