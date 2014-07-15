
from quick2wire.i2c_ctypes import I2C_M_RD
from quick2wire.gpio import In
from quick2wire.parts.pcf8591 import PCF8591, FOUR_SINGLE_ENDED, THREE_DIFFERENTIAL, SINGLE_ENDED_AND_DIFFERENTIAL, TWO_DIFFERENTIAL
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

def is_read(m):
    return bool(m.flags & I2C_M_RD)

def is_write(m):
    return not is_read(m)

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

def create_pcf8591(*args, **kwargs):
    adc = PCF8591(*args, **kwargs)
    i2c.message_precondition = correct_message_for(adc)
    return adc

def assert_all_input_pins_report_direction(adc):
    assert all(adc.single_ended_input(p).direction == In for p in range(adc.single_ended_input_count))
    assert all(adc.differential_input(p).direction == In for p in range(adc.differential_input_count))


def test_can_be_created_with_four_single_ended_inputs():
    adc = PCF8591(i2c, FOUR_SINGLE_ENDED)
    assert adc.single_ended_input_count == 4
    assert adc.differential_input_count == 0
    assert_all_input_pins_report_direction(adc)

def test_can_be_created_with_three_differential_inputs():
    adc = PCF8591(i2c, THREE_DIFFERENTIAL)
    assert adc.single_ended_input_count == 0
    assert adc.differential_input_count == 3
    assert_all_input_pins_report_direction(adc)

def test_can_be_created_with_one_differential_and_two_single_ended_inputs():
    adc = PCF8591(i2c, SINGLE_ENDED_AND_DIFFERENTIAL)
    assert adc.single_ended_input_count == 2
    assert adc.differential_input_count == 1
    assert_all_input_pins_report_direction(adc)

def test_can_be_created_with_two_differential_inputs():
    adc = PCF8591(i2c, TWO_DIFFERENTIAL)
    assert adc.single_ended_input_count == 0
    assert adc.differential_input_count == 2
    assert_all_input_pins_report_direction(adc)

def test_cannot_be_created_with_an_invalid_mode():
    with pytest.raises(ValueError):
        PCF8591(i2c, 999)

def test_can_read_a_single_ended_pin():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    pin = adc.single_ended_input(2)
    
    i2c.add_response(bytes([0x80, 0x60]))
    i2c.add_response(bytes([0x40, 0x40]))
    
    sample = pin.value
    
    assert i2c.request_count == 2
    
    m1a,m1b = i2c.request(0)
    assert is_write(m1a)
    assert m1a.len == 1
    assert m1a.buf[0][0] == 0b00000010
    
    assert is_read(m1b)
    assert m1b.len == 2
    
    m2, = i2c.request(1)
    assert is_read(m2)
    assert m2.len == 2
    
    assert_is_approx(0.25, sample)


def test_can_read_raw_value_of_a_single_ended_pin():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    pin = adc.single_ended_input(2)
    
    i2c.add_response(bytes([0x80, 0x60]))
    i2c.add_response(bytes([0x40, 0x40]))
    
    sample = pin.raw_value
    
    assert i2c.request_count == 2
    
    m1a,m1b = i2c.request(0)
    assert is_write(m1a)
    assert m1a.len == 1
    assert m1a.buf[0][0] == 0b00000010
    
    assert is_read(m1b)
    assert m1b.len == 2
    
    m2, = i2c.request(1)
    assert is_read(m2)
    assert m2.len == 2
    
    assert sample == 0x40


def test_can_read_a_differential_pin():
    adc = create_pcf8591(i2c, THREE_DIFFERENTIAL)
    
    pin = adc.differential_input(1)
    

    i2c.add_response(bytes([0x80, 0x60]))
    
    # -64 in 8-bit 2's complement representation
    i2c.add_response(bytes([0xC0, 0xC0]))
    
    sample = pin.raw_value
    
    assert i2c.request_count == 2
    
    m1a,m1b = i2c.request(0)
    assert is_write(m1a)
    assert m1a.len == 1
    assert m1a.buf[0][0] == 0b00010001
    
    assert is_read(m1b)
    assert m1b.len == 2
    
    m2, = i2c.request(1)
    assert is_read(m2)
    assert m2.len == 2
    
    assert sample == -64


def test_can_read_raw_value_of_a_differential_pin():
    adc = create_pcf8591(i2c, THREE_DIFFERENTIAL)
    
    pin = adc.differential_input(1)
    
    i2c.add_response(bytes([0x80, 0x60]))
    
    # -64 in 8-bit 2's complement representation
    i2c.add_response(bytes([0xC0, 0xC0]))
    
    sample = pin.value
    
    assert i2c.request_count == 2
    
    m1a,m1b = i2c.request(0)
    assert is_write(m1a)
    assert m1a.len == 1
    assert m1a.buf[0][0] == 0b00010001
    
    assert is_read(m1b)
    assert m1b.len == 2
    
    m2, = i2c.request(1)
    assert is_read(m2)
    assert m2.len == 2
    
    assert_is_approx(-0.25, sample)


def test_sends_correct_mode_bits_for_four_single_ended_mode():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    pin = adc.single_ended_input(1)
    
    pin.get()
    
    assert i2c.request(0)[0].buf[0][0] == 0b00000001


def test_sends_correct_mode_bits_for_four_single_ended_mode():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    pin = adc.single_ended_input(1)
    
    pin.get()
    
    assert i2c.request(0)[0].buf[0][0] == 0b00000001


def test_sends_correct_mode_bits_for_two_differential_mode():
    adc = create_pcf8591(i2c, TWO_DIFFERENTIAL)

    pin = adc.differential_input(1)
    
    pin.get()
    
    assert i2c.request(0)[0].buf[0][0] == 0b00110001


def test_sends_correct_mode_bits_for_single_ended_and_differential_mode():
    adc = create_pcf8591(i2c, SINGLE_ENDED_AND_DIFFERENTIAL)
    
    pin = adc.single_ended_input(1)
    
    pin.get()
    
    assert i2c.request(0)[0].buf[0][0] == 0b00100001
    

def test_does_not_switch_channel_and_only_reads_once_for_subsequent_reads_from_same_pin():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    pin0 = adc.single_ended_input(0)
    
    sample = pin0.value
    assert i2c.request_count == 2
    
    sample = pin0.value
    assert i2c.request_count == 3
    
    sample = pin0.value
    assert i2c.request_count == 4


def test_switches_channel_and_reads_twice_when_reading_from_different_pin():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    pin0 = adc.single_ended_input(0)
    pin1 = adc.single_ended_input(1)
    
    sample = pin0.value
    assert i2c.request_count == 2
    
    sample = pin0.value
    assert i2c.request_count == 3
    
    sample = pin1.value
    assert i2c.request_count == 5
    
    ma,mb = i2c.request(3)
    assert is_write(ma)
    assert ma.len == 1
    assert ma.buf[0][0] == 0b00000001
    assert is_read(mb)
    assert mb.len == 2
    

def test_opening_and_closing_the_output_pin_turns_the_digital_to_analogue_converter_on_and_off():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    adc.output.open()
    assert i2c.request_count == 1
    m1, = i2c.request(0)
    assert is_write(m1)
    assert m1.len == 1
    assert m1.buf[0][0] == 0b01000000
    
    adc.output.close()
    assert i2c.request_count == 2
    m2, = i2c.request(1)
    assert is_write(m2)
    assert m2.len == 1
    assert m2.buf[0][0] == 0b00000000


def test_output_pin_opens_and_closes_itself_when_used_as_a_context_manager():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    with adc.output:
        assert i2c.request_count == 1
    
    assert i2c.request_count == 2


def test_setting_value_of_output_pin_sends_value_as_second_written_byte():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    with adc.output as pin:
        pin.value = 0.5
        
        assert i2c.request_count == 2
        m1, = i2c.request(1)
        assert m1.len == 2
        assert m1.buf[0][0] == 0b01000000
        assert m1.buf[1][0] == 127

        pin.value = 0.25
        
        assert i2c.request_count == 3
        m2, = i2c.request(2)
        assert m2.len == 2
        assert m2.buf[0][0] == 0b01000000
        assert m2.buf[1][0] == 63



def test_setting_value_of_output_pin_does_not_affect_currently_selected_input_pin():
    adc = create_pcf8591(i2c, FOUR_SINGLE_ENDED)
    
    with adc.output as opin:
        assert i2c.request_count == 1
        
        adc.single_ended_input(1).get()
        assert i2c.request_count == 3
        
        opin.value = 0.5
        assert i2c.request_count == 4
        assert i2c.request(3)[0].buf[0][0] == 0b01000001
        
        adc.single_ended_input(2).get()
        assert i2c.request_count == 6
        
        opin.value = 0.5
        assert i2c.request_count == 7
        assert i2c.request(6)[0].buf[0][0] == 0b01000010
