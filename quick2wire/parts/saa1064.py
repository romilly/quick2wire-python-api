from functools import reduce
from operator import or_

__author__ = 'stuartervine'

from quick2wire.i2c import writing_bytes

displayController = 0x38
STATIC_MODE = 0b00000000
DYNAMIC_MODE = 0b00000001
CONTINUOUS_DISPLAY = 0b00000110

class SAA1064(object):
    def __init__(self, master):
        self.master = master
        self._mode = STATIC_MODE
        self._brightness = 0b11100000
        self._segment_output = tuple(_OutputPin(i) for i in range(8))

    def display(self, digits):
        pass

    def configure(self):
        self.master.transaction(
            writing_bytes(displayController, 0b00000000, self.mode | self.brightness | CONTINUOUS_DISPLAY)
        )

    def write(self):
        bits_to_write = [output.asBinary for output in self._segment_output]
        byte_to_write = reduce(or_, bits_to_write)
        self.master.transaction(
            writing_bytes(displayController, 0b00000001, byte_to_write)
        )

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = value

    def segment_output(self, index):
        return self._segment_output[index]


class _OutputPin(object):
    def __init__(self, index):
        self._value = 0
        self._binary = 2 ** index

    @property
    def asBinary(self):
        return self._value * self._binary

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value