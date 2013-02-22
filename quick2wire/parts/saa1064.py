__author__ = 'stuartervine'

from functools import reduce
from operator import or_
from quick2wire.i2c import writing_bytes

displayController = 0x38
STATIC_MODE = 0b00000000
DYNAMIC_MODE = 0b00000001
CONTINUOUS_DISPLAY = 0b00000110

"""
    Value conversions for the display segments

         --64--
        |      |
        2      32
        |      |
         -- 1--
        |      |
        4      16
        |      |
         -- 8--   DP-128
    """
digit_map = {
    '0':126,
    '1':48,
    '2':109,
    '3':121,
    '4':51,
    '5':91,
    '6':95,
    '7':112,
    '8':127,
    '9':123,
    'A':119,
    'B':31,
    'C':78,
    'D':61,
    'E':79,
    'F':71,
    'R':5
}

class SAA1064(object):
    def createPinBank(self, i):
        return _PinBank(i)

    def __init__(self, master, digits=1):
        self.master = master
        self._mode = STATIC_MODE
        self._brightness = 0b11100000
        if(digits > 4):
            raise ValueError('SAA1064 only supports driving up to 4 digits')
        self._pin_bank = tuple(self.createPinBank(i) for i in range(digits))

    def display(self, digits):
        pass

    def configure(self):
        self.write_control(self.mode|self._brightness|CONTINUOUS_DISPLAY)

    def write_control(self, control_byte):
        self.master.transaction(
            writing_bytes(displayController, 0b00000000, control_byte)
        )

    def write(self):
        i2c_messages = [pin_bank.i2c_message for pin_bank in self._pin_bank]
        self.master.transaction(*i2c_messages)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        if(mode > 1):
            raise ValueError('invalid mode ' + str(mode) + ' only STATIC_MODE and DYNAMIC_MODE are supported')
        self._mode = mode

    @property
    def brightness(self):
        return self._brightness >> 5

    @brightness.setter
    def brightness(self, brightness):
        if(brightness > 7):
            raise ValueError('invalid brightness, valid between 0-7.')
        self._brightness = brightness << 5

    def digit(self, index):
        return Digit(self._pin_bank[index])

    def pin_bank(self, index):
        return self._pin_bank[index]

    def __getitem__(self, n):
        if 0 < n < len(self):
            raise ValueError('no pin bank index {n} out of range', n=n)
        return self._pin_bank[n]

    def __len__(self):
        return len(self._pin_bank)

class Digit(object):
    def __init__(self, pin_bank):
        self._pin_bank = pin_bank

    def value(self, value):
        try:
            self._pin_bank.value=digit_map[str(value)]
        except:
            raise ValueError('cannot display digit ' + value)

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
            raise ValueError('no segment output index {n} out of range', n=n)
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