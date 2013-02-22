import pytest
from quick2wire.i2c_ctypes import I2C_M_RD
from quick2wire.parts.fake_i2c import FakeI2CMaster
from quick2wire.parts.saa1064 import SAA1064, STATIC_MODE, DYNAMIC_MODE

__author__ = 'stuartervine'

i2c = FakeI2CMaster()

def setup_function(f):
    i2c.clear()

def test_cannot_be_created_with_invalid_number_of_digits():
    with pytest.raises(ValueError):
        SAA1064(i2c, digits=5)

def test_static_non_blanked_brightest_display_single_digit_by_default():
    saa1064 = SAA1064(i2c)
    assert len(saa1064._pin_bank) == 1

    saa1064.configure()
    assert i2c.request_count == 1

    controlMessage = i2c.request(0)[0]
    assert controlMessage.len == 2
    assert controlMessage.buf[0][0] == 0b00000000
    assert controlMessage.buf[1][0] == 0b11100110

def test_configuring_dynamic_display():
    saa1064 = SAA1064(i2c)
    saa1064.mode=DYNAMIC_MODE
    saa1064.configure()

    assert i2c.request_count == 1

    controlMessage = i2c.request(0)[0]
    assert controlMessage.len == 2
    assert controlMessage.buf[0][0] == 0b00000000
    assert controlMessage.buf[1][0] == 0b11100111

def test_configuring_display_brightness():
    saa1064 = SAA1064(i2c)
    saa1064.mode=DYNAMIC_MODE
    saa1064.brightness=0b01100000
    saa1064.configure()

    assert i2c.request_count == 1

    controlMessage = i2c.request(0)[0]
    assert controlMessage.len == 2
    assert controlMessage.buf[0][0] == 0b00000000
    assert controlMessage.buf[1][0] == 0b01100111

def test_cannot_be_configured_with_invalid_mode():
    saa1064 = SAA1064(i2c)
    with pytest.raises(ValueError):
        saa1064.mode=99

def test_writing_single_digit_segment_outputs_to_i2c():
    saa1064 = SAA1064(i2c, digits=1)

    saa1064.pin_bank(0).segment_output(0).value=1
    saa1064.pin_bank(0).segment_output(1).value=0
    saa1064.pin_bank(0).segment_output(2).value=0
    saa1064.pin_bank(0).segment_output(3).value=1
    saa1064.pin_bank(0).segment_output(4).value=1
    saa1064.pin_bank(0).segment_output(5).value=1
    saa1064.pin_bank(0).segment_output(6).value=0
    saa1064.pin_bank(0).segment_output(7).value=1
    saa1064.write()

    assert i2c.request_count == 1
    dataMessage = i2c.message(0)
    assert dataMessage.len == 2
    assert dataMessage.byte(0) == 0b00000001
    assert dataMessage.byte(1) == 0b10111001

def test_writing_two_digit_segment_outputs_to_i2c():
    saa1064 = SAA1064(i2c, digits=2)

    saa1064.pin_bank(0).segment_output(0).value=1
    saa1064.pin_bank(0).segment_output(1).value=0
    saa1064.pin_bank(0).segment_output(2).value=1
    saa1064.pin_bank(0).segment_output(3).value=0
    saa1064.pin_bank(0).segment_output(4).value=0
    saa1064.pin_bank(0).segment_output(5).value=0
    saa1064.pin_bank(0).segment_output(6).value=0
    saa1064.pin_bank(0).segment_output(7).value=0

    saa1064.pin_bank(1).segment_output(0).value=0
    saa1064.pin_bank(1).segment_output(1).value=0
    saa1064.pin_bank(1).segment_output(2).value=0
    saa1064.pin_bank(1).segment_output(3).value=0
    saa1064.pin_bank(1).segment_output(4).value=1
    saa1064.pin_bank(1).segment_output(5).value=0
    saa1064.pin_bank(1).segment_output(6).value=1
    saa1064.pin_bank(1).segment_output(7).value=0
    saa1064.write()

    assert i2c.request_count == 1

    message1 = i2c.message(0)
    assert message1.len == 2
    assert message1.byte(0) == 0b00000001
    assert message1.byte(1) == 0b00000101

    message2 = i2c.message(1)
    assert message2.len == 2
    assert message2.byte(0) == 0b00000010
    assert message2.byte(1) == 0b01010000

def test_writing_four_digit_segment_outputs_to_i2c():
    saa1064 = SAA1064(i2c, digits=4)

    saa1064.pin_bank(0).value=255
    saa1064.pin_bank(1).value=127
    saa1064.pin_bank(2).value=63
    saa1064.pin_bank(3).value=31
    saa1064.write()

    assert i2c.request_count == 1

    message1 = i2c.message(0)
    assert message1.len == 2
    assert message1.byte(0) == 1
    assert message1.byte(1) == 255

    message2 = i2c.message(1)
    assert message2.len == 2
    assert message2.byte(0) == 2
    assert message2.byte(1) == 127

    message3 = i2c.message(2)
    assert message3.len == 2
    assert message3.byte(0) == 3
    assert message3.byte(1) == 63

    message4 = i2c.message(3)
    assert message4.len == 2
    assert message4.byte(0) == 4
    assert message4.byte(1) == 31

def test_digits_are_mapped_into_correct_i2c_message():
    saa1064 = SAA1064(i2c, digits=2)

    saa1064.digit(0).value('9')
    saa1064.digit(1).value('5')
    saa1064.write()

    assert i2c.request_count == 1
    message1 = i2c.message(0)
    assert message1.len == 2
    assert message1.byte(0) == 1
    assert message1.byte(1) == 123

    message2 = i2c.message(1)
    assert message2.len == 2
    assert message2.byte(0) == 2
    assert message2.byte(1) == 91

def test_digits_can_be_set_using_integer_value():
    saa1064 = SAA1064(i2c, digits=2)

    saa1064.digit(0).value(9)
    saa1064.write()

    assert i2c.request_count == 1
    message1 = i2c.message(0)
    assert message1.len == 2
    assert message1.byte(0) == 1
    assert message1.byte(1) == 123

def test_does_not_accept_invalid_digit_values():
    saa1064 = SAA1064(i2c, digits=2)

    with pytest.raises(ValueError):
        saa1064.digit(0).value('@')
