"""
API for the LTC2309 A/D converter

See data sheet at <http://www.linear.com/product/LTC2309>

This module is currently incomplete:
  * The support for differential channels is untested
  * Repeated-START reading is untested
  * No support for napping/sleeping

[This module originally by Octameter Computing (8ameter.com), December 2013]
"""

from quick2wire.i2c import reading, writing_bytes
from quick2wire.gpio import In

GLOBAL_ADDRESS = 0x6b

ALLOWED_ADDRESSES = (0x08, 0x09, 0x0a, 0x0b,
                     0x18, 0x19, 0x1a, 0x1b,
                     0x28,
                     GLOBAL_ADDRESS)

# Full scale, unipolar; bipolar is [-FS/2..FS/2]
FULL_RANGE = 4.096

class LTC2309(object):
    """API to control an LTC2309 A/D converter via I2C."""

    def __init__(self, master, address=0x08):
        """Initialises an LTC2309.

        Parameters:
        master  -- the I2CMaster with which to commmunicate with the
                   LTC2309 chip.
        address -- the I2C address of the LTC2309 chip, which can be in
                   (0x08, 0x09, 0x0a, 0x0b, 0x18, 0x19, 0x1a, 0x1b, 0x28),
                   or the global address 0x6b
                   [optional, default=0x08]
        """
        self.master = master

        if address not in ALLOWED_ADDRESSES:
            raise ValueError("Invalid address {}".format(address))

        self.address = address
        self._last_din_read = 0x00 # reading differential channel 0

    @property
    def direction(self):
        return In

    def single_ended_input(self, n, bipolar=False):
        """Returns the nth single-ended analogue input channel.
        If bipolar=True (default False) the channel is signed. """
        if n not in range(8):
            raise ValueError("Single-ended input channels must be in range 0..7, not {}".format(n))
        dins = [ 0x80, 0xc0, 0x90, 0xd0, 0xa0, 0xe0, 0xb0, 0xf0 ]
        if bipolar:
            return _InputChannel(dins[n],
                                 self.read_bipolar,
                                 FULL_RANGE)
        else:
            return _InputChannel(dins[n] | 0x8,
                                 self.read_unipolar,
                                 FULL_RANGE)

    def differential_input(self, n, negate=False):
        """Returns the nth differential analogue input channel.
        If negate=True (default False), the value is inverted."""
        if n not in range(4):
            raise ValueError("Differential input channels must be in range 0..3, not {}".format(n))
        return _InputChannel((n | (4 if negate else 0)) << 4,
                             self.read_bipolar, # ???
                             -FULL_RANGE if negate else FULL_RANGE)

    def read_unipolar(self, din):
        """Return the 12-bit value of a single-ended input channel"""
        return self.read_raw(din)

    def read_bipolar(self, din):
        """Return the 12-bit value of a differential input channel"""
        v = self.read_raw(din)
        if v & 0x800:
            v -= 0x1000
        return v

    def read_raw(self, din):
        if din != self._last_din_read:
            self.master.transaction(writing_bytes(self.address, din))#XXX???
            self._last_din_read = din

        results = self.master.transaction(reading(self.address, 2))
        res = (results[0][0] << 4) + (results[0][1] >> 4)
        return res

class _InputChannel(object):
    def __init__(self, din, read_fn, full_range):
        self._din = din
        self._read = read_fn
        self._range = full_range / 4096

    @property
    def direction(self):
        return In

    def get(self):
        return self.get_raw() * self._range
    value = property(get)

    def get_raw(self):
        return self._read(self._din)
    raw_value = property(get_raw)

    # No-op implementations of Pin resource management API
    
    def open(self):
        pass
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        return False
