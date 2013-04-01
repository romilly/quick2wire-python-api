Getting Started With GPIO
=========================


Before You Start Coding...
--------------------------

Ensure you have installed gpio-admin and are in the gpio group.  Run
the `groups` command to list your group membership. For example:

    $ groups
    pi adm dialout cdrom sudo audio video plugdev games users netdev input indiecity 

If you don't see `gpio` in the list, you can add yourself to the gpio group with the command:

    sudo adduser $USER gpio

You must then log out and in again for Linux to apply the change in
group membership.

    $ groups
    pi adm dialout cdrom sudo audio video plugdev games users netdev input indiecity gpio 


Now Let's Write Some Code!
--------------------------

The GPIO pins are controlled by Pin objects, and those Pin objects are
managed by a "pin bank".  The simplest pin bank to use is called
`pins` and gives access to the pins labelled P0 to P7 on the
Quick2Wire interface board (or named GPIO0 to GPIO7 on the Raspberry
Pi's header number 1).  There's also a bank called pi_header_1 that
gives access to all the header pins, but we don't need that for this
example.

Python programs must import the `pins` pin bank from the
`quick2wire.gpio` module, along with constants to configure the pin:

    from quick2wire.gpio import pins, In, Out

Then you can get a Pin by calling the pin bank's `pin` method. This
takes two arguments: the pin number and whether the pin is to be used
for input or output.

    in_pin = pins.pin(0, direction=In)
    out_pin = pins.pin(1, direction=Out)

You must open a pin before you can read or write its value and close
the pin when you no longer need it.  The most convenient way to do
this is to use Python's `with` statement, which will open the pins at
the start of the statement and close them when the body of the
statement has finished running, even if the user kills the program or
failure makes the code throw an exception.
    
    with in_pin, out_pin:
        out_pin.value = 1
        print(in_pin.value)

A pin has a value of 1 when high, a value of 0 when low.

Putting it all together into a single program:

    from quick2wire.gpio import pins, In, Out
    
    in_pin = pins.pin(0, direction=In)
    out_pin = pins.pin(1, direction=Out)
    
    with in_pin, out_pin:
        out_pin.value = 1
        print(in_pin.value)


Here's a slightly more complicated example that blinks an LED attached to pin 1. This will
loop forever until the user stops it with a Control-C.

    from time import sleep
    from quick2wire.gpio import pins, Out
    
    with pins.pin(1, direction=Out) as pin:
        while True:
            pin.value = 1 - pin.value
            sleep(1)
