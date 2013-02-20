__author__ = 'stuartervine'

from functools import reduce
from operator import or_
from quick2wire.i2c import writing_bytes

displayController = 0x38
STATIC_MODE = 0b00000000
DYNAMIC_MODE = 0b00000001
CONTINUOUS_DISPLAY = 0b00000110

class SAA1064(object):
    def createPinBank(self, i):
        return _PinBank(i)

    def __init__(self, master, digits=1):
        self.master = master
        self._mode = STATIC_MODE
        self._brightness = 0b11100000
        self._pin_bank = tuple(self.createPinBank(i) for i in range(digits))

    def display(self, digits):
        pass

    def configure(self):
        self.master.transaction(
            writing_bytes(displayController, 0b00000000, self.mode | self.brightness | CONTINUOUS_DISPLAY)
        )

    def write(self):
        i2c_messages = [pin_bank.i2c_message for pin_bank in self._pin_bank]
        self.master.transaction(i2c_messages)

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

    def pin_bank(self, index):
        return self._pin_bank[index]

    def __getitem__(self, n):
        if 0 < n < len(self):
            raise ValueError("no pin bank index {n} out of range", n=n)
        return self._pin_bank[n]

    def __len__(self):
        return len(self._pin_bank)


class _PinBank(object):
    def __init__(self, index):
        self._value = 0
        self._segment_output = tuple(_OutputPin(self, i) for i in range(8))
        self.segment_address = index+1

    def segment_output(self, index):
        return self._segment_output[index]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def i2c_message(self):
        return writing_bytes(displayController, self.segment_address, self._value)

    def __getitem__(self, n):
        if 0 < n < len(self):
            raise ValueError("no segment output index {n} out of range", n=n)
        return self._segment_output[n]

    def __len__(self):
        return len(self._segment_output)

class _OutputPin(object):
    def __init__(self, pin_bank, index):
        self._pin_bank = pin_bank
        self._binary = 2 ** index

    @property
    def value(self):
        return self._pin_bank.value & self._binary

    @value.setter
    def value(self, value):
        self._pin_bank.value = self._pin_bank.value | (self._binary * value)