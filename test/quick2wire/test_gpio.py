
from quick2wire.gpio import Pin, exported
import pytest


@pytest.mark.gpio
@pytest.mark.hardware
class TestPin:
    def setup_method(self, method):
        self.pin = Pin(25)
    
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
        p = Pin(25, Pin.Out)
        
        assert p.is_exported
        assert p.direction == Pin.Out



@pytest.mark.gpio
@pytest.mark.hardware
class TestExportedContextManager:
    def test_can_automatically_unexport_pin_with_context_manager(self):
        with exported(Pin(25)) as p:
            assert p.is_exported
        
        p = Pin(25)
        assert not p.is_exported
    
    def test_can_use_context_manager_with_pin_exported_by_constructor(self):
        with exported(Pin(25, Pin.Out)) as p:
            assert p.is_exported
        
        p = Pin(25)
        assert not p.is_exported
    
    def test_can_use_context_manager_with_pin_already_exported(self):
        Pin(25).export()
        self.test_can_automatically_unexport_pin_with_context_manager()
        
