from quick2wire.i2c_ctypes import I2C_M_RD
from quick2wire.gpio import Out
from quick2wire.parts.ltc2631 import LTC2631
import pytest


# This fake I2C master class is now cut-and-pasted in three places.
# Separating this into a separate module would be desirable, but not trivial
# (because the pytest sys.path includes only the directory where
# pytest was run).  That's for a later refactoring.
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


def correct_message_for(dac):
    def check(m):
        assert m.addr == dac.address
        assert m.flags not in (0, I2C_M_RD)
        assert m.len == 3
    
    return check



i2c = FakeI2CMaster()

def is_read(m):
    return bool(m.flags & I2C_M_RD)

def is_write(m):
    return not is_read(m)

def setup_function(f):
    i2c.clear()

def create_ltc2631(*args, **kwargs):
    dac = LTC2631(*args, **kwargs)
    i2c.message_precondition = correct_message_for(dac)
    return dac

def test_cannot_create_invalid_variant():
    with pytest.raises(ValueError):
        LTC2631(i2c, 'foo')

def test_cannot_create_with_bad_address():
    with pytest.raises(ValueError):
        LTC2631(i2c, 'LM12', address=0x20) # M variants support 0x10, 11, 12

def test_can_create():
    dac = LTC2631(i2c, 'LM12')
    assert dac.direction == Out

def test_can_create_different_address():
    dac = LTC2631(i2c, 'LM12', address=0x12)
    assert dac.direction == Out

def test_can_create_global_address():
    dac = LTC2631(i2c, 'LM12', address=0x73)
    assert dac.direction == Out

def test_can_powerdown():
    dac = LTC2631(i2c, 'LM12')

    dac.powerdown()

    assert i2c.request_count == 1
    m1, = i2c.request(0)
    assert is_write(m1)
    assert m1.len == 3
    assert m1.buf[0][0] == 0x40 # spec requires 0b0100xxxx
    assert m1.buf[1][0] == 0    # bytes 2 and 3 are don't-cares
    assert m1.buf[2][0] == 0

def test_can_write_lm10():
    dac = LTC2631(i2c, 'LM10')
    assert not dac.reset_to_zero_p() # This variant resets to mid-range
    assert dac.full_scale() == 2.5

    pin = dac.output
    assert pin.direction == Out

    pin.value = 1.25            # -> 1.25/2.5*2^10 = 0x200x

    assert i2c.request_count == 1
    m1, = i2c.request(0)
    assert is_write(m1)
    assert m1.len == 3
    assert m1.buf[0][0] == 0x30 # 0x3x is Write and Update DAC
    assert m1.buf[1][0] == 0x80 # 0x200 << 6 = 0x8000
    assert m1.buf[2][0] == 0x00

def test_can_write_lz12():
    dac = LTC2631(i2c, 'LZ12')
    assert dac.reset_to_zero_p()  # This variant resets to zero-range
    assert dac.full_scale() == 2.5

    pin = dac.output
    assert pin.direction == Out

    pin.value = 0.1777          # -> 0.1777/2.5*2^12 = 0x123x

    assert i2c.request_count == 1
    m1, = i2c.request(0)
    assert is_write(m1)
    assert m1.len == 3
    assert m1.buf[0][0] == 0x30 # 0x3x is Write and Update DAC
    assert m1.buf[1][0] == 0x12 # 0x123 << 4 = 0x1230
    assert m1.buf[2][0] == 0x30

def test_can_write_hz8():
    dac = LTC2631(i2c, 'HZ8')
    assert dac.reset_to_zero_p() # This variant resets to zero-range
    assert dac.full_scale() == 4.096

    pin = dac.output
    assert pin.direction == Out

    pin.value = 2.635           # -> 2.635/4.096*2^8 = 164.69, rounded to 0xa5x

    assert i2c.request_count == 1
    m1, = i2c.request(0)
    assert is_write(m1)
    assert m1.len == 3
    assert m1.buf[0][0] == 0x30 # 0x3x is Write and Update DAC
    assert m1.buf[1][0] == 0xa5 # 0xa5 << 8 = 0xa500
    assert m1.buf[2][0] == 0x00
