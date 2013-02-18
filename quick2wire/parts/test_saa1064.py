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


i2c = FakeI2CMaster()

def setup_function(f):
    i2c.clear()

def test_static_display_brightest_by_default():
    saa1064 = SAA1064(i2c)
    saa1064.configure()

    assert i2c.request_count == 1

    controlMessage = i2c.request(0)[0]
    assert controlMessage.len == 2
    assert controlMessage.buf[0][0] == 0b00000000
    assert controlMessage.buf[1][0] == 0b11100110


def test_dynamic_display_brightest_by_default():
    saa1064 = SAA1064(i2c)
    saa1064.mode=DYNAMIC_MODE
    saa1064.configure()

    assert i2c.request_count == 1

    controlMessage = i2c.request(0)[0]
    assert controlMessage.len == 2
    assert controlMessage.buf[0][0] == 0b00000000
    assert controlMessage.buf[1][0] == 0b11100111

def test_display_brightness():
    saa1064 = SAA1064(i2c)
    saa1064.mode=DYNAMIC_MODE
    saa1064.brightness=0b01100000
    saa1064.configure()

    assert i2c.request_count == 1

    controlMessage = i2c.request(0)[0]
    assert controlMessage.len == 2
    assert controlMessage.buf[0][0] == 0b00000000
    assert controlMessage.buf[1][0] == 0b01100111

def test_setting_pins_and_writing_outputs_to_i2c():
    saa1064 = SAA1064(i2c)
    saa1064.mode=STATIC_MODE
    saa1064.brightness=5
    saa1064.configure()

    saa1064.segment_output(0).value=1
    saa1064.segment_output(1).value=0
    saa1064.segment_output(2).value=0
    saa1064.segment_output(3).value=1
    saa1064.segment_output(4).value=1
    saa1064.segment_output(5).value=1
    saa1064.segment_output(6).value=0
    saa1064.segment_output(7).value=1

    saa1064.write()

    assert i2c.request_count == 2
    dataMessage = i2c.request(1)[0]
    assert dataMessage.len == 2
    assert dataMessage.buf[0][0] == 0b00000001
    assert dataMessage.buf[1][0] == 0b10111001
