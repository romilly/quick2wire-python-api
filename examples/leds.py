# minimal example for the website
import quick2wire.i2c as i2c

iodir_register_b = 0x01 # IODIRB
gpio_register_b = 0x13 # GPIOB

address = 0x20 # base I2C address for MCP23017

with i2c.I2CMaster(1) as bus:
    bus.transaction(
        i2c.writing_bytes(address, iodir_register_b, 0x00)) # all PORT B pins are now outputs
    bus.transaction(
        i2c.writing_bytes(address, gpio_register_b, 0xAA)) # PORT B now set to output hex AA

