from quick2wire.parts.saa1064 import DECIMAL_POINT
from quick2wire.parts.seven_segment_display import SevenSegmentDisplay

__author__ = 'stuartervine'

class FakeDigit(object):
    def __init__(self):
        self.value = 0

class FakeSAA1064(object):
    def __init__(self):
        self._fake_digits = [FakeDigit() for x in range(4)]

    def reset(self):
        for digit in self._fake_digits:
            digit.value = 0

    def digit(self, index):
        return self._fake_digits[index]

    def write(self):
        pass

    def __len__(self):
        return len(self._fake_digits)

saa1064 = FakeSAA1064()

def test_cannot_be_created_with_invalid_number_of_digits():
    display = SevenSegmentDisplay(saa1064)
    display.display('1234')
    assert saa1064.digit(0).value == '1'
    assert saa1064.digit(1).value == '2'
    assert saa1064.digit(2).value == '3'
    assert saa1064.digit(3).value == '4'

def test_shows_decimal_point():
    display = SevenSegmentDisplay(saa1064)
    display.display('0.123')
    assert saa1064.digit(0).value == '0.'
    assert saa1064.digit(1).value == '1'
    assert saa1064.digit(2).value == '2'
    assert saa1064.digit(3).value == '3'

def test_hands_through_potentially_undisplayable_values():
    display = SevenSegmentDisplay(saa1064)
    display.display('@')
    assert saa1064.digit(3).value == '@'

def test_pads_unused_digits_when_not_all_are_used():
    display = SevenSegmentDisplay(saa1064)
    display.display('12')
    assert saa1064.digit(0).value == 0
    assert saa1064.digit(1).value == 0
    assert saa1064.digit(2).value == '1'
    assert saa1064.digit(3).value == '2'

