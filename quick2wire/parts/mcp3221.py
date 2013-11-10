"""
API for the MCP3221 A/D converter.

The MCP3221 chip provides a single 12-bit measurement of an input
analogue value, available through one single-ended channel.

Applications talk to the chip via objects of the MCP3221 class.
When an MCP3221 object is created, it is passed a single I2CMaster,
through which it communicates.

For example:

    with I2CMaster() as i2c:
        adc = MCP3221(i2c)
        input = adc.single_ended_input
        print("{}".format(input.value))

The A/D signal is obtained by querying the channel's 'value' property,
which varies in the range 0.0 <= value < 1.0.

[This module originally by Octameter computing (8ameter.com),
funded by Anacail (anacail.com); November 2013.]
"""

from quick2wire.i2c import reading
from quick2wire.gpio import In

# According to the MCP3221 documentation, the base address is 0x48
# (in the sense that the device's 'device code' is 0x48), with an
# 'address' comprised of the following three bits, which default to
# 101.  Therefore the base address is 0x48, and the default address is 0x4d.
BASE_ADDRESS = 0x48

class MCP3221(object):
    """PI to query and control an MCP3221 A/D converter via I2C.

    For the MCP3221, "If [...] the voltage level of AIN is equal to or
    less than VSS + 1/2 LSB, the resultant code will be
    000h. Additionally, if the voltage at AIN is equal to or greater
    than VDD - 1.5 LSB, the output code will be FFFh."  Therefore,
    the full scale, corresponding to VSS+1.0*(VDD-VSS), is 1000h,
    but the maximum floating-point value that can be returned is FFFh/1000h.
    """

    def __init__(self, master, address=5):
        """Initialises an MCP3221.

        Parameters:
        master  -- the I2CMaster with which to commmunicate with the
                   MCP3221 chip.
        address -- the I2C address of the MCP3221 chip, as a number in [0..7]
                   (optional, default = 5)
        """
        self.master = master
        self.address = BASE_ADDRESS + address

        if address < 0 or address >= 8:
            raise ValueError("Invalid address {} (should be in [0..7]".format(address))
        else:
            self._single_ended_input = _InputChannel(self.read_single_ended, 0x1000*1.0)

    @property
    def direction(self):
        return In

    @property
    def single_ended_input(self):
        return self._single_ended_input

    def read_single_ended(self):
        """Read the 8-bit value of a single-ended input channel."""
        return self.read_raw()

    def read_raw(self):
        results = self.master.transaction(reading(self.address, 2))
        # results is a (single-element) list of reads;
        # each read is a two-byte array
        r = results[0]
        return r[0]*0x100 + r[1]


class _InputChannel(object):
    def __init__(self, read_fn, scale):
        self._read = read_fn
        self._scale = scale

    @property
    def direction(self):
        return In

    @property
    def value(self):
        return self.get_raw() / self._scale

    def get_raw(self):
        return self._read()

    # Expose the value as a property.  The property and the underlying
    # function must be distinct, since value(self) calls get_raw().
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
