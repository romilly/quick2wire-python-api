# The methods and data here are common to the I2C MCP23017 and SPI MCP23S17

# only the methods for reading and writing to registers differ, and they must be defined in the appropriate subclasses.

# The MCP23x17 has two register addressing modes, depending on the value of bit7 of IOCON
# we assume bank=0 addressing (which is the POR default value)

import contextlib

# TODO - import from GPIO or common definitions module
In = "in"
Out = "out"

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

_BankA = 0
_BankB = 1

def _banked_register(bank, reg):
    return reg*2 + bank

IODIRA = _banked_register(_BankA, IODIR)
IODIRB = _banked_register(_BankB, IODIR)
IPOLA = _banked_register(_BankA, IPOL)
IPOLB = _banked_register(_BankB, IPOL)
GPINTENA=_banked_register(_BankA, GPINTEN)
GPINTENB = _banked_register(_BankB, GPINTEN)
DEFVALA = _banked_register(_BankA, DEFVAL)
DEFVALB = _banked_register(_BankB, DEFVAL)
INTCONA = _banked_register(_BankA, INTCON)
INTCONB = _banked_register(_BankB, INTCON)
IOCONA = _banked_register(_BankA, IOCON)
IOCONB = _banked_register(_BankB, IOCON) # Actually addresses the same register as IOCONA
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


_initial_register_values = (
    ((IOCON,), 0x00),
    ((IODIR,), 0xFF),
    ((IPOL, GPINTEN, DEFVAL, INTCON, GPPU, INTF, INTCAP, GPIO, OLAT), 0x00))


class Registers(object):
    """Abstract interface to MCP23x17 registers"""
    
    def reset(self):
        """Reset to power-on state"""
        for regs, value in _initial_register_values:
            for reg in regs:
                self.write_banked_register(_BankA, reg, value)
                if reg != IOCON:
                    # Avoid unnecessary communication
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



class PinBanks(object):
    def __init__(self, registers):
        self.registers = registers
        self.bank_a = PinBank(self, 0)
        self.bank_b = PinBank(self, 1)
        self.banks = (self.bank_a, self.bank_b)
    
    def reset(self):
        self.registers.reset()
        for bank in self.banks:
            bank.reset()


class PinBank(object):
    def __init__(self, chip, bank_id):
        self.chip = chip
        self._bank_id = bank_id
        self._pins = tuple([Pin(self, i) for i in range(8)])
    
    def __len__(self):
        return len(self._pins)
    
    def __getitem__(self, n):
        pin = self._pins[n]
        pin._open()
        return pin;


class Pin(object):
    def __init__(self, bank, index):
        self.bank = bank
        self.index = index
        self._is_claimed = False
        self.direction = In
    
    def _open(self):
        if self._is_claimed:
            raise ValueError("pin already in use")
        self._is_claimed = True
    
    def close(self):
        self._is_claimed = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

