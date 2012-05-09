
from quick2wire.gpio import Pin
from time import sleep
import pytest

Pins = [Pin(header_pin_number) for header_pin_number in [11, 12, 13, 15, 16, 18, 22, 7]]

def setup_module():
    for pin in Pins:
        pin.export()

def teardown_module():
    for pin in Pins:
        if pin.is_exported:
            pin.unexport()

@pytest.mark.gpio_loopback
def test_gpio_loopback():
    assert_outputs_seen_at_corresponding_inputs(Pins[:4], Pins[4:])
    assert_outputs_seen_at_corresponding_inputs(Pins[4:], Pins[:4])


def assert_outputs_seen_at_corresponding_inputs(outputs, inputs):
    for (op, ip) in zip(outputs, inputs):
        assert_output_seen_at_input(op, ip)


def assert_output_seen_at_input(output_pin, input_pin):
    output_pin.direction = Pin.Out
    input_pin.direction = Pin.In
    
    for value in [0, 1]:
        output_pin.value = value
        assert input_pin.value == value
        
    output_pin.value = 0



