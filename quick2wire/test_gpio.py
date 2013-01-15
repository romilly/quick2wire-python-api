
from quick2wire.gpio import GPIOPin, exported, In, Out
import pytest


@pytest.mark.gpio
@pytest.mark.loopback
class TestPin:
    def setup_method(self, method):
        self.pin = GPIOPin(0)
    
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
        
        self.pin.direction = Out
        assert self.pin.direction == Out
        
        self.pin.direction = In
        assert self.pin.direction == In

        
    def test_can_set_value_of_output_pin(self):
        self.pin.export()
        
        self.pin.direction = Out
        
        self.pin.value = 1
        assert self.pin.value == 1
        
        self.pin.value = 0
        assert self.pin.value == 0
        
    def test_can_export_pin_and_set_direction_on_construction(self):
        p = GPIOPin(0, Out)
        
        assert p.is_exported
        assert p.direction == Out

    def test_can_read_after_write(self):
        outpin = GPIOPin(0, Out)
        
        outpin.value = 1
        assert self.pin.value == 1
        with open('/sys/class/gpio/gpio17/value', 'r+') as f:
            assert f.read() == '1\n'
    


@pytest.mark.gpio
@pytest.mark.loopback
class TestExportedContextManager:
    def test_can_automatically_unexport_pin_with_context_manager(self):
        with exported(GPIOPin(0)) as p:
            assert p.is_exported
        
        p = GPIOPin(0)
        assert not p.is_exported
    
    def test_can_use_context_manager_with_pin_exported_by_constructor(self):
        with exported(GPIOPin(0, Out)) as p:
            assert p.is_exported
        
        p = GPIOPin(0)
        assert not p.is_exported
    
    def test_can_use_context_manager_with_pin_already_exported(self):
        GPIOPin(0).export()
        self.test_can_automatically_unexport_pin_with_context_manager()
        
