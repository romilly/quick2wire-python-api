
from quick2wire.i2c import writing_bytes, reading
from quick2wire.parts.mcp23x17 import *


class Chip(MCP23x17):
    """Raw access to the MCP23017 chip"""
    
    def __init__(self, master, address=0x20):
        self.master = master
        self.address = address
        
    def write_register(self, reg, byte):
        self.master.transaction(
            writing_bytes(reg, byte))
    
    def read_register(self, reg):
        return self.master.transaction(
            reading(reg))[0][0]
    
