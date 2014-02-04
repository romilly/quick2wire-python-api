from quick2wire.i2c_ctypes import I2C_M_RD
from quick2wire.gpio import In
from quick2wire.parts.ltc2309 import LTC2309
import pytest


# This fake I2C master class is now cut-and-pasted in four places.
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


def assert_is_approx(expected, value, delta=0.005):
    assert abs(value - expected) <= delta

def correct_message_for(adc):
    def check(m):
        assert m.addr == adc.address or m.addr == 0x6b
        assert m.flags in (0, I2C_M_RD)
        assert m.len <= 2
    
    return check



i2c = FakeI2CMaster()

def is_read(m):
    return bool(m.flags & I2C_M_RD)

def is_write(m):
    return not is_read(m)

def setup_function(f):
    i2c.clear()

def create_ltc2309(*args, **kwargs):
    adc = LTC2309(*args, **kwargs)
    i2c.message_precondition = correct_message_for(adc)
    return adc

####

def test_cannot_create_with_bad_address():
    with pytest.raises(ValueError):
        LTC2309(i2c, address=0)

def test_cannot_create_with_global_address():
    with pytest.raises(ValueError):
        LTC2309(i2c, address=0x6b)

def test_can_create():
    adc = create_ltc2309(i2c)
    assert adc.direction == In

def test_can_create_different_address():
    adc = create_ltc2309(i2c, address=0x18)
    assert adc.direction == In

def test_read_single_unipolar_channel_0():
    adc = create_ltc2309(i2c)
    with adc.single_ended_input(0) as input:
        assert input.direction == In

        i2c.add_response(bytes([0x12, 0x30]))

        sample = input.value

        # there are two requests, the write which changes the Din, and the read
        assert i2c.request_count == 2
        m1, = i2c.request(0)
        assert is_write(m1)
        assert m1.len == 1
        assert m1.buf[0][0] == 0x88 # 0b1000 10xx (cf data sheet Table 1)

        m2, = i2c.request(1)
        assert is_read(m2)
        assert m2.len == 2      # 2-byte response

        assert_is_approx(0.291, sample) # 0x123 * 1mV

def test_read_single_channel_with_sleep():
    # as above, but do two reads, with the second one setting the sleep bit
    adc = create_ltc2309(i2c)
    with adc.single_ended_input(0) as input:
        assert input.direction == In

        i2c.add_response(bytes([0x12, 0x30]))
        i2c.add_response(bytes([0x45, 0x60]))

        sample = input.value
        assert_is_approx(0.291, sample)

        input.sleep_after_conversion(True)

        sample = input.value
        assert_is_approx(1.110, sample)

        # there are four requests:
        #   1. the write which changes the Din for the first time
        #   2. the first read request
        #   3. the write which updates the Din
        #   4. the second read request
        assert i2c.request_count == 4

        m, = i2c.request(0)
        assert is_write(m)
        assert m.len == 1
        assert m.buf[0][0] == 0x88

        m, = i2c.request(1)
        assert is_read(m)
        assert m.len == 2

        m, = i2c.request(2)
        assert is_write(m)
        assert m.len == 1
        assert m.buf[0][0] == 0x8c # 0x1000 1100, including set SLP bit

        m, = i2c.request(3)
        assert is_read(m)
        assert m.len == 2

def test_read_single_bipolar_channel_0():
    adc = create_ltc2309(i2c)
    with adc.single_ended_input(0, bipolar=True) as input:
        assert input.direction == In

        i2c.add_response(bytes([0xa0, 0x10]))

        sample = input.value

        assert i2c.request_count == 2
        m1, = i2c.request(0)
        assert is_write(m1)
        assert m1.len == 1
        assert m1.buf[0][0] == 0x80 # 0x1000 00xx (cf data sheet Table 1)

        m2, = i2c.request(1)
        assert is_read(m2)
        assert m2.len == 2

        assert_is_approx(-1.535, sample) # (0xa01 - 0x1000) * 1mV

def test_multiread_single_unipolar_channels():
    adc = create_ltc2309(i2c)
    with adc.single_ended_input(0) as i0, adc.single_ended_input(1) as i1:
        assert i0.direction == In
        assert i1.direction == In

        i2c.add_response(bytes([0x12, 0x30]))
        i2c.add_response(bytes([0x45, 0x60]))
        i2c.add_response(bytes([0x78, 0x90]))

        sample = i0.value
        # there are two requests, the write which changes the Din, and the read
        assert i2c.request_count == 2
        m1, = i2c.request(0)
        assert is_write(m1)
        assert m1.len == 1
        assert m1.buf[0][0] == 0x88 # 0b1000 10xx (cf data sheet Table 1)
        m2, = i2c.request(1)
        assert is_read(m2)
        assert m2.len == 2
        assert_is_approx(0.291, sample) # 0x123 * 1mV

        sample = i0.value
        # just one new request this time, because we don't change the Din
        assert i2c.request_count == 3
        m1, = i2c.request(2)
        assert is_read(m1)
        assert m1.len == 2
        assert_is_approx(1.110, sample) # 0x456 * 1mV

        sample = i1.value
        # two new requests again
        assert i2c.request_count == 5
        m1, = i2c.request(3)
        assert is_write(m1)
        assert m1.len == 1
        assert m1.buf[0][0] == 0xc8 # 0b1100 10xx (cf data sheet Table 1)
        m2, = i2c.request(4)
        assert is_read(m2)
        assert m2.len == 2
        assert_is_approx(1.929, sample) # 0x789 * 1mV

def test_read_differential_channel_0():
    adc = create_ltc2309(i2c)
    with adc.differential_input(0) as input:
        assert input.direction == In

        i2c.add_response(bytes([0x12, 0x30]))

        sample = input.value
        # there is only one requests, because this Din is the default
        assert i2c.request_count == 1
        m1, = i2c.request(0)
        assert is_read(m1)
        assert m1.len == 2      # 2-byte response

        assert_is_approx(0.291, sample) # 0x123 * 1mV

def test_read_differential_channel_0_negated():
    # as above, but with the differential sign swapped
    adc = create_ltc2309(i2c)
    with adc.differential_input(0, negate=True) as input:
        assert input.direction == In

        i2c.add_response(bytes([0x12, 0x30]))

        sample = input.value
        # there are two requests, the write which changes the Din, and the read
        assert i2c.request_count == 2
        m1, = i2c.request(0)
        assert is_write(m1)
        assert m1.len == 1
        assert m1.buf[0][0] == 0x40 # 0b0100 00xx (cf data sheet Table 1)

        m2, = i2c.request(1)
        assert is_read(m2)
        assert m2.len == 2      # 2-byte response

        assert_is_approx(0.291, sample) # 0x123 * 1mV

def test_global_sync():
    adc = create_ltc2309(i2c)
    adc.global_sync()

    assert i2c.request_count == 1
    m1, = i2c.request(0)
    assert is_write(m1)
    assert m1.addr == 0x6b
    assert m1.len == 0
