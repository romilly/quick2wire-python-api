
from quick2wire.i2c_ctypes import I2C_M_RD
from quick2wire.parts.pcf8591 import PinBank as PCF8591
from quick2wire.parts.pcf8591 import FOUR_SINGLE_ENDED, THREE_DIFFERENTIAL, SINGLE_ENDED_AND_DIFFERENTIAL, TWO_DIFFERENTIAL
from factcheck import forall, from_range

class FakeI2CMaster:
    def __init__(self):
        self._requests = []
        self._responses = []
        self._next_response = 0
        
    def clear(self):
        self.__init__()
    
    def transaction(self, *messages):
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

def is_read(m):
    return bool(m.flags & I2C_M_RD)

def is_write(m):
    return not is_read(m)

def assert_is_approx(expected, value, delta=0.005):
    assert abs(value - expected) <= delta


def setup_function(f):
    i2c.clear()


octets = from_range(256)


def test_can_be_created_with_four_single_ended_inputs():
    adc = PCF8591(i2c, FOUR_SINGLE_ENDED)
    assert adc.input_count == 4

def test_can_be_created_with_three_differential_inputs():
    adc = PCF8591(i2c, THREE_DIFFERENTIAL)
    assert adc.input_count == 3

def test_can_be_created_with_one_differential_and_two_single_ended_inputs():
    adc = PCF8591(i2c, SINGLE_ENDED_AND_DIFFERENTIAL)
    assert adc.input_count == 3

def test_can_be_created_with_two_differential_inputs():
    adc = PCF8591(i2c, TWO_DIFFERENTIAL)
    assert adc.input_count == 2

def test_reading_a_pin_requests_adc_for_associated_channel_with_correct_mode_bits():
    adc = PCF8591(i2c, FOUR_SINGLE_ENDED, samples=1)
    
    pin = adc.input_pin(2)
    
    i2c.add_response(bytes([64]))
    
    sample = pin.value
    
    assert i2c.request_count == 2
    
    m1, = i2c.request(0)
    assert is_write(m1)
    assert m1.addr == adc.address
    assert m1.len == 1
    assert m1.buf[0][0] == 0b00000010
    
    m2, = i2c.request(1)
    assert is_read(m2)
    assert m2.addr == adc.address
    assert m2.len == 1
    
    assert_is_approx(0.25, sample)


def test_sends_correct_mode_bits_for_four_single_ended_mode():
    adc = PCF8591(i2c, FOUR_SINGLE_ENDED)
    pin = adc.input_pin(1)
    
    pin.value
    
    assert i2c.request(0)[0].buf[0][0] == 0b00000001


def test_sends_correct_mode_bits_for_four_single_ended_mode():
    adc = PCF8591(i2c, FOUR_SINGLE_ENDED)
    pin = adc.input_pin(1)
    
    pin.value
    
    assert i2c.request(0)[0].buf[0][0] == 0b00000001


def test_sends_correct_mode_bits_for_two_differential_mode():
    adc = PCF8591(i2c, TWO_DIFFERENTIAL)
    pin = adc.input_pin(1)
    
    pin.value
    
    assert i2c.request(0)[0].buf[0][0] == 0b00110001


def test_sends_correct_mode_bits_for_single_ended_and_differential_mode():
    adc = PCF8591(i2c, SINGLE_ENDED_AND_DIFFERENTIAL)
    pin = adc.input_pin(1)
    
    pin.value
    
    assert i2c.request(0)[0].buf[0][0] == 0b00100001
    

def test_can_be_configured_to_perform_multiple_samples_and_reports_last_one():
    adc = PCF8591(i2c, THREE_DIFFERENTIAL, samples=3)
    
    pin = adc.input_pin(1)
    
    i2c.add_response(bytes([32]))
    i2c.add_response(bytes([64]))
    i2c.add_response(bytes([128]))
    
    sample = pin.value
    
    assert_is_approx(0.5, sample)


def test_does_not_write_control_byte_to_switch_channel_if_multiple_reads_from_same_pin():
    adc = PCF8591(i2c, THREE_DIFFERENTIAL, samples=1)
    
    pin0 = adc.input_pin(0)
    pin1 = adc.input_pin(1)
    
    sample = pin0.value
    assert i2c.request_count == 2
    ctl1, = i2c.request(0)
    assert is_write(ctl1)
    assert ctl1.len == 1
    assert ctl1.buf[0][0] == 0b00010000
    
    sample = pin0.value
    assert i2c.request_count == 3
    
    sample = pin1.value
    assert i2c.request_count == 5
    
    ctl2, = i2c.request(3)
    assert is_write(ctl2)
    assert ctl2.len == 1
    assert ctl2.buf[0][0] == 0b00010001


    

