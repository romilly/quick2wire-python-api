Getting Started With I2C
========================


Warning:
-------

[Revision 2.0](http://www.raspberrypi.org/archives/1929) of the Raspberry Pi swaps the connections to I2C buses 0 and 1.

With a revision 2.0 board, if you connect an I2C device to the appropriate header,
you will see it when you run `i2cdetect 1` instead of `i2cdetect 0`.

The library now auto-detects whether you are running version 1.0 or 2.0 of the board, so the same code will work on
either.

The example:
------------

In this example, we're going to write a program that reads the state
of the GPIO pins of an MCP23008 port expander connected to the
Raspberry Pi's I2C bus.

Before You Start Coding...
--------------------------

By default, i2c is disabled in the raspbian kernel. To enable it, and check out your installation, follow [these
instructions](http://quick2wire.com/articles/physical-python-part-1/)

Ensure you are in the i2c group.  Run the `groups` command to list
your group membership. For example:

    $ groups
    nat fuse i2c gpio

You can add yourself to the i2c group with the command:

    sudo adduser $USER i2c

You must then log out and in again for Linux to apply the change in
group membership.

Check the MCP23008 is connected to your I2C bus and its address is
configured as expected.  We can see the device on the bus by running
the `i2cdetect` command. Remember to replace 0 with 1 if you hav a revision 2 board.

    $ i2cdetect 0
    WARNING! This program can confuse your I2C bus, cause data loss and worse!
    I will probe file /dev/i2c-0.
    I will probe address range 0x03-0x77.
    Continue? [Y/n] Y
         0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    20: 20 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    70: -- -- -- -- -- -- -- --                         

The default address of the MCP23008 is 0x20, but it can be changed
(read the chip's data sheet for information about that).  If the chip
appears at a different address, change the value of the address
variable in the code below.

Now Let's Write Some Code!
--------------------------

To use the Quick2Wire I2C API we must import the quick2wire.i2c
module.  We'll import it with a shorter name for convenience:

    import quick2wire.i2c as i2c

Let's define variables to represent attributes of the MCP23008:

    address = 0x20
    iodir_register = 0x00
    gpio_register = 0x09

To communicate with the chip we need to create an I2CMaster object.  The
I2CMaster class supports the context manager protocol, meaning we can use
the `with` statement to automatically close the bus when the user
quits our program by pressing Control-C.

    with i2c.I2CMaster() as bus:
        ...

Now we can communicate with the chip.  First we'll set all the GPIO
pins be inputs by writing to the chip's IODIR register. Setting a bit
in the register to 1 switches the corresponding pin to be an input, so
setting the byte to 255 (or 0xFF in hex) switches all pins to input.
To write to the register we perform an I2C transaction containing a
single write operation that writes two bytes: the register to
write to and the value of the register.

        bus.transaction(
            i2c.writing_bytes(address, iodir_register, 0xFF))

Then we'll read the value of the chip's GPIO register by performing a
transaction containing two operations: a write operation that tells
the chip which register we want to read, and a read operation that
reads a single byte from that register.

        read_results = bus.transaction(
            i2c.writing_bytes(address, gpio_register),
            i2c.reading(address, 1))

The I2CMaster' transaction method returns a list of byte sequences, one
for each read operation performed.  Each result is an array of bytes
read from the device.  So the state of the GPIO pins is the first and
only byte of the first and only byte sequence returned.

        gpio_state = read_results[0][0]

We finally print that in hexadecimal:

        print("%02x" % gpio_state)

Putting it all together:

    #!/usr/bin/env python3
    
    import quick2wire.i2c as i2c
    
    address = 0x20
    iodir_register = 0x00
    gpio_register = 0x09
    
    with i2c.I2CMaster() as bus:    
        bus.transaction(
            i2c.writing_bytes(address, iodir_register, 0xFF))
        
        read_results = bus.transaction(
            i2c.writing_bytes(address, gpio_register),
            i2c.reading(address, 1))
        
        gpio_state = read_results[0][0]
        
        print("%02x" % gpio_state)
