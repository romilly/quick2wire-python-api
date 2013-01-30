from quick2wire.i2c import writing_bytes, reading
from quick2wire.gpio import Out, In

DEFAULT_ADDRESS = 0x48

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
        self.bank._disable_output()
    
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


class PCF8591(object):
    """Access to the PCF8591 A/D and D/A converter"""
    
    def __init__(self, master, mode, address=DEFAULT_ADDRESS, samples=3):
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
        self._write_control_flags()
    
    def _disable_output(self):
        self._control_flags &= ~ANALOGUE_OUTPUT_ENABLE_FLAG
        self._write_control_flags()
    
    def _write_control_flags(self):
        if self._last_channel_read is None:
            self._last_channel_read = 0
        
        self.master.transaction(
            writing_bytes(self.address, self._control_flags|self._last_channel_read))
        
    def write(self, value):
        int_value = min(max(0, int(value*255)), 0xFF)
        
        if self._last_channel_read is None:
            self._last_channel_read = 0
        
        self.master.transaction(
            writing_bytes(self.address, self._control_flags|self._last_channel_read, int_value))
    
    def read(self, channel):
        if channel != self._last_channel_read:
            self.master.transaction(writing_bytes(self.address, self._control_flags|channel))
            self._last_channel_read = channel
        
        for i in range(self.samples):
            results = self.master.transaction(reading(self.address, 1))
        
        return results[0][0] / 255.0

