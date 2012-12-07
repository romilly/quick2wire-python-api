

from quick2wire.parts.mcp23x17 import Registers, PinBanks, In, Out, IOCONA, IOCONB, GPIO

class FakeRegisters(Registers):
    def __init__(self):
        self.registers = {}
        self.writes = []
        self.reset()
    
    def write_register(self, reg, value):
        self.writes.append((reg, value))
        self.registers[reg] = value
    
    def read_register(self, reg):
        return self.registers[reg]


def setup_function(function):
    global chip, registers
    registers = FakeRegisters()
    chip = PinBanks(registers)


def test_has_two_banks_of_eight_pins():
    assert len(chip.banks) == 2
    assert chip.banks[0].index == 0
    assert chip.banks[1].index == 1
    assert len(chip.banks[0]) == 8
    assert len(chip.banks[1]) == 8
    

def test_can_use_a_context_manager_to_claim_ownership_of_a_pin_in_a_bank_and_release_it():
    with chip.banks[0][1] as pin:
        assert pin.bank == chip.banks[0]
        assert pin.index == 1
        

def test_a_pin_can_only_be_claimed_once_at_any_time():
    with chip.banks[0][1] as pin:
        try :
            with chip.banks[0][1] as pin2:
                raise AssertionError("claim_pin() should have failed")
        except ValueError as e:
            pass


def test_a_pin_can_be_claimed_after_being_released():
    with chip.banks[0][1] as pin:
        pass
    
    with chip.banks[0][1] as pin_again:
        pass

    
def test_after_reset_or_poweron_all_pins_are_input_pins():
    # Chip is reset in setup
    for pin in all_pins(chip):
        assert pin.direction == In
    

def test_resets_iocon_before_other_registers():
    # Chip is reset in setup
    assert chip.registers.writes[0] == (IOCONA, 0)

        
def test_only_resets_iocon_once_because_same_register_has_two_addresses():
    # Chip is reset in setup
    assert IOCONB not in [reg for (reg, value) in chip.registers.writes]


def test_can_read_value_of_input_pin():
    for pin in all_pins(chip):
        registers.write_banked_register(pin.bank.index, GPIO, 1 << pin.index)
        assert pin.value == 1
        
        registers.write_banked_register(pin.bank.index, GPIO, 0)
        assert pin.value == 0


def all_pins(chip):
    for b in 0,1:
        for p in range(8):
            with chip.banks[b][p] as pin:
                yield pin
