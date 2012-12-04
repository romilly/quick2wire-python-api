from quick2wire.i2c import writing_bytes, reading

ANALOGE_OUT = 1 << 6
ANALOGE_IN = 0

FOUR_SINGLE_ENDED = 0
THREE_DIFFERENTIAL = 1
SINGLE_ENDED_AND_DIFFERENTIAL = 2
TWO_DIFFERENTIAL = 3

class PCF8591:
    """Access to the PCF8591 A/D and D/A converter"""

    def __init__ (self, master, address):
        self.master = master
        self.address = address

    def begin_analoge_in(self, input_pins, auto_increment, channel):
        control = (input_pins << 4) | (1 << 2 if auto_increment else 0) | channel
        self.master.transaction(
                writing_bytes(self.address, control))

    def read(self, count=1):
        values = self.master.transaction(reading(self.address, count))[0]
        return values

    def analoge_out(self, value):
        control = ANALOGE_OUT
        self.master.transaction(self.writing_bytes(self.address, control, value))

