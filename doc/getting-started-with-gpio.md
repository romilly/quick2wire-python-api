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


Another example, blinking an LED attached to header pin 12 and
using a context manager to unexport the pin when the user quits 
the program with Control-C.

    from time import sleep
    from quick2wire.gpio import Pin, exported
    
    with exported(Pin(12, Pin.Out)) as pin:
        while True:
            pin.value = 1 - pin.value
            sleep(1)
