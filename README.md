Quick2Wire Python API
=====================

A Python library for controlling the hardware attached to the
Raspberry Pi's header pins, without running as the root user.

Dependencies
------------

The library depends on Python 3.1. To install Python 3.1 run this command from an administrator account, such as `pi`:

    sudo apt-get install python3

You'll also find the python tools [virtualenv](http://www.virtualenv.org/en/latest/index.html) and [pip](http://www.pip-installer.org/en/latest/index.html) useful:

    sudo apt-get install python-pip
    sudo apt-get install python-virtualenv


The GPIO API depends on Quick2Wire GPIO Admin.  To install Quick2Wire
GPIO Admin, follow the instructions at
http://github.com/quick2wire/quick2wire-gpio-admin

The I2C API depends on I2C support in the kernel.  We've been using
Chris Boot's kernel builds from
http://www.bootc.net/projects/raspberry-pi-kernel/


Installation
------------

The library is currently under active development, so we do not
recommend installing it into the system-wide Python libraries. 
Instead, you can either use it without installation or 
install it into an isolated Python development environment created with `virtualenv`.

To use the library without installation, add the full path of the
`src` subdirectory of the source tree to the `PYTHONPATH` environment
variable. For example:

    export QUICK2WIRE_API_HOME=[the directory cloned from Git or unpacked from the source archive]
    export PYTHONPATH=$PYTHONPATH:$QUICK2WIRE_API_HOME/src

To install into a virtualenv, [make the virtualenv active](http://www.virtualenv.org/en/latest/index.html#activate-script) 
and run:

    python setup.py install

If you don't have virtualenv set up yet, you can create a local environment by running this in the project directory:

    make env


Getting Started
---------------

 * [Getting Started with GPIO](http://github.com/quick2wire/quick2wire-python-api/blob/master/doc/getting-started-with-gpio.md)
 * [Getting Started with I2C](http://github.com/quick2wire/quick2wire-python-api/blob/master/doc/getting-started-with-i2c.md)
