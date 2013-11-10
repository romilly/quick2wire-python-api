from quick2wire.i2c_ctypes import I2C_M_RD
from quick2wire.parts.mcp3221 import MCP3221
from quick2wire.gpio import In
import pytest

class FakeI2CMaster:
    def __init__(self):
        self._requests = []
        self._responses = []
        self._next_response = 0
        self.message_precondition = lambda m: True
        
    def all_messages_must(self, p):
        self.message_precondition
    
    def clear(self):
        self.__init__()
    
    def transaction(self, *messages):
        for m in messages:
            self.message_precondition(m)
        
        self._requests.append(messages)
        
        read_count = sum(bool(m.flags & I2C_M_RD) for m in messages)
        if read_count == 0:
            return []
        elif self._next_response < len(self._responses):
            response = self._responses[self._next_response]
            self._next_response += 1
            return response
        else:
            return [(0x00,)]*read_count
    
    def add_response(self, *messages):
        self._responses.append(messages)
    
    @property
    def request_count(self):
        return len(self._requests)
    
    def request(self, n):
        return self._requests[n]


i2c = FakeI2CMaster()

# def is_read(m):
#     return bool(m.flags & I2C_M_RD)

# def is_write(m):
#     return not is_read(m)

def assert_is_approx(expected, value, delta=0.005):
    assert abs(value - expected) <= delta

def correct_message_for(adc):
    def check(m):
        assert m.addr == adc.address
        assert m.flags in (0, I2C_M_RD)
        assert m.len == 1 or m.len == 2
    
    return check


def setup_function(f):
    i2c.clear()

def create_mcp3221(*args, **kwargs):
    adc = MCP3221(*args, **kwargs)
    i2c.message_precondition = correct_message_for(adc)
    return adc

def test_cannot_be_created_with_invalid_address():
    with pytest.raises(ValueError):
        MCP3221(i2c, 8)

def test_can_read_a_single_ended_pin():
    adc = create_mcp3221(i2c, 0)
    pin = adc.single_ended_input

    i2c.add_response(bytes([0x8, 0x00]))

    assert pin.direction == In

    sample = pin.value

    assert_is_approx(0.5, sample)

def test_can_read_a_single_ended_pin_raw():
    adc = create_mcp3221(i2c, 0)
    pin = adc.single_ended_input

    i2c.add_response(bytes([0x8, 0x00]))

    sample = pin.raw_value

    assert sample == 0x800
