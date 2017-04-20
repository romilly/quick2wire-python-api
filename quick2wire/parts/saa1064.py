"""
API for the SAA1064 seven segment display driver chip.

The SAA1064 can drive up to 4 seven segment displays simultaneously.
There are 2 modes the chip can run in:

STATIC mode - drives 2 seven segment displays.
Where no multiplexing is required, and the outputs of the pins 3-11
and 14-22 can be connected directly to the LED displays.
[URL]

DYNAMIC mode - drives 4 seven segment displays.
The chip multiplexes the output of displays 1+3 and 2+4. The pairs
of displays are connected to the same output pins as above. The circuit
requires 2 transistors to be connected to the multiplex outputs to control
which display to trigger.

Applications talk to the chip via objects of the SAA1064 class. A
SAA1064 object is created with an I2CMaster and a number of digits between 1-4.

The display brightness can be supplied using the brightness property.
This supports values between 0-7.

The displays can then be controlled individually by setting valid values
on digits and then calling write().

For example:

    with I2CMaster() as i2c:
        saa1064 = SAA1064(i2c, digits=2)

        saa1064.digit(0).value('1')
        saa1064.digit(1).value('2')
        saa1064.write()

The current values supported for a digit are: 0-9, A-F, r

Specifying a decimal point after the value will light the point in the display.

For example:
    with I2CMaster() as i2c:
        saa1064 = SAA1064(i2c, digits=2)

        saa1064.digit(0).value('1.')

The displays are configured using the following value conversions for the display segments

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
from quick2wire.pin import PinAPI, PinBankAPI


__author__ = 'stuartervine'

from functools import reduce
from operator import or_
from quick2wire.i2c import writing_bytes

displayController = 0x38
STATIC_MODE = 0b00000000
DYNAMIC_MODE = 0b00000001
CONTINUOUS_DISPLAY = 0b00000110

DECIMAL_POINT = 0b10000000

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
    def create_pin_bank(self, i):
        return _PinBank(i)

    def __init__(self, master, digits=1, brightness=7):
        self.master = master
        self.brightness = brightness
        self.configured = False

        if digits <= 0 or digits > 4:
            raise ValueError('SAA1064 only supports driving 1 to 4 digits')
        elif digits <= 2:
            self._mode = STATIC_MODE
        else:
            self._mode = DYNAMIC_MODE

        self._pin_bank = tuple(self.create_pin_bank(i) for i in range(digits))

    def configure(self):
        """Writes the configured control byte to the chip."""
        self.write_control(self.mode|self._brightness|CONTINUOUS_DISPLAY)

    def reset(self):
        for pin_bank in self:
            pin_bank.value = 0

    def write_control(self, control_byte):
        """Writes a raw control byte to the chip."""
        self.master.transaction(
            writing_bytes(displayController, 0b00000000, control_byte)
        )
        self.configured = True

    def write(self):
        """Writes the segment outputs to the chip."""
        if(not self.configured):
            self.configure()

        i2c_messages = [pin_bank.i2c_message for pin_bank in self._pin_bank]
        self.master.transaction(*i2c_messages)

    @property
    def mode(self):
        """Returns the display mode the chip is currently configured in, 0: static, 1: dynamic"""
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Changes the display mode the chip is configured in."""
        if mode > 1 or mode < 0:
            raise ValueError('invalid mode ' + str(mode) + ' only STATIC_MODE and DYNAMIC_MODE are supported')
        self._mode = mode

    @property
    def brightness(self):
        """Returns the current brightness level configured for the LED displays."""
        return self._brightness >> 5

    @brightness.setter
    def brightness(self, brightness):
        """Sets the brightness of the LED displays, between 0-7."""
        if brightness > 7:
            raise ValueError('invalid brightness, valid between 0-7.')
        self._brightness = brightness << 5

    def digit(self, index):
        """Returns a Digit object for the display at given 'index'."""
        return Digit(self._pin_bank[index])

    def bank(self, index):
        """Returns a PinBank object for the display at given 'index'."""
        return self._pin_bank[index]

    def __getitem__(self, n):
        """Allows the SAA1064 to iterate through it's pin banks."""
        if 0 < n < len(self):
            raise ValueError('no pin bank index {n} out of range', n=n)
        return self._pin_bank[n]

    def __len__(self):
        return len(self._pin_bank)

class Digit(object):
    def __init__(self, pin_bank):
        self._pin_bank = pin_bank

    value = property(lambda p: p.get(),
                     lambda p,v: p.set(v),
                     doc="""The value represented by the digit""")

    def get(self):
        return self._pin_bank.value

    def set(self, new_value):
        digit = str(new_value)
        try:
            byte_value = digit_map[digit[:1]]
            if digit.find(".") > -1:
                byte_value |= DECIMAL_POINT
            self._pin_bank.value=byte_value
        except:
            raise ValueError('cannot display digit ' + new_value)


class _PinBank(PinBankAPI):

    def __init__(self, index):
        super(_PinBank,self).__init__()
        self._value = 0
        self._segment_output = tuple(_OutputPin(self, i) for i in range(8))
        self.segment_address = index+1

    def segment_output(self, index):
        return self._segment_output[index]

    pin = segment_output

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

class _OutputPin(PinAPI):
    def __init__(self, pin_bank, index):
        super(_OutputPin,self).__init__(pin_bank, index)
        self._binary = 1 << index

    def open(self):
        pass

    def close(self):
        pass

    def get(self):
        """The current value of the pin: 1 if the pin is high or 0 if the pin is low."""
        return (self._bank.value & (1 << self._index)) >> self._index

    def set(self, new_value):
        self._bank.value = self._bank.value | (self._binary * new_value)
