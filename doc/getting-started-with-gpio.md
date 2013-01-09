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

When you have a Pin instance you can read or write its value.  A value
of 1 is high, a value of 0 is low.
   
    out_pin.value = 1
    print(in_pin.value)

When you have finished using the pin, you must unexport it:

    out_pin.unexport()
    in_pin.unexport()

Putting it all together into a single program:

    from quick2wire.gpio import Pin
    
    in_pin = Pin(0, direction=In)
    out_pin = Pin(1, direction=Out)
    
    out_pin.value = 1
    print(in_pin.value)
    
    out_pin.unexport()
    in_pin.unexport()

To make sure you always unexport any pins you've exported, you can wrap the Pin objects
with `exported()`, a Python [context manager](http://docs.python.org/reference/datamodel.html#context-managers),
as part of a [with](http://docs.python.org/reference/compound_stmts.html#with) statement:

    from quick2wire.gpio import Pin, exported

    with exported(GPIOPin(0, direction=In)) as in_pin, exported(GPIOPin(1, direction=Out)) as out_pin:
        out_pin.value = 1
    	print(in_pin.value)

This will unexport the pins when the program leaves the `with` statement, even 
if the user kills the program or a bad piece of code throws an exception.

Here's a slightly more complicated example that blinks an LED attached to pin 1. This will
loop forever until the user stops it with a Control-C.

    from time import sleep
    from quick2wire.gpio import GPIOPin, Out, exported
    
    with exported(GPIOPin(1, direction=Out)) as pin:
        while True:
            pin.value = 1 - pin.value
            sleep(1)
