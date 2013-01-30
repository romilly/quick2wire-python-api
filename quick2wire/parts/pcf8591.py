from quick2wire.i2c import writing_bytes, reading
from quick2wire.gpio import Out, In


FOUR_SINGLE_ENDED = 0
THREE_DIFFERENTIAL = 1
SINGLE_ENDED_AND_DIFFERENTIAL = 2
TWO_DIFFERENTIAL = 3

ANALOGUE_OUTPUT_ENABLE_FLAG = 1 << 6


def _input_count(mode):
    if mode == FOUR_SINGLE_ENDED:
        return 4
    elif mode == TWO_DIFFERENTIAL:
        return 2
    else:
        return 3


class OutputPin(object):
    def __init__(self, bank):
        self.bank = bank
        self._value = 0x80
    
    def open(self):
        self.bank._enable_output()
    
    def close(self):
        self.bank._close_output()
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *exc):
        self.close()
        return False
    
    @property
    def direction(self):
        return Out
    
    def get(self):
        return self._value
    
    def set(self, value):
        self._value = value
        self.bank.write(self._value)
    
    value = property(get, set)


class InputPin(object):
    def __init__(self, bank, index):
        self.bank = bank
        self.index = index
    
    @property
    def direction(self):
        return In
    
    def get(self):
        return self.bank.read(self.index)
    
    value = property(get)
    
    # No-op implementations of Pin resource management API
    
    def open(self):
        pass
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        return False


class PinBank(object):
    def __init__(self, master, mode, address=0x48, samples=3):
        self.master = master
        self.address = address
        self._control_flags = (mode << 4)
        self._last_channel_read = None
        self._output = OutputPin(self)
        self._inputs = tuple([InputPin(self,i) for i in range(_input_count(mode))])
        self.samples = samples
    
    @property
    def output_pin(self):
        return self._output
    
    @property
    def input_count(self):
        return len(self._inputs)

    def input_pin(self, n):
        return self._inputs[n]
    
    def _enable_output(self):
        self._control_flags |= ANALOGUE_OUTPUT_ENABLE_FLAG
    
    def _disable_output(self):
        self._control_flags &= ~ANALOGUE_OUTPUT_ENABLE_FLAG
    
    def write(self, value):
        self.master.transaction(
            writing_bytes(control_flags, (value*255) & 0xFF))
    
    def read(self, channel):
        if channel != self._last_channel_read:
            self.master.transaction(writing_bytes(self.address, self._control_flags|channel))
            self._last_channel_read = channel
        
        for i in range(self.samples):
            results = self.master.transaction(reading(self.address, 1))
        
        return results[0][0] / 255.0


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

        self._control = ANALOGUE_OUTPUT_ENABLE_FLAG | set << 4 | channel
        self.master.transaction(writing_bytes(self.address, self._control))
        return SingleInputPin(self, self._control & 0x3f)

    def read(self, count=1):
        """ 
        Read the next conversion with the current input channel and 
        programming
        """
        return self.master.transaction(reading(self.address, count))[0]

    def analogue_out(self, value):
        self._control = ANALOGUE_OUTPUT_ENABLE_FLAG | self._control
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
