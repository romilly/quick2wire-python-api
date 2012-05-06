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

We recommend using a Python 3 virtualenv for Python development.
Python's setup tools do not provide a way of *uninstalling* a library,
so if you install as a system-wise Python libraries you'll have to
manually uninstall the files.  With virtualenv, it is easy to create
development environments with different libraries in, so lack of
uninstall is not a problem.

To install into a virtualenv, make the virtualenv active and run:

    python setup.py install

If you are not using virtualenv, you can install into the system-wide python libraries (not recommended):

    sudo python3 setup.py install

Or, you can add the `src` directory of the project to your PYTHONPATH
before running your Python program, in which case yo udon't need to
install anything at all.

    export QUICK2WIRE_API_HOME=...the directory unpacked from the archive...
    export PYTHONPATH=$PYTHONPATH:$QUICK2WIRE_API_HOME/src
    python3 myprogram.py


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
    print("received:", in_pin.value)

When you have finished using the pin, you must unexport it:

    out_pin.unexport()
    in_pin.unexport()

Putting it all together into a single program:

    from quick2wire.gpio import Pin
    
    out_pin = Pin(12, Pin.Out)
    in_pin = Pin(16, Pin.In)
    
    out_pin.value = 1
    print("received:", in_pin.value)
    
    out_pin.unexport()
    in_pin.unexport()
