"""A convenient API to access the GPIO pins of the Raspberry Pi.

"""

import os
import subprocess
from contextlib import contextmanager
from quick2wire.board_revision import revision
from quick2wire.selector import EDGE

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



Out = "out"
In = "in"
    
Rising = "rising"
Falling = "falling"
Both = "both"
    
PullDown = "pulldown"
PullUp = "pullup"
    

class Pin(object):
    """Controls a GPIO pin."""
    
    __trigger__ = EDGE
    
    def __init__(self, index_to_soc_pin_number, index, direction=In, interrupt=None, pull=None):
        """Creates a pin
        
        Parameters:
        user_pin_number -- the identity of the pin used to create the derived class.
        soc_pin_number  -- the pin on the header to control, identified by the SoC pin number.
        direction       -- (optional) the direction of the pin, either In or Out.
        interrupt       -- (optional)
        pull            -- (optional)
        
        Raises:
        IOError        -- could not export the pin (if direction is given)
        """
        self._index_to_soc_pin_number = index_to_soc_pin_number
        self._index = index
        self._file = None
        self._direction = direction
        self._interrupt = interrupt
        self._pull = pull
    
    
    @property 
    def index(self):
        return self._index
    
    @property
    def soc_pin_number(self):
        return self._index_to_soc_pin_number(self._index)
    
    def open(self):
        gpio_admin("export", self.soc_pin_number, self._pull)
        self._file = open(self._pin_path("value"), "r+")
        self._write("direction", self._direction)
        if self._direction == In:
            self._write("edge", self._interrupt if self._interrupt is not None else "none")
            
    def close(self):
        if not self.closed:
            if self.direction == Out:
                self.value = 0
            self._file.close()
            self._file = None
            self._write("direction", In)
            self._write("edge", "none")
            gpio_admin("unexport", self.soc_pin_number)
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *exc):
        self.close()
        return False
    
    @property
    def value(self):
        """The current value of the pin: 1 if the pin is high or 0 if the pin is low.
        
        The value can only be set if the pin's direction is Out.
        
        Raises: 
        IOError -- could not read or write the pin's value.
        """
        self._check_open()
        self._file.seek(0)
        v = self._file.read()
        return int(v) if v else 0
    
    @value.setter
    def value(self, new_value):
        self._check_open()
        if self._direction != Out:
            raise ValueError("not an output pin")
        self._file.seek(0)
        self._file.write(str(int(new_value)))
        self._file.flush()
    
        
    @property
    def direction(self):
        """The direction of the pin: either In or Out.
        
        The value of the pin can only be set if its direction is Out.
        
        Raises:
        IOError -- could not set the pin's direction.
        """
        return self._direction
    
    @direction.setter
    def direction(self, new_value):
        self._write("direction", new_value)
        self._direction = new_value
    
    @property 
    def interrupt(self):
        """The interrupt property specifies what event (if any) will raise an interrupt.
        
        One of: 
        Rising  -- voltage changing from low to high
        Falling -- voltage changing from high to low
        Both    -- voltage changing in either direction
        None    -- interrupts are not raised
        
        Raises:
        IOError -- could not read or set the pin's interrupt trigger
        """
        return self._interrupt
    
    @interrupt.setter
    def interrupt(self, new_value):
        self._write("edge", new_value)
        self._interrupt = new_value

    @property
    def pull(self):
        return self._pull
    
    def fileno(self):
        """Return the underlying file descriptor.  Useful for select, epoll, etc."""
        return self._file.fileno()
    
    @property
    def closed(self):
        """Returns if this pin is closed"""
        return self._file is None or self._file.closed
    
    def _check_open(self):
        if self.closed:
            raise IOError(str(self) + " is closed")
    
    def _write(self, filename, value):
        with open(self._pin_path(filename), "w+") as f:
            f.write(value)
    
    def _pin_path(self, filename=""):
        return "/sys/devices/virtual/gpio/gpio%i/%s" % (self.soc_pin_number, filename)
    
    def __repr__(self):
        return self.__module__ + "." + str(self)
    
    def __str__(self):
        return "%s(%s,%i)"%(self.__class__.__name__, self._index_to_soc_pin_number.__name__, self.index)
    

def pi_broadcom_soc(index):
    return index

def pi_header(index):
    return header_to_soc(index)

def gpio_breakout(index):
    return gpio_to_soc(index)



# Backwards compatability

def HeaderPin(header_pin_number, *args, **kwargs):
    return Pin(pi_header, header_pin_number, *args, **kwargs)

def GPIOPin(gpio_pin_number, *args, **kwargs):
    return Pin(gpio_breakout, gpio_pin_number, *args, **kwargs)
