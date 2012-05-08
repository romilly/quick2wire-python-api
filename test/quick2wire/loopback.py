from quick2wire.gpio import Pin
from time import sleep
import unittest

class LoopbackTest(unittest.TestCase):
		
    def testGPIO(self):
        pin_0 = Pin(11, Pin.Out)
        pin_1 = Pin(12, Pin.Out)
        pin_2 = Pin(13, Pin.Out)
        pin_3 = Pin(15, Pin.Out)
        pin_4 = Pin(16, Pin.In)
        pin_5 = Pin(18, Pin.In)
        pin_6 = Pin(22, Pin.In)
        pin_7 = Pin(7,  Pin.In)
        self.check(pin_0, pin_4)
        self.check(pin_1, pin_5)
        self.check(pin_2, pin_6)
        self.check(pin_3, pin_7)
        pin_0 = Pin(11, Pin.In)
        pin_1 = Pin(12, Pin.In)
        pin_2 = Pin(13, Pin.In)
        pin_3 = Pin(15, Pin.In)
        pin_4 = Pin(16, Pin.Out)
        pin_5 = Pin(18, Pin.Out)
        pin_6 = Pin(22, Pin.Out)
        pin_7 = Pin(7,  Pin.Out)
        self.check(pin_4, pin_0)
        self.check(pin_5, pin_1)
        self.check(pin_6, pin_2)
        self.check(pin_7, pin_3)
        

    def check(self, op, ip):
        for value in [0, 1]:
            op.value = value
            self.assertEqual(ip.value,value, 'input was not %d' % value)
        op.value = 0

if __name__ == '__main__':
    unittest.main()
        


