Quick2Wire Python API
=====================

A Python library for controlling the hardware attached to the
Raspberry Pi's header pins, without running as the root user.

Dependencies
------------

The library depends on Python 3.1. To install Python 3.1 run the command:

    sudo apt-get install python3

The GPIO API depends on Quick2Wire GPIO Admin.  To install Quick2Wire
GPIO Admin, follow the instructions at
http://github.com/quick2wire/quick2wire-gpio-admin

The I2C API depends on I2C support in the kernel.  We've been using
Chris Boot's kernel builds from
http://www.bootc.net/projects/raspberry-pi-kernel/


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

 * [Getting Started with GPIO](doc/getting-started-with-gpio.md)
 * [Getting Started with I2C](doc/getting-started-with-i2c.md)
