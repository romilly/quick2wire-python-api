
from quick2wire.i2c import writing_bytes, reading
import quick2wire.parts.mcp23x17 as mcp23x17


class Registers(mcp23x17.Registers):
    """Low level access to the MCP23017 registers"""
    
    def __init__(self, master, address):
        self.master = master
        self.address = address
        
    def write_register(self, register_id, byte):
        self.master.transaction(
            writing_bytes(self.address, register_id, byte))
    
    def read_register(self, register_id):
        return self.master.transaction(
            writing_bytes(self.address, register_id),
            reading(self.address, 1))[0][0]


class MCP23017(mcp23x17.PinBanks):
    def __init__(self, master, address=0x20):
        super().__init__(Registers(master, address))

