"""
Application-programming interface for the PCF8591 I2C A/D D/A converter.
"""

from ctypes import c_int8
from quick2wire.i2c import writing_bytes, reading
from quick2wire.gpio import Out, In

DEFAULT_ADDRESS = 0x48

FOUR_SINGLE_ENDED = 0
THREE_DIFFERENTIAL = 1
SINGLE_ENDED_AND_DIFFERENTIAL = 2
TWO_DIFFERENTIAL = 3

_ANALOGUE_OUTPUT_ENABLE_FLAG = 1 << 6



class _OutputChannel(object):
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


class _InputChannel(object):
    def __init__(self, bank, index, read_fn):
        self.bank = bank
        self.index = index
        self._read = read_fn
    
    @property
    def direction(self):
        return In
    
    def get(self):
        return self._read(self.index)
    
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
    """API to query and control an PCF8591 A/D and D/A converter via I2C"""
    
    def __init__(self, master, mode, address=DEFAULT_ADDRESS, samples=3):
        self.master = master
        self.address = address
        self.samples = samples
        self._control_flags = (mode << 4)
        self._last_channel_read = None
        self._output = _OutputChannel(self)
        
        if mode == FOUR_SINGLE_ENDED:
            self._single_ended_inputs = tuple(_InputChannel(self,i,self.read_single_ended) for i in range(4))
            self._differential_inputs = ()
        elif mode == TWO_DIFFERENTIAL:
            self._single_ended_inputs = ()
            self._differential_inputs = tuple(_InputChannel(self,i,self.read_differential) for i in range(2))
        elif mode == SINGLE_ENDED_AND_DIFFERENTIAL:
            self._single_ended_inputs = tuple(_InputChannel(self,i,self.read_single_ended) for i in (0,1))
            self._differential_inputs = (_InputChannel(self,2,self.read_differential),)
        elif mode == THREE_DIFFERENTIAL:
            self._single_ended_inputs = ()
            self._differential_inputs = tuple(_InputChannel(self,i,self.read_differential) for i in range(3))
    
    @property
    def output(self):
        """The single analogue output channel"""
        return self._output
    
    @property
    def single_ended_input_count(self):
        """The number of single-ended analogue input channels"""
        return len(self._single_ended_inputs)
    
    def single_ended_input(self, n):
        """Returns the n'th single-ended analogue input channel"""        
        return self._single_ended_inputs[n]
    
    @property
    def differential_input_count(self):
        """The number of differential analogue input channels"""
        return len(self._differential_inputs)
    
    def differential_input(self, n):
        """Returns the n'th differential analogue input channel"""        
        return self._differential_inputs[n]
    
    def _enable_output(self):
        self._control_flags |= _ANALOGUE_OUTPUT_ENABLE_FLAG
        self._write_control_flags()
    
    def _disable_output(self):
        self._control_flags &= ~_ANALOGUE_OUTPUT_ENABLE_FLAG
        self._write_control_flags()
    
    def _write_control_flags(self):
        if self._last_channel_read is None:
            self._last_channel_read = 0
        
        self.master.transaction(
            writing_bytes(self.address, self._control_flags|self._last_channel_read))
    
    def write(self, value):
        self.write_raw(min(max(0, int(value*255)), 0xFF))
        
    def write_raw(self, int_value):
        if self._last_channel_read is None:
            self._last_channel_read = 0
        
        self.master.transaction(
            writing_bytes(self.address, self._control_flags|self._last_channel_read, int_value))
    
    def read_single_ended(self, channel):
        return self.read_raw(channel) / 255.0
    
    def read_differential(self, channel):
        return c_int8(self.read_raw(channel)).value / 128.0
    
    def read_raw(self, channel):
        if channel != self._last_channel_read:
            self.master.transaction(writing_bytes(self.address, self._control_flags|channel))
            self._last_channel_read = channel
        
        for i in range(self.samples):
            results = self.master.transaction(reading(self.address, 1))
        
        return results[0][0]
