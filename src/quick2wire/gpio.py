"""A convenient API to access the GPIO pins of the Raspberry Pi.

"""

import os
import subprocess
from contextlib import contextmanager

# Maps header pin numbers to SoC GPIO numbers
# See http://elinux.org/RPi_Low-level_peripherals
#
# Note: - header pins are numbered from 1, SoC GPIO from zero 
#       - the Pi documentation identifies some header pins as GPIO0,
#         GPIO1, etc., but these are not the same as the SoC GPIO
#         numbers.
#
# Todo - different factory functions for creating Pins by SoC id,
#        header id and Pi GPIO id.
#
RaspberryPi_HeaderToSOC = {
    3:  0, 
    5:  1, 
    7:  4, 
    8:  14, 
    10: 15, 
    11: 17, 
    12: 18, 
    13: 21, 
    15: 22, 
    16: 23, 
    18: 24, 
    19: 10, 
    21: 9, 
    22: 25, 
    23: 11, 
    25: 7,
    26: 8
}

def header_to_soc(header_pin_number):
    if header_pin_number in RaspberryPi_HeaderToSOC:
        return RaspberryPi_HeaderToSOC[header_pin_number]
    else:
        raise ValueError(str(header_pin_number)+" is not a valid GPIO header pin")

def gpio_admin(subcommand, pin):
    subprocess.check_call(["gpio-admin", subcommand, str(pin)])


def pin_file(name, parser, doc):
    def _read(self):
        with open(self._pin_file(name), "r") as f:
            return parser(f.read())

    def _write(self, value):
        with open(self._pin_file(name), "w") as f:
            f.write(str(value))

    return property(_read, _write, doc=doc)

def pin_value_file(name, doc):
    def _read(self):
        f = self._lazyopen()
        f.seek(0)
        v = f.read()
        return int(v) if v else 0

    def _write(self, value):
        f = self._lazyopen()
        f.seek(0)
        f.write(str(value))
        f.flush()
    
    return property(_read, _write, doc=doc)
    

class Pin(object):
    """Controls a GPIO pin."""
    
    Out = "out"
    In = "in"

    Rising = "rising"
    Falling = "falling"
    Both = "both"
    
    def __init__(self, header_pin_number, direction=None, edge=None):
        """Creates a pin, given a header pin number.
        
        If the direction is specified, the pin is exported if
        necessary and its direction is set.  If the direction is not
        specified, the pin is not exported and you must call export()
        before you start using it.
        
        Parameters:
        header_pin_id -- the pin on the header to control.
        direction     -- (optional) the direction of the pin, either In or Out.
        
        Raises:
        IOError       -- could not export the pin (if direction is given)
        """
        
        self.header_pin_id = header_pin_number
        self.pin_id = header_to_soc(header_pin_number)
        self._file = None
        if direction:
            if not self.is_exported:
                self.export()
            self.direction = direction
        if edge:
            self.edge = edge

    
    def __repr__(self):
        return self.__module__ + "." + str(self)
    
    def __str__(self):
        return "%s(%i)"%(self.__class__.__name__, self.header_pin_id)
    
    @property
    def is_exported(self):
        """Has the pin been exported to user space?"""
        return os.path.exists(self._pin_file())
    
    def export(self):
        """Export the pin to user space, making its control files visible in the filesystem.
        
        Raises:
        IOError -- could not export the pin.

        
        """
        gpio_admin("export", self.pin_id)
    
    def unexport(self):
        """Unexport the pin, removing its control files from the filesystem.
        
        Raises:
        IOError -- could not unexport the pin.
        
        """
        self._maybe_close()
        gpio_admin("unexport", self.pin_id)
    
    value = pin_value_file("value", 
        """The current value of the pin: 1 if the pin is high or 0 if
        the pin is low.
        
        The value can only be set if the pin's direction is Out.
        
        Raises: 
        IOError -- could not read or write the pin's value.
        
        """)
    
    direction = pin_file("direction", str.strip,
        """The direction of the pin: either In or Out.
        
        The value of the pin can only be set if its direction is Out.
        
        Raises:
        IOError -- could not read or set the pin's direction.
        
        """)

    edge = pin_file("edge", str.strip,
            """The edge property specifies what event (if any) will
            trigger an interrupt.

            Raises:
            IOError -- could not read or set the pin's direction

            """)

    def fileno(self):
        """
        Return the underlying fileno. Useful for calling select
       
        """
        self._lazyopen()
        return self._file.fileno()
    
    def _pin_file(self, filename=""):
        return "/sys/devices/virtual/gpio/gpio%i/%s" % (self.pin_id, filename)

    def _lazyopen(self):
        if self._file == None:
            self._file = open(self._pin_file("value"), "r+")
        return self._file

    def _maybe_close(self):
        if self._file != None:
            self._file.close()


@contextmanager
def exported(pin):
    """A context manager that automatically exports a pin if necessary
    and exports it at the end of the block.
    
    Example::
    
        with exported(Pin(15)) as pin:
            print(pin.value)
    
    """
    
    if not pin.is_exported:
        pin.export()
    try:
        yield pin
    finally:
        pin.unexport()
