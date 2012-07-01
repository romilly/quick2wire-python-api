Getting Started With I2C
========================

We're going to write a program that counts the number of times a
button has been clicked and displays the count in binary on a LEDs.
We'll connect the button and LEDs to an MCP23008 port expander and
communicate to the MCP23008 by I2C.

Before You Start Coding...
--------------------------

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
the `i2cdetect` command:

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


To communicate with the chip we need to create an I2CBus object.  The
I2CBus class supports the context manager protocol, meaning we can use
the `with` statement to automatically close the bus when the user
quits our program by pressing Control-C.

    with i2c.I2CBus() as bus:
        ...

To help us write the communication code, we'll define some attributes of the MCP23008 chip:

    address = 0x20
    iodir_register = 0x00
    gpio_register = 0x09

And define some helper functions to write to and read from registers of the chip. This is where we perform I2C transactions. 
    def write_register(bus, reg, b):
        bus.transaction(
            i2c.write_bytes(address, reg, b))
    
    def read_register(bus, reg):
        return bus.transaction(
            i2c.write_bytes(address, reg),
            i2c.read(address, 1))[0][0]

Now we can communicate with the chip.  First we'll reset it so that
GPIO pin 7 is an input pin and pins 0-6 are output pins, and clear the
outputs to zero.

    write_register(bus, iodir_register, 0x80)
    write_register(bus, gpio_register, 0x00)

Then we'll loop.  On each iteration we'll read the GPIO register and
test the state of the input pin to see if the button has been clicked.
If it has, we'll increment the count to a maximum of 127, and write
the new count to the GPIO register to set the value of the output pins
connected to the LEDs.  Finally, we'll sleep a bit to let other
processes use the CPU.
    
    button_down = False
    count = 0
    
    while True:
        gpio_state = read_register(bus, gpio_register)
        
        button_was_down = button_down
        button_down = bool(gpio_state & 0x80)
        
        if button_down and not button_was_down:
            count = min(count + 1, 127)
            write_register(bus, gpio_register, count)
        
        time.sleep(0.05)



Putting it all together:

    #!/usr/bin/env python3

    import quick2wire.i2c as i2c
    import time

    address = 0x20
    iodir_register=0x00
    gpio_register=0x09

    def write_register(bus, reg, b):
        bus.transaction(
            i2c.write_bytes(address, reg, b))

    def read_register(bus, reg):
        return bus.transaction(
            i2c.write_bytes(address, reg),
            i2c.read(address, 1))[0][0]

    with i2c.I2CBus() as bus:
        write_register(bus, iodir_register, 0x80)
        write_register(bus, gpio_register, 0x00)

        print("ready")

        button_down = False
        count = 0

        while True:
            gpio_state = read_register(bus, gpio_register)

            button_was_down = button_down
            button_down = bool(gpio_state & 0x80)

            if button_down and not button_was_down:
                count = min(count + 1, 127)
                write_register(bus, gpio_register, count)

            time.sleep(0.05)
