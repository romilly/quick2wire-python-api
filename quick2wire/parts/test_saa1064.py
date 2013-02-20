from quick2wire.i2c_ctypes import I2C_M_RD
from quick2wire.parts.saa1064 import SAA1064, STATIC_MODE, DYNAMIC_MODE

__author__ = 'stuartervine'


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
        return []

    def add_response(self, *messages):
        self._responses.append(messages)


    @property
    def request_count(self):
        return len(self._requests)


    def request(self, n):
        return self._requests[n]

    def message(self, request_index, message_index):
        request = self.request(0)
        return I2CMessageWrapper(request[request_index][message_index])

class I2CMessageWrapper:
    def __init__(self, i2_message):
        self._i2c_message = i2_message
        self.len = i2_message.len

    def byte(self, index):
        return self._i2c_message.buf[index][0]

i2c = FakeI2CMaster()

def setup_function(f):
    i2c.clear()

def test_static_non_blanked_brightest_display_by_default():
    saa1064 = SAA1064(i2c)
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
    dataMessage = i2c.message(0, 0)
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

    message1 = i2c.message(0, 0)
    assert message1.len == 2
    assert message1.byte(0) == 0b00000001
    assert message1.byte(1) == 0b00000101

    message2 = i2c.message(0, 1)
    assert message2.len == 2
    assert message2.byte(0) == 0b00000010
    assert message2.byte(1) == 0b01010000
