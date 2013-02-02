
import os
from quick2wire.gpio import pins, In, Out, PullDown, gpio_admin
import pytest


@pytest.mark.gpio
@pytest.mark.loopback
class TestGPIO:
    def test_pin_must_be_opened_before_use_and_is_unusable_after_being_closed(self):
        pin = pins.pin(0)
        
        with pytest.raises(IOError):
            pin.value
        
        pin.open()
        try:
            pin.value
        finally:
            pin.close()
        
        with pytest.raises(IOError):
            pin.value
    
    
    def test_opens_and_closes_itself_when_used_as_a_context_manager(self):
        pin = pins.pin(0)
        
        with pin:
            pin.value
        
        with pytest.raises(IOError):
            pin.value
    
    
    def test_exports_gpio_device_to_userspace_when_opened_and_unexports_when_closed(self):
        with pins.pin(0) as pin:
            assert os.path.exists('/sys/class/gpio/gpio17/value')
        
        assert not os.path.exists('/sys/class/gpio/gpio17/value')
    
    
    def test_can_set_and_query_direction_of_pin_when_open(self):
        with pins.pin(0) as pin:
            pin.direction = Out
            assert pin.direction == Out
            
            assert content_of("/sys/class/gpio/gpio17/direction") == "out\n"
            
            pin.direction = In
            assert pin.direction == In
            
            assert content_of("/sys/class/gpio/gpio17/direction") == "in\n"
    
    
    def test_can_set_direction_on_construction(self):
        pin = pins.pin(0, Out)
        
        assert pin.direction == Out
        assert not os.path.exists("/sys/class/gpio/gpio17/direction")
        
        with pin:
            assert content_of("/sys/class/gpio/gpio17/direction") == "out\n"
            assert pin.direction == Out
    
    
    def test_setting_value_of_output_pin_writes_to_device_file(self):
        with pins.pin(0) as pin:
            pin.direction = Out
            
            pin.value = 1
            assert pin.value == 1
            assert content_of('/sys/class/gpio/gpio17/value') == '1\n'
            
            pin.value = 0
            assert pin.value == 0
            assert content_of('/sys/class/gpio/gpio17/value') == '0\n'
    
    
    def test_direction_and_value_of_pin_is_reset_when_closed(self):
        with pins.pin(0, Out) as pin:
            pin.value = 1
        
        gpio_admin("export", 17, PullDown)
        try:
            assert content_of('/sys/class/gpio/gpio17/value') == '0\n'
            assert content_of('/sys/class/gpio/gpio17/direction') == 'in\n'
        finally:
            gpio_admin("unexport", 17)

    def test_cannot_get_a_pin_with_an_invalid_index(self):
        with pytest.raises(IndexError):
            pins.pin(-1)
        
        with pytest.raises(IndexError):
            pins.pin(len(pins))

        
def content_of(filename):
    with open(filename, 'r') as f:
        return f.read()

