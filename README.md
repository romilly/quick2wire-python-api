Quick2Wire Python API
=====================

A Python library for controlling the Raspberry Pi's GPIO pins without
running as root.

Dependencies
------------

The library depends on:

* Python 3.1
* Quick2Wire GPIO Admin

To install Python 3.1 run the command:

    sudo apt-get install python3

To install Quick2Wire GPIO Admin, follow the instructions at
http://github.com/quick2wire/quick2wire-gpio-admin


Installation
------------

The library is currently under active development, so we do not
recommend installing it into the system-wide Python
libraries. Instead, you can either use it with no installation or use
virtualenv, to do all your development within an isolated Python
environment, and install into that.

To use the library without any installation, add the full path of the
`src` subdirectory of the source tree to the PYTHONPATH environment
variable.  For example:

    export QUICK2WIRE_API_HOME=[the directory cloned from Git or unpacked from the source archive]
    export PYTHONPATH=$PYTHONPATH:$QUICK2WIRE_API_HOME/src

To install into a virtualenv, make the virtualenv active and run:

    python setup.py install



Getting Started
---------------

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
unexporting the pin when the user quits the program with Control-C.

    from time import sleep
    from quick2wire.gpio import Pin
    
    pin = Pin(12)
    
    try:
        while True:
            pin.value = 1 - pin.value
            sleep(1)
    except KeyboardInterrupt:
        pin.unexport()
