"""
API for the LTC2309 A/D converter

The LTC2309 chip has eight input pins, named CH0 to CH7, at which it
measures voltage.  These can be configured as eight single-ended
channels, or four differential channels (CH0/CH1, CH2/CH3, CH4/CH5 or
CH6/CH7).

Applications control the chip through an object of the LTC2309 clas.
This is created with an I2CMaster, through which it communicates with
the chip.

Applications may obtain one of the single-ended channels with the
method `single_ended_input`, and one of the differential channels with
the method `differential_input`.

There are nine possible addresses which the chip can have, plus one
global address which is used to instruct a suite of LTC2309 chips to
make a conversion at the same time.  This function is available
through the method `global_sync`.

See data sheet at <http://www.linear.com/product/LTC2309>

Note that the input voltage is converted only _after_ any read or
write message to the chip (after an I2C STOP command, in fact).
Therefore if a channel is read repeatedly, the value returned is
always the value obtained after the previous read.  If two channels
are read alternately, however, then the reads are up to date (since
such an operation involves a command write, which triggers a
conversion).

For example:

    with I2CMaster() as i2c:
        adc = LTC2309(i2c, address=???)
        with adc.single_ended_input(0) as in0, adc.differential_input(2) as in2:
            print('single={}, differential2={}'.format(in0.value, in2.value)

The value of a channel is obtained by querying its `value` property.
For single-ended channels the value varies between 0 and 4.096 for
'unipolar' channels, and -2.048 and +2.048 for 'bipolar' channels,
created with single_ended_input(n, bipolar=True).  Differential
channels vary between -2.048 and +2.048.

If the channel's `sleep_after_conversion` method is called, the chip
is put into low-power sleep between conversions (as opposed to a
lowish-power 'napping' mode).

[This module originally by Octameter Computing (8ameter.com), December 2013]
"""

from quick2wire.i2c import reading, writing_bytes
from quick2wire.gpio import In

GLOBAL_ADDRESS = 0x6b

ALLOWED_ADDRESSES = (0x08, 0x09, 0x0a, 0x0b,
                     0x18, 0x19, 0x1a, 0x1b,
                     0x28)

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
        """Returns the nth differential analogue input channel from
        the set (CH0-CH1, CH2-CH3, CH4-CH5 or CH6-CH7).
        If negate=True (default False), the value is inverted, so that
        the channel CH0-CH1 becomes instead CH1-CH0."""
        if n not in range(4):
            raise ValueError("Differential input channels must be in range 0..3, not {}".format(n))
        return _InputChannel((n | (4 if negate else 0)) << 4,
                             self.read_bipolar, # ???
                             FULL_RANGE)

    def read_unipolar(self, din):
        """Return the 12-bit value of a single-ended input channel"""
        return self.read_raw(din)

    def read_bipolar(self, din):
        """Return the 12-bit value of a differential input channel"""
        v = self.read_raw(din)
        if v & 0x800:
            v -= 0x1000
        return v

    def read_raw_repeated_start(self, din):
        """Read a value using the 'repeated start' pattern, which
        means that the value returned is the value from the _previous_
        conversion, which might be unexpected, if the Din provided is
        different from the previous one.  This method is currently unused."""
        if din != self._last_din_read:
            l = (writing_bytes(self.address, din),)
            self._last_din_read = din
        else:
            l = ()
        l = l + (reading(self.address, 2),)

        results = self.master.transaction(*l)
        res = (results[0][0] << 4) + (results[0][1] >> 4)
        return res

    def read_raw(self, din):
        """Read a byte.  If the provided Din is different from the
        value which applied to the previous read, then update the Din
        value first.  Note that we do this in two transactions, so
        that the STOP at the end of the first will initiate a
        conversion, and therefore the value subsequently read will be
        done with the modified Din/channel."""
        if din != self._last_din_read:
            self.master.transaction(writing_bytes(self.address, din))
            self._last_din_read = din

        results = self.master.transaction(reading(self.address, 2))
        res = (results[0][0] << 4) + (results[0][1] >> 4)
        #print('{:x},{:x} -> {:x} = {}'.format(results[0][0], results[0][1], res, res))
        return res

    def global_sync(self):
        """Send a command to synchronise all LTC2309s on the bus,
        without changing any channel.  Although the LTC2309 supports
        including a channel-selection byte, this is not currently supported
        in this API."""
        self.master.transaction(writing_bytes(GLOBAL_ADDRESS))

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

    def sleep_after_conversion(self, sleep_p):
        """If the argument is True, then the LTC2309 will be instructed
        to go into sleep mode after each conversion"""
        if sleep_p:
            self._din = self._din | 4
        else:
            self._din = self._din & ~4

    # No-op implementations of Pin resource management API
    
    def open(self):
        pass
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        return False
