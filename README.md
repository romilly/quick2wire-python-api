Quick2Wire Python API
=====================

A Python library for controlling the hardware attached to the
Raspberry Pi's header pins, [without running as the root user](http://quick2wire.com/articles/working-safely-with-your-pi/).

STOP PRESS
----------

Earlier versions of the I2C API do not work if you upgrade the kernel of the official Raspbian distribution to Linux 3.6 by running rpi-update.  You will see an error like:

    File "/home/pi/quick2wire-python-api/src/quick2wire/i2c.py", line 74, in transaction
        ioctl(self.fd, I2C_RDWR, addressof(ioctl_arg))
    OverflowError: Python int too large to convert to C long

Please pull the latest changes if you have this issue.  The I2C API now works on Raspbian with the 3.6 kernel and the 3.2 kernel that's shipped with 
the official Raspbian distribution.  Note that we've recently reorganised the API repo slightly to conform with Python 
conventions. The root of the repository should now be added to PYTHONPATH.  If you run python3 from within the root directory of th repository, you can import 
quick2wire modules without having to fiddle with the PYTHONPATH at all. 


Dependencies
------------

The library depends on Python 3. To install Python 3 run this command from an administrator account, such as `pi`:

    sudo apt-get install python3

You'll also find the python tools
[virtualenv](http://www.virtualenv.org/en/latest/index.html) and
[pip](http://www.pip-installer.org/en/latest/index.html) useful:

    sudo apt-get install python-pip
    sudo apt-get install python-virtualenv


The GPIO API depends on Quick2Wire GPIO Admin.  To install Quick2Wire
GPIO Admin, follow the instructions at
http://github.com/quick2wire/quick2wire-gpio-admin

The I2C and SPI API depend on support in the kernel. Recent raspbian kernels should be fine.


Installation
------------

The library is currently under active development, so we do not
recommend installing it into the system-wide Python libraries.
Instead, you can either use it without installation or install it into
an isolated Python development environment created with
[`virtualenv`](http://www.virtualenv.org/).

To use the library without installation, add the full path of the
source tree to the `PYTHONPATH` environment variable. For example:

    export QUICK2WIRE_API_HOME=[the directory cloned from Git or unpacked from the source archive]
    export PYTHONPATH=$PYTHONPATH:$QUICK2WIRE_API_HOME

If you're using virtualenv, make your virtualenv
[active](http://www.virtualenv.org/en/latest/index.html#activate-script),
and then run:

    python3 setup.py install

Getting Started
---------------

 * [Getting Started with GPIO](http://github.com/quick2wire/quick2wire-python-api/blob/master/doc/getting-started-with-gpio.md)
 * [Getting Started with I2C](http://github.com/quick2wire/quick2wire-python-api/blob/master/doc/getting-started-with-i2c.md)


Help and Support
----------------

There is a [discussion group](https://groups.google.com/group/quick2wire-users) in which you can ask questions about the library.

If you have discovered a bug or would like to request a feature, raise an issue in the [issue tracker](https://github.com/quick2wire/quick2wire-python-api/issues).
