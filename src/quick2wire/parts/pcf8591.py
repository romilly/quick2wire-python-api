from quick2wire.i2c import writing_bytes, reading

ANALOGUE_OUT = 1 << 6

FOUR_SINGLE_ENDED = 0
THREE_DIFFERENTIAL = 1
SINGLE_ENDED_AND_DIFFERENTIAL = 2
TWO_DIFFERENTIAL = 3

class PCF8591:
    """Access to the PCF8591 A/D and D/A converter"""

    def __init__ (self, master, address = 0x48):
        self.master = master
        self.address = address
        self._control = 0

    @property
    def input_channel(self):
        """
        Channel that will be converted on next read command 
        """
        return self._control & 7

    @property
    def autoincrement(self):
        """
        Enables the auto increment flag for reads
        """
        return self._control & 8 == 8

    @property
    def inputs(self):
        """ 
        Selects the input configuration. Supply one of FOUR_SINGLE_ENDED, 
        THREE_DIFFERENTIAL, SINGLE_ENDED_AND_DIFFERENTIAL, or TWO_DIFFERENTIAL
        """
        return self._control & 0x30 >> 4

    def begin_analogue_read(self, channel, set=FOUR_SINGLE_ENDED):
        """
        Selects an analogue input configuration. The specified channel
        will be enabled in the configuration set (which defaults to FOUR_SINGLE_ENDED)
        """

        self._control = ANALOGUE_OUT | set << 4 | channel
        self.master.transaction(writing_bytes(self.address, self._control))
        return SingleInputPin(self, self._control & 0x3f)

    def read(self, count=1):
        """ 
        Read the next conversion with the current input channel and 
        programming
        """
        return self.master.transaction(reading(self.address, count))[0][0]

    def analogue_out(self, value):
        self._control = ANALOGUE_OUT | self._control
        self.master.transaction(writing_bytes(self.address, self._control, value))

    def _validate_input(self, config):
        """Resets the input configuration to the supplied configuration"""
        if (self._control & 0x3f) != config:
            self._control = self._control & 0x40 | config
            self.master.transaction(writing_bytes(self.address, self._control))

class SingleInputPin:
    def __init__(self, chip, input_config):
        self._chip = chip
        self._input_config = input_config

    @property
    def chip(self):
        return self._chip

    def read(self):
        """Read a single value from the PCF8591"""
        self.chip._validate_input(self._input_config)
        return self.chip.read(1)[0]
