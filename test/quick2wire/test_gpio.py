
from quick2wire.gpio import Pin
import pytest


class TestPin:
    def setup_method(self, method):
        self.pin = Pin(5)
    
    def teardown_method(self, method):
        if self.pin.is_exported:
            self.pin.unexport()
    
    def test_pin_must_be_exported_before_use(self):
        with pytest.raises(IOError):
            self.pin.value
        self.pin.export()
        self.pin.value
        
    def test_pin_can_be_unexported_and_made_unusable(self):
        self.pin.export()
        self.pin.unexport()
        with pytest.raises(IOError):
            self.pin.value
    
    def test_can_set_and_query_direction_of_pin(self):
        self.pin.export()
        
        self.pin.direction = Pin.Out
        assert self.pin.direction == Pin.Out
        
        self.pin.direction = Pin.In
        assert self.pin.direction == Pin.In

        
    def test_can_set_value_of_output_pin(self):
        self.pin.export()
        
        self.pin.direction = Pin.Out
        
        self.pin.value = 1
        assert self.pin.value == 1
        
        self.pin.value = 0
        assert self.pin.value == 0
        
    def test_can_export_pin_and_set_direction_on_construction(self):
        p = Pin(5, Pin.Out)
        
        assert p.is_exported
        assert p.direction == Pin.Out
        
