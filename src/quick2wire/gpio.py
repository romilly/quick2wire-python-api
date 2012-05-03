
import os
import subprocess

#TODO - support multiple platforms
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
    17: 24, 
    18: 10, 
    20: 9, 
    21: 25, 
    22: 11, 
    23: 8, 
    25: 7
}

def header_to_soc(header_pin_number):
    if header_pin_number in RaspberryPi_HeaderToSOC:
        return RaspberryPi_HeaderToSOC[header_pin_number]
    else:
        raise ValueError(str(header_pin_number)+" is not a valid GPIO header pin")

def gpio_admin(subcommand, pin):
    subprocess.check_call(["gpio-admin", subcommand, str(pin)])


def pin_file(name, parser):
    def _read(self):
        with open(self._pin_file(name), "r") as f:
            return parser(f.read())
    
    def _write(self, value):
        with open(self._pin_file(name), "w") as f:
            f.write(str(value))
    
    return property(_read, _write)
    

class Pin(object):
    Out = "out"
    In = "in"
    
    def __init__(self, header_pin_id):
        self.header_pin_id = header_pin_id
        self.pin_id = header_to_soc(header_pin_id)
    
    def __repr__(self):
        return self.__module__ + "." + str(self)
    
    def __str__(self):
        return "%s(%i)"%(self.__class__.__name__, self.header_pin_id)
    
    @property
    def is_exported(self):
        return os.path.exists(self._pin_file())
    
    def export(self):
        gpio_admin("export", self.pin_id)
    
    def unexport(self):
        gpio_admin("unexport", self.pin_id)
    
    value = pin_file("value", int)
    direction = pin_file("direction", str.strip)
    
    def _pin_file(self, filename=""):
        return "/sys/devices/virtual/gpio/gpio%i/%s" % (self.pin_id, filename)

