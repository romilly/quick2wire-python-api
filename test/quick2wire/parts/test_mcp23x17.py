

from quick2wire.parts.mcp23x17 import Registers, PinBanks

class FakeRegisters(Registers):
    def __init__(self):
        self.registers = {}
        self.reset()
    
    def write_register(self, reg, value):
        self.registers[reg] = value
    
    def read_register(self, reg):
        return self.registers[reg]


class TestPinBanks:
    def setup_method(self, method):
        self.chip = PinBanks(FakeRegisters())
    
    def test_has_two_banks(self):
        assert len(self.chip.banks) == 2
        assert self.chip.banks[0] is not None
        assert self.chip.banks[1] is not None
    
    def test_both_banks_have_eight_pins(self):
        assert len(self.chip.banks[0]) == 8
        assert len(self.chip.banks[1]) == 8
    
    def test_can_use_a_context_manager_to_claim_ownership_of_a_pin_in_a_bank_and_release_it(self):
        with self.chip.banks[0][1] as pin:
            assert pin.bank == self.chip.banks[0]
            assert pin.index == 1
        
    def test_a_pin_can_only_be_claimed_once_at_any_time(self):
        with self.chip.banks[0][1] as pin:
            try :
                with self.chip.banks[0][1] as pin2:
                    raise AssertionError("claim_pin() should have failed")
            except ValueError as e:
                pass

    def test_a_pin_can_be_claimed_after_being_released(self):
        with self.chip.banks[0][1] as pin:
            pass
        
        with self.chip.banks[0][1] as pin_again:
            pass
