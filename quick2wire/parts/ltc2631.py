"""
API for the LTC2631 D/A converter.

The LTC2631 is a family of 12-, 10-, and 8-bit voltage-output DACs
with an integrated, high accuracy, low-drift reference.

The LTC2631-L has a full-scale output of 2.5V, and operates from a
single 2.7V to 5.5V supply. The LTC2631-H has a full-scale output of
4.096V, and operates from a 4.5V to 5.5V supply.

Each DAC can also operate in External Reference mode, in which a
voltage supplied to the REF pin sets the full-scale output
(this mode is not currently supported in this API).

See data sheet at http://www.linear.com/product/LTC2631

Applications talk to the chip via objects of the LTC2631 class.
When an LTC2631 object is created, it is passed a single I2CMaster,
through which it communicates.

For example:

    with I2CMaster() as i2c:
        adc = LTC2631(i2c)
        with adc.output as output:
            # assert 2V as the output voltage
            output.set(2.0)
            ....more

The chip is returned to its power-off mode when the program exits the
'output' block (so the above program isn't useful as it stands).

[This module originally by Octameter computing (8ameter.com), December 2013]
"""

from quick2wire.i2c import writing_bytes
from quick2wire.gpio import Out

GLOBAL_ADDRESS = 0x73

# For variant codes, see data sheet p3
Z_ADDRESSES = (0x10, 0x11, 0x12, 0x13,
               0x20, 0x21, 0x22, 0x23,
               0x30,
               GLOBAL_ADDRESS)
M_ADDRESSES = (0x10, 0x11, 0x12,
               GLOBAL_ADDRESS)

class Variant(object):
    def __init__(self, is_4v, is_zero_reset, nbits):
        self._is_zero_reset = is_zero_reset
        self._is_4v = is_4v
        self._nbits = nbits

    def nbits(self):
        return self._nbits

    def addresses(self):
        if self._is_zero_reset:
            return Z_ADDRESSES
        else:
            return M_ADDRESSES

    def full_scale(self):
        if self._is_4v:
            return 4.096
        else:
            return 2.5

    def reset_to_zero_p(self):
        return self._is_zero_reset        

    def vout(self, voltage):
        """Given a desired voltage, returns the DAC input, k, such that
        V_out = (k/2^N) Vref.
        The result is an int, rounded.
        Guaranteed to be in range [0,2^full_bits()].
        """
        if voltage < 0:
            return 0
        else:
            v = min(voltage/self.full_scale(), 1) # v in [0,1]
            return round(v * (1 << self._nbits))

    def kword(self, voltage):
        """Given a desired voltage, returns the 16-bit word which will
        be sent to the DAC.
        """
        return self.vout(voltage) << (16 - self._nbits)

# List the bit-widths of the recognised variants.
# If a variant isn't in this list, it's not a known variant 
# (ie, this dictionary is complete)
lookup_bits = { 'LM12': 12,
                'LM10': 10,
                'LM8':  8,
                'LZ12': 12,
                'LZ10': 10,
                'LZ8':  8,
                'HM12': 12,
                'HM10': 10,
                'HM8':  8,
                'HZ12': 12,
                'HZ10': 10,
                'HZ8':  8, }

# List all of the variants which have 4.096V full-scale
# (ie, all those with an 'H' in their name)
lookup_all_4v = ('HM12', 'HM10', 'HM8', 'HZ12', 'HZ10', 'HZ8' )

# List all of the variants which reset to zero-scale on power-on
# (ie, all those with a Z in their name
lookup_all_zero_reset = ('LZ12', 'LZ10', 'LZ8', 'HZ12', 'HZ10', 'HZ8')


class LTC2631(object):
    """PI to query and control an LTC2631 D/A converter via I2C.

    XXX
    For the MCP3221, "If [...] the voltage level of AIN is equal to or
    less than VSS + 1/2 LSB, the resultant code will be
    000h. Additionally, if the voltage at AIN is equal to or greater
    than VDD - 1.5 LSB, the output code will be FFFh."  Therefore,
    the full scale, corresponding to VSS+1.0*(VDD-VSS), is 1000h,
    but the maximum floating-point value that can be returned is FFFh/1000h.
    """

    def __init__(self, master, variant_ident, address=0x10):
        """Initialises an LTC2631.

        Parameters:
        master  -- the I2CMaster with which to commmunicate with the
                   LTC2631 chip.
        address -- the I2C address of the LCT2631 chip, as a number in [0..7]
                   (optional, default = 5)
        """
        self.master = master

        if variant_ident not in lookup_bits:
            raise ValueError("Invalid variant {}".format(variant_ident))

        self._variant = Variant(variant_ident in lookup_all_4v,
                                variant_ident in lookup_all_zero_reset,
                                lookup_bits[variant_ident])

        if address not in self._variant.addresses():
            raise ValueError("Invalid address {} for variant {}".format(address, variant_ident))

        self.address = address

        self._output = _OutputChannel(self)

    @property
    def output(self):
        return self._output

    def write(self, value):
        # Command codes:
        #   0000, Write to input register
        #   0001, Update (Power Up) DAC Register
        #   0011, Write to and Update (Power Up) DAC Register
        word = self._variant.kword(value)
        self.master.transaction(
            writing_bytes(self.address,
                          0x3 << 4,           # write and update DAC
                          (word & 0xff00)>>8, # high byte
                          (word & 0xff)))     # low byte
        

    @property
    def direction(self):
        return Out

    def full_scale(self):
        return self._variant.full_scale()

    def reset_to_zero_p(self):
        return self._variant.reset_to_zero_p()

    def powerdown(self):
        # Command code: 0100, Power Down
        self.master.transaction(
            writing_bytes(self.address, 0x40, 0, 0))

    # @property
    # def single_ended_output(self):
    #     return self._single_ended_output

    # def write_single_ended(self):
    #     """Write the XXX-bit value of a single-ended output channel."""
    #     return self.write_raw()

    # def write_raw(self):
    #     results = self.master.transaction(writing(self.address, 2))
    #     XXX
    #     # results is a (single-element) list of reads;
    #     # each read is a two-byte array
    #     r = results[0]
    #     return r[0]*0x100 + r[1]


class _OutputChannel(object):
    def __init__(self, bank):
        self.bank = bank

    @property
    def direction(self):
        return Out

    def get(self):
        return self._value

    def set(self, value):
        self._value = value
        self.bank.write(self._value)

    value = property(get, set)

    def open(self):
        pass

    def close(self):
        # Send the power-down command
        self.bank.powerdown()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()
        return False
