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

The GPIO pins are controlled by GPIOPin objects. Python program must
import the GPIOPin class from the quick2wire.gpio module, along with
constants to configure the pin:

    from quick2wire.gpio import GPIOPin, In, Out

Then you can create a Pin. The Pin's constructor takes two arguments:
the header pin number and whether the pin is to be used for input or
output.

    in_pin = Pin(0, direction=In)
    out_pin = Pin(1, direction=Out)

You must open a pin before you can read or write its value and close
the pin when you no longer need it.  The most convenient way to do
this is to use Python's `with` statement, which will open the pins at
the start of the statement and close them when the body of the
statement has finished running, even if the user kills the program or
a bad piece of code throws an exception.
    
    with in_pin, out_pin:
        out_pin.value = 1
        print(in_pin.value)

A pin has a value of 1 when high, a value of 0 when low.

Putting it all together into a single program:

    from quick2wire.gpio import Pin, In, Out
    
    in_pin = Pin(0, direction=In)
    out_pin = Pin(1, direction=Out)
    
    with in_pin, out_pin:
        out_pin.value = 1
        print(in_pin.value)


Here's a slightly more complicated example that blinks an LED attached to pin 1. This will
loop forever until the user stops it with a Control-C.

    from time import sleep
    from quick2wire.gpio import GPIOPin, Out
    
    with GPIOPin(1, direction=Out) as pin:
        while True:
            pin.value = 1 - pin.value
            sleep(1)
