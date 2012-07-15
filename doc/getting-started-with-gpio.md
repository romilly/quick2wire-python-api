Getting Started With GPIO
=========================


Before You Start Coding...
--------------------------

Ensure you have installed gpio-admin and are in the gpio group.  Run
the `groups` command to list your group membership. For example:

    $ groups
    nat fuse i2c gpio

You can add yourself to the gpio group with the command:

    sudo adduser $USER gpio

You must then log out and in again for Linux to apply the change in
group membership.


Now Let's Write Some Code!
--------------------------

The GPIO pins are controlled by Pin objects. Python program must
import the Pin class from the quick2wire.gpio module:

    from quick2wire.gpio import Pin

Then you can create a Pin. The Pin's constructor takes two arguments:
the header pin number and whether the pin is to be used for input or
output.

    out_pin = Pin(12, Pin.Out)
    in_pin = Pin(16, Pin.In)

When you have a Pin instance you can read or write its value.  A value
of 1 is high, a value of 0 is low.
   
    out_pin.value = 1
    print(in_pin.value)

When you have finished using the pin, you must unexport it:

    out_pin.unexport()
    in_pin.unexport()

Putting it all together into a single program:

    from quick2wire.gpio import Pin
    
    out_pin = Pin(12, Pin.Out)
    in_pin = Pin(16, Pin.In)
    
    out_pin.value = 1
    print(in_pin.value)
    
    out_pin.unexport()
    in_pin.unexport()

To make sure you always unexport any pins you've exported, you can wrap the Pin objects
with `exported()`, a Python [context manager](http://docs.python.org/reference/datamodel.html#context-managers),
as part of a [with](http://docs.python.org/reference/compound_stmts.html#with) statement:

    from quick2wire.gpio import Pin, exported

    with exported(Pin(12, Pin.Out)) as out_pin, exported(Pin(16, Pin.In)) as in_pin:
        out_pin.value = 1
    	print(in_pin.value)

This will unexport the pins when the program leaves the `with` statement, even 
if the user kills the program or a bad piece of code throws an exception.

Here's a slightly more complicated example that blinks an LED attached to pin 8. This will 
loop forever until the user stops it with a Control-C.

    from time import sleep
    from quick2wire.gpio import Pin, exported
    
    with exported(Pin(8, Pin.Out)) as pin:
        while True:
            pin.value = 1 - pin.value
            sleep(1)


Connecting Pins
---------------

To make this blink program work, you'll need to know which physical pins to connect. The 
`quick2wire.gpio` library sorts out the confusion of pin numbering schemes so that you can
just specify the physical pin on the device. [This page](http://elinux.org/Rpi_Low-level_peripherals) 
currently seems to be the best summary of the pins and the I/O roles they fulfill. The library
will allow you to allocate only those pins which support GPIO. Lower numbered
pins are at the top end of the Pi with the SD Card and power connector. Pins 1 and 2 (at the top of 
the columns) are the 3.3 and 5 volt outputs. Here's a Pi wired up for the blink program 

<img src="http://github.com/quick2wire/quick2wire-python-api/raw/master/doc/getting-started-with-gpio-setup.png" alt="GPIO wiring example" width="250"/>
