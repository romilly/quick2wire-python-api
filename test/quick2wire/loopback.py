from quick2wire.gpio import Pin
from time import sleep
import unittest

class LoopbackTest(unittest.TestCase):
    def setUp(self):
        self.pins = list([Pin(headerPinNumber) for headerPinNumber in [11, 12, 13, 15, 16, 18, 22, 7]])
        for pin in self.pins:
            pin.export()
		
    def tearDown(self):
        for pin in self.pins:
            if pin.is_exported:
                pin.unexport()
		
    def test_GPIO(self):
        for i in range(0, 4):
            self.pins[i].direction = Pin.Out
            self.pins[i+4].direction = Pin.In
            self.checkOutputSeeenAtInput(self.pins[i], self.pins[i+4])
        for i in range(0, 4):
            self.pins[i].direction = Pin.In
            self.pins[i+4].direction = Pin.Out
            self.checkOutputSeeenAtInput(self.pins[i+4], self.pins[i])
        
    def checkOutputSeeenAtInput(self, op, ip):
        for value in [0, 1]:
            op.value = value
            self.assertEqual(ip.value, value, 'input %d was not %d' % (ip.header_pin_id, value))
        op.value = 0

if __name__ == '__main__':
    unittest.main()
        


