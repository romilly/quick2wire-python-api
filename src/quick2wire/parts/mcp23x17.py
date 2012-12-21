# The methods and data here are common to the I2C MCP23017 and SPI MCP23S17

# only the methods for reading and writing to registers differ, and they must be defined in the appropriate subclasses.

# The MCP23x17 has two register addressing modes, depending on the value of bit7 of IOCON
# we assume bank=0 addressing (which is the POR default value)

import contextlib
from warnings import warn

# TODO - import from GPIO or common definitions module
In = "in"
Out = "out"

# Bits within the IOCON regiseter
IOCON_INTPOL=1
IOCON_ODR=2
IOCON_MIRROR=6

# Register names within a bank
IODIR=0
IPOL=1
GPINTEN=2
DEFVAL=3
INTCON=4
IOCON=5
GPPU=6
INTF=7
INTCAP=8
GPIO=9
OLAT=10

bank_register_names = sorted([s for s in globals() if s.upper() == s], 
                             key=lambda s: globals()[s])


BANK_SIZE = 11

_BankA = 0
_BankB = 1

def _banked_register(bank, reg):
    return reg*2 + bank

IODIRA = _banked_register(_BankA, IODIR)
IODIRB = _banked_register(_BankB, IODIR)
IPOLA = _banked_register(_BankA, IPOL)
IPOLB = _banked_register(_BankB, IPOL)
GPINTENA =_banked_register(_BankA, GPINTEN)
GPINTENB = _banked_register(_BankB, GPINTEN)
DEFVALA = _banked_register(_BankA, DEFVAL)
DEFVALB = _banked_register(_BankB, DEFVAL)
INTCONA = _banked_register(_BankA, INTCON)
INTCONB = _banked_register(_BankB, INTCON)
IOCONA = _banked_register(_BankA, IOCON)
IOCONB = _banked_register(_BankB, IOCON) # Actually addresses the same register as IOCONA
IOCON_BOTH = IOCONA
GPPUA = _banked_register(_BankA, GPPU)
GPPUB = _banked_register(_BankB, GPPU)
INTFA = _banked_register(_BankA, INTF)
INTFB = _banked_register(_BankB, INTF)
INTCAPA = _banked_register(_BankA, INTCAP)
INTCAPB = _banked_register(_BankB, INTCAP)
GPIOA = _banked_register(_BankA, GPIO)
GPIOB = _banked_register(_BankB, GPIO)
OLATA = _banked_register(_BankA, OLAT)
OLATB = _banked_register(_BankB, OLAT)

register_names = sorted([s for s in globals() if s[-1] in ('A','B') and s.upper() == s], 
                        key=lambda s: globals()[s])

_initial_register_values = (
    ((IODIR,), 0xFF),
    ((IPOL, GPINTEN, DEFVAL, INTCON, GPPU, INTF, INTCAP, GPIO, OLAT), 0x00))

def _reset_sequence():
    return [(reg,value) for regs, value in _initial_register_values for reg in regs]


class Registers(object):
    """Abstract interface to MCP23x17 registers"""
    
    def reset(self, iocon=0x00):
        """Reset to power-on state"""
        self.write_register(IOCON_BOTH, iocon)
        
        for reg, value in _reset_sequence():
            self.write_banked_register(_BankA, reg, value)
            self.write_banked_register(_BankB, reg, value)
    
    def write_banked_register(self, bank, reg, value):
        self.write_register(_banked_register(bank, reg), value)
        
    def read_banked_register(self, bank, reg):
        return self.read_register(_banked_register(bank, reg))
    
    def write_register(self, reg, value):
        """Implement in subclasses"""
        pass
    
    def read_register(self, reg):
        """Implement in subclasses"""
        pass



def _set_bit(current_value, bit_index, new_value):
    bit_mask = 1 << bit_index
    return (current_value | bit_mask) if new_value else (current_value & ~bit_mask)


class PinBanks(object):
    def __init__(self, registers):
        self.registers = registers
        self._banks = (PinBank(self, 0), PinBank(self, 1))
    
    def bank(self, n):
        return self._banks[n]
    
    def __len__(self):
        return len(self._banks)

    __getitem__ = bank
    
    def reset(self, interrupt_polarity=False, interrupt_open_drain=False, interrupt_mirror=False):
        self.registers.reset((interrupt_polarity << IOCON_INTPOL)
                            |(interrupt_open_drain << IOCON_ODR)
                            |(interrupt_mirror << IOCON_MIRROR))
        
        for bank in self._banks:
            bank._reset_cache()


# Read and write modes

def deferred_read(f):
    """read() must be called explicitly."""
    pass

def immediate_read(f):
    """read() is called automatically on every get of Pin.value."""
    f()

def deferred_write(f):
    """write() must be called explicitly."""
    pass

def immediate_write(f):
    """registers are written when Pin attributes are set."""
    f()


class PinBank(object):
    def __init__(self, chip, bank_id):
        self.chip = chip
        self._bank_id = bank_id
        self._pins = tuple([Pin(self, i) for i in range(8)])
        self._register_cache = [None]*BANK_SIZE # self._register_cache[IOCON] is ignored
        self._outstanding_writes = []
        self.read_mode = immediate_read
        self.write_mode = immediate_write
    
    def __str__(self):
        return "PinBank("+self.index+")"
    

    def _reset_cache(self):
        for reg, value in _reset_sequence():
            self._register_cache[reg] = value
    
    
    @property
    def index(self):
        return self._bank_id
    

    def __len__(self):
        return len(self._pins)
    

    def pin(self, n):
        pin = self._pins[n]
        return pin
    
    __getitem__ = pin
    

    def read(self):
        self._read_register(INTCAP)
        self._read_register(GPIO)
    

    def write(self):
        for r in self._outstanding_writes:
            self._write_register(r, self._register_cache[r])
        self._outstanding_writes = []
    

    def _get_register_bit(self, register, bit_index):
        self.read_mode(lambda:self._read_register(register))
        
        if self._register_cache[register] is None:
            self._read_register(register)
        
        return bool(self._register_cache[register] & (1<<bit_index))
    
    
    def _read_register(self, register):
        self._register_cache[register] = self.chip.registers.read_banked_register(self._bank_id, register)
    
    
    def _set_register_bit(self, register, bit_index, new_value):
        self._register_cache[register] = _set_bit(self._register_cache[register], bit_index, new_value)
        if register not in self._outstanding_writes:
            self._outstanding_writes.append(register)
        
        self.write_mode(self.write)

    
    def _write_register(self, register, new_value):
        self.chip.registers.write_banked_register(self._bank_id, register, new_value)


    def _check_read_mode_for_interrupts(self):
        if self.read_mode == immediate_read:
            warn("interrupts enabled when in immediate read mode", stacklevel=1)
    


class Pin(object):
    def __init__(self, bank, index):
        self.bank = bank
        self.index = index
        self._is_claimed = False
    
    def open(self):
        if self._is_claimed:
            raise ValueError("pin already in use")
        self._is_claimed = True
    
    def close(self):
        self._is_claimed = False
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    @property
    def direction(self):
        return In if self._get_register_bit(IODIR) else Out
    
    @direction.setter
    def direction(self, new_direction):
        self._set_register_bit(IODIR, (new_direction == In))
    
    def get(self):
        return self._get_register_bit(GPIO)
    
    def set(self, new_value):
        self._set_register_bit(OLAT, new_value)
    
    value = property(get, set)
    
    @property
    def pull_down(self):
        return self._get_register_bit(GPPU)
    
    @pull_down.setter
    def pull_down(self, value):
        self._set_register_bit(GPPU, value)
    
    def interrupt_on_change(self):
        self.bank._check_read_mode_for_interrupts()
        # TODO - do these in a single transaction?
        self._set_register_bit(INTCON, 0)
        self._set_register_bit(GPINTEN, 1)
    
    def interrupt_when(self, value):
        self.bank._check_read_mode_for_interrupts()
        # TODO - do these in a single transaction?
        self._set_register_bit(INTCON, 1)
        self._set_register_bit(DEFVAL, not value)
        self._set_register_bit(GPINTEN, 1)
    
    @property
    def interrupt(self):
        return self._get_register_bit(INTCAP)
    
    def _set_register_bit(self, register, new_value):
        self.bank._set_register_bit(register, self.index, new_value)
    
    def _get_register_bit(self, register):
        return self.bank._get_register_bit(register, self.index)
        
    def __repr__(self):
        return "Pin(banks["+ str(self.bank.index) + "], " + str(self.index) + ")"
    
