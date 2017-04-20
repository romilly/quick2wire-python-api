import re

__author__ = 'stuartervine'

class SevenSegmentDisplay(object):
    def __init__(self, driver_chip):
        self._driver_chip = driver_chip

    def display(self, value):
        self._driver_chip.reset()

        digit_values = re.findall(".\.?", str(value))
        for i, digit_value in zip(reversed(range(len(self._driver_chip))), reversed(digit_values)):
            self._driver_chip.digit(i).value=digit_value

        self._driver_chip.write()

