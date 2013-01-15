"""A convenient API to access the GPIO pins of the Raspberry Pi.

"""

import os
import subprocess
from contextlib import contextmanager
from quick2wire.board_revision import revision

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
    24: 8,
    26: 7
}

if revision() > 1:
    RaspberryPi_HeaderToSOC[3] = 2
    RaspberryPi_HeaderToSOC[5] = 3
    RaspberryPi_HeaderToSOC[13] = 27


RaspberryPi_GPIOToHeader = [11, 12, 13, 15, 16, 18, 22, 7]

def gpio_to_soc(gpio_pin_number):
    if 0 <= gpio_pin_number < 8:
        return header_to_soc(RaspberryPi_GPIOToHeader[gpio_pin_number])
    else:
        raise ValueError(str(gpio_pin_number)+" is not a valid GPIO pin")


def header_to_soc(header_pin_number):
    if header_pin_number in RaspberryPi_HeaderToSOC:
        return RaspberryPi_HeaderToSOC[header_pin_number]
    else:
        raise ValueError(str(header_pin_number)+" is not a valid IO header pin")

def gpio_admin(subcommand, pin, pull=None):
    if pull:
        subprocess.check_call(["gpio-admin", subcommand, str(pin), pull])
    else:
        subprocess.check_call(["gpio-admin", subcommand, str(pin)])



def _pin_file(name, parser, doc):
    def _read(self):
        self._ensure_exported()
        with open(self._pin_path(name), "r") as f:
            return parser(f.read())

    def _write(self, value):
        self._ensure_exported()
        with open(self._pin_path(name), "w") as f:
            f.write(str(value))

    return property(_read, _write, doc=doc)


class _IOPin(object):
    """Controls a GPIO pin."""
    
    Out = "out"
    In = "in"
    
    Rising = "rising"
    Falling = "falling"
    Both = "both"
    
    PullDown = "pulldown"
    PullUp = "pullup"
    
    def __init__(self, user_pin_number, soc_pin_number, direction=None, interrupt=None, pull=None):
        """Creates a pin
        
        If the direction is specified, the pin is exported if
        necessary and its direction is set.  If the direction is not
        specified, the pin is not exported and you must call export()
        before you start using it.
        
        Parameters:
        user_pin_number -- the identity of the pin used to create the derived class.
        soc_pin_number  -- the pin on the header to control, identified by the SoC pin number.
        direction       -- (optional) the direction of the pin, either In or Out.
        interrupt       -- (optional) 
        
        Raises:
        IOError        -- could not export the pin (if direction is given)
        """
        self.index = user_pin_number
        self.soc_pin_number = soc_pin_number
        self._file = None
        self.pull = pull
        if direction is not None:
            self.direction = direction
        if interrupt is not None:
            self.interrupt = interrupt
    
    
    def __repr__(self):
        return self.__module__ + "." + str(self)
    
    def __str__(self):
        return "%s(%i)"%(self.__class__.__name__, self.index)
    
    @property
    def is_exported(self):
        """Has the pin been exported to user space?"""
        return os.path.exists(self._pin_path())
    
    def export(self):
        """Export the pin to user space, making its control files visible in the filesystem.
        
        Raises:
        IOError -- could not export the pin.

        
        """
        gpio_admin("export", self.soc_pin_number, self.pull)
    
    def unexport(self):
        """Unexport the pin, removing its control files from the filesystem.
        
        Raises:
        IOError -- could not unexport the pin.
        
        """
        self._maybe_close()
        gpio_admin("unexport", self.soc_pin_number)
        
    def _ensure_exported(self):
        if not self.is_exported:
            self.export()
    
    @property
    def value(self):
        """The current value of the pin: 1 if the pin is high or 0 if
        the pin is low.
        
        The value can only be set if the pin's direction is Out.
        
        Raises: 
        IOError -- could not read or write the pin's value.
        
        """
        f = self._lazyopen()
        f.seek(0)
        v = f.read()
        return int(v) if v else 0
    
    @value.setter
    def value(self, new_value):
        f = self._lazyopen()
        f.seek(0)
        f.write(str(int(new_value)))
        f.flush()
    
    direction = _pin_file("direction", str.strip,
        """The direction of the pin: either In or Out.
        
        The value of the pin can only be set if its direction is Out.
        
        Raises:
        IOError -- could not read or set the pin's direction.
        
        """)

    interrupt = _pin_file("edge", str.strip,
            """The interrupt property specifies what event (if any) will trigger an interrupt.

            Raises:
            IOError -- could not read or set the pin's interrupt trigger

            """)
    
    def fileno(self):
        """
        Return the underlying fileno. Useful for calling select
        """
        return self._lazyopen().fileno()
        
    def _lazyopen(self):
        if self._file is None:
            self._file = open(self._pin_path("value"), "r+")
        return self._file
    
    def _maybe_close(self):
        if self._file is not None:
            self._file.close()
            self._file = None
    
    def _pin_path(self, filename=""):
        return "/sys/devices/virtual/gpio/gpio%i/%s" % (self.soc_pin_number, filename)
    


class HeaderPin(_IOPin):
    def __init__(self, header_pin_number, *args, **kwargs):
        return super(HeaderPin, self).__init__(header_pin_number, header_to_soc(header_pin_number), *args, **kwargs)

class GPIOPin(_IOPin):
    def __init__(self, gpio_pin_number, *args, **kwargs):
        return super(GPIOPin, self).__init__(gpio_pin_number, gpio_to_soc(gpio_pin_number), *args, **kwargs)



Out = _IOPin.Out
In = _IOPin.In

Rising = _IOPin.Rising
Falling = _IOPin.Falling
Both = _IOPin.Both

PullDown = _IOPin.PullDown
PullUp = _IOPin.PullUp



# Backwards compatability
Pin = HeaderPin

@contextmanager
def exported(pin):
    """A context manager that automatically exports a pin if necessary
    and unexports it at the end of the block.
    
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
