
from itertools import product, permutations
from quick2wire.parts.mcp23x17 import Registers, PinBanks, In, Out, IOCONA, IOCONB, GPIO
from factcheck import *

bank_ids = range(2)
pin_ids = range(8)

def all_pins_of_chip():
    global chip
    
    for b in bank_ids:
        for p in pin_ids:
            with chip.banks[b][p] as pin:
                yield pin


class FakeRegisters(Registers):
    def __init__(self):
        self.registers = {}
        self.writes = []
        self.reset()
    
    def write_register(self, reg, value):
        self.writes.append((reg, value))
        self.registers[reg] = value
        if reg == IOCONA:
            self.registers[IOCONB] = value
        elif reg == IOCONB:
            self.registers[IOCONA] = value
    
    def read_register(self, reg):
        return self.registers[reg]


def setup_function(function):
    global chip, registers
    registers = FakeRegisters()
    chip = PinBanks(registers)
    chip.reset()


def test_has_two_banks_of_eight_pins():
    assert len(chip.banks) == 2
    for b in bank_ids:
        assert len(chip.banks[b]) == 8

@forall(b=bank_ids, p=pin_ids)
def test_all_pins_report_their_bank_and_index(b, p):
    assert chip.banks[b][p].bank == chip.banks[b]
    assert chip.banks[b][p].index == p

@forall(b=bank_ids, p=pin_ids)
def test_can_use_a_context_manager_to_claim_ownership_of_a_pin_in_a_bank_and_release_it(b, p):
    with chip.banks[b][p] as pin:
        try :
            with chip.banks[b][p] as pin2:
                raise AssertionError("claiming the pin should have failed")
        except ValueError as e:
            pass

@forall(b=bank_ids, p=pin_ids)
def test_a_pin_can_be_claimed_after_being_released(b, p):
    with chip.banks[b][p] as pin:
        pass
    
    with chip.banks[b][p] as pin_again:
        pass


@forall(p=all_pins_of_chip())
def test_after_reset_or_poweron_all_pins_are_input_pins(p):
    # Chip is reset in setup
    assert p.direction == In


def test_resets_iocon_before_other_registers():
    # Chip is reset in setup
    assert chip.registers.writes[0] == (IOCONA, 0)

        
def test_only_resets_iocon_once_because_same_register_has_two_addresses():
    # Chip is reset in setup
    assert IOCONB not in [reg for (reg, value) in chip.registers.writes]


@forall(p=all_pins_of_chip())
def test_can_read_value_of_input_pin(p):
    registers.write_banked_register(p.bank.index, GPIO, 1 << p.index)
    assert p.value == 1
    
    registers.write_banked_register(p.bank.index, GPIO, 0)
    assert p.value == 0


@forall(p=all_pins_of_chip())
def test_can_set_pin_to_output_mode_and_write_value(p):
    p.direction = Out
    p.value = 1
    
    assert registers.read_banked_register(p.bank.index, GPIO) == (1 << p.index)
    
    p.value = 0
    assert registers.read_banked_register(p.bank.index, GPIO) == (0 << p.index)

@forall(ps=permutations(product(bank_ids, pin_ids), 2), p2_value=[0,1])
def test_can_write_value_of_pin_without_affecting_other_output_pins(ps, p2_value):
    (b1,p1), (b2,p2) = ps
    
    with chip.banks[b1][p1] as pin1, chip.banks[b2][p2] as pin2:
        pin1.direction = Out
        pin2.direction = Out
        
        pin2.value = p2_value
        
        pin1.value = 0
        assert registers.read_banked_register(b1, GPIO) & (1 << p1) == 0
        assert registers.read_banked_register(b2, GPIO) & (1 << p2) == (p2_value << p2)
        
        pin1.value = 1
        assert registers.read_banked_register(b1, GPIO) & (1 << p1) == (1 << p1)
        assert registers.read_banked_register(b2, GPIO) & (1 << p2) == (p2_value << p2)
        
        pin1.value = 0
        assert registers.read_banked_register(b1, GPIO) & (1 << p1) == 0
        assert registers.read_banked_register(b2, GPIO) & (1 << p2) == (p2_value << p2)
        

def _TODO_test_can_read_a_set_bit_then_write_then_read_same_set_bit():
    assert False, "not implemented yet"
