import re

__author__ = 'stuartervine'

class SevenSegmentDisplay(object):
    def __init__(self, driver_chip):
        self._driver_chip = driver_chip

    def display(self, value):
        digit_values = re.findall(".\.?", value)
        digit_index=0
        for digit_value in digit_values:
            self._driver_chip.digit(digit_index).value = digit_value
            digit_index += 1

