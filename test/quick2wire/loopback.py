from quick2wire.gpio import Pin
from time import sleep
import unittest

class LoopbackTest(unittest.TestCase):
		
    def testGPIO(self):
        pin_0 = Pin(11, Pin.Out)
        pin_4 = Pin(16, Pin.In)
        pin_1 = Pin(12, Pin.Out)
        pin_5 = Pin(18, Pin.In)
        self.check(pin_0, pin_4, 0)
        self.check(pin_0, pin_4, 1)
        self.check(pin_1, pin_5, 0)
        self.check(pin_1, pin_5, 1)

    def check(self, op, ip, value):
        op.value = value
        self.assertEqual(ip.value,value, 'input was not %d' % value)

if __name__ == '__main__':
    unittest.main()
        


