"""A convenient API to access the GPIO pins of the Raspberry Pi.

"""

import os
import subprocess
from contextlib import contextmanager

# Maps header pin numbers to SOC GPIO numbers
# See http://elinux.org/RPi_Low-level_peripherals
#
# Note: - header pins are numbered from 1, SOC GPIO from zero 
#       - the Pi documentation identifies some header pins as GPIO0,
#         GPIO1, etc., but these are not the same as the SOC GPIO
#         numbers.
#
# Todo - different factory functions for creating Pins by SOC id,
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
    

class Pin(object):
    """Controls a GPIO pin."""
    
    Out = "out"
    In = "in"
    
    def __init__(self, header_pin_number, direction=None):
        """Creates a pin, given a header pin number.
        
        If the direction is specified, the pin is exported if
        necessary and its direction is set.  If the direction is not
        specified, the pin is not exported and you must call export()
        before you start using it.
        
        Parameters:
            
            header_pin_id - the pin on the header to control.
            
            direction (optional) - the direction of the pin, either In
            or Out.
           
        """
        
        self.header_pin_id = header_pin_number
        self.pin_id = header_to_soc(header_pin_number)
        if direction:
            if not self.is_exported:
                self.export()
            self.direction = direction
    
    def __repr__(self):
        return self.__module__ + "." + str(self)
    
    def __str__(self):
        return "%s(%i)"%(self.__class__.__name__, self.header_pin_id)
    
    @property
    def is_exported(self):
        """Has the pin been exported to user space?"""
        return os.path.exists(self._pin_file())
    
    def export(self):
        """Export the pin to user space, making its control files visible in the filesystem."""
        gpio_admin("export", self.pin_id)
    
    def unexport(self):
        """Unexport the pin, removing its control files from the filesystem."""
        gpio_admin("unexport", self.pin_id)
    
    value = pin_file("value", int,
        """The current value of the pin: 1 if the pin is high or 0 if
        the pin is low.
        
        The value can only be set if the pin's direction is Out
        
        """)
    
    direction = pin_file("direction", str.strip,
        """The direction of the pin: either In or Out.
        
        The value of the pin can only be set if its direction is Out.
        
        """)
    
    def _pin_file(self, filename=""):
        return "/sys/devices/virtual/gpio/gpio%i/%s" % (self.pin_id, filename)


@contextmanager
def exported(pin):
    if not pin.is_exported:
        pin.export()
    try:
        yield pin
    finally:
        pin.unexport()
