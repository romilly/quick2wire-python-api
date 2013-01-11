Getting Started
---------------

 1. Ensure Python 3 is installed:
 
        sudo apt-get install python3

 2. Make a Python virtual environment for developing the API itself

        make env


Running Tests
-------------

To run all the tests use the command:

    make check

This will run both unit and loopback tests. To run the loopback tests you must have the appropriate hardware devices connected to the Pi and connected into the expected loopback configuration.

You can run loopback tests for a subset of devices (e.g. if you only have some connected) by running make with the `devices` variable set to a space-separated list of devices.  For example:

    make check devices="mcp23017 gpio"

The devices are:

 * gpio (used to test the GPIO API and the Quick2Wire breakout board via the Pi's SoC GPIO)
 * mcp23017 (used to test the MCP23017 expander board)
 * pcf8591 (used to test the PCF8591 AD/DA board)



Running with a different version of Python
------------------------------------------

If you want to use a different version of Python, ensure it is installed on the Pi.  Then make a virtual environment for that version.  For example:

    make env python=2.7

Then specify that python version when running make:

    make check python=2.7

