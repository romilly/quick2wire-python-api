# The methods and data here are common to the I2C MCP23017 and SPI MCP23S17

# only the methods for reading and writing to registers differ, and they must be defined in the appropriate subclasses.

# The MCP23x17 has two register addressing modes, depending on the value of bit7 of IOCON
# we assume bank=0 addressing (which is the POR default value)

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
IPOLA = _banked_register(_BankA, IOPOL)
IPOLB = _banked_register(_BankB, IOPOL)
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
    ((IOCON), 0x00),
    ((IODIR), 0xFF),
    ((IPOL, GPINTEN, DEFVAL, INTCON, GPPU, INTF, INTCAP, GPIO, OLAT), 0x00))

class MCP23x17:
    def reset(self):
        """Reset to power-on state"""
        for regs, value in _initial_register_values:
            for reg in regs:
                self.write_banked_register(_BankA, reg, value)
                if reg != IOCON:
                    # Avoid unnecessary communication
                    self.write_banked_register(_BankB, reg, value)
    
    def write_banked_register(bank, reg, value):
        self.write_register(_banked_register(bank, reg), value)
