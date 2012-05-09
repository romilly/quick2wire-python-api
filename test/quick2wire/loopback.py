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
        self.checkOutputsSeenAtCorrespondingInputs(self.pins[:4], self.pins[4:])
        self.checkOutputsSeenAtCorrespondingInputs(self.pins[4:], self.pins[:4])
        
    def checkOutputsSeenAtCorrespondingInputs(self, outputs, inputs):
        for (op, ip) in zip(outputs, inputs):
            op.direction = Pin.Out
            ip.direction = Pin.In
            self.checkOutputSeenAtInput(op, ip)
        
    def checkOutputSeenAtInput(self, op, ip):
        for value in [0, 1]:
            op.value = value
            self.assertEqual(ip.value, value, 'input %d was not %d' % (ip.header_pin_id, value))
        op.value = 0

if __name__ == '__main__':
    unittest.main()
        


