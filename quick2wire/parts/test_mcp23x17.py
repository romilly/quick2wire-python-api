
from itertools import product, permutations, count
from warnings import catch_warnings, simplefilter as issue_warnings
import quick2wire.parts.mcp23x17 as mcp23x17
from quick2wire.parts.mcp23x17 import *
from quick2wire.parts.mcp23x17 import _banked_register
from factcheck import *

bits = from_range(2)
bank_ids = from_range(2)
pin_ids = from_range(0,8)
banked_pin_ids = tuples(bank_ids, pin_ids)
pin_pairs = ((p1,p2) for (p1,p2) in tuples(banked_pin_ids,banked_pin_ids) if p1 != p2)

def all_pins_of_chip():
    global chip
    
    for b,p in banked_pin_ids:
        with chip[b][p] as pin:
            yield pin

def setup_function(function=None):
    global chip, registers
    
    registers = FakeRegisters()
    chip = PinBanks(registers)
    chip.reset()


def test_has_two_banks_of_eight_pins():
    assert len(chip) == 2
    assert len(chip[0]) == 8
    assert len(chip[1]) == 8


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_all_pins_report_their_bank_and_index(b, p):
    assert chip[b][p].bank == chip[b]
    assert chip[b][p].index == p


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_can_use_a_context_manager_to_claim_ownership_of_a_pin_in_a_bank_and_release_it(b, p):
    with chip[b][p] as pin:
        try:
            with chip[b][p] as pin2:
                raise AssertionError("claiming the pin should have failed")
        except ValueError as e:
            pass


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_a_pin_can_be_claimed_after_being_released(b, p):
    with chip[b][p] as pin:
        pass
    
    with chip[b][p] as pin_again:
        pass


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_after_reset_or_poweron_all_pins_are_input_pins(b,p):
    # Chip is reset in setup
    with chip[b][p] as pin:
        assert pin.direction == In


def test_resets_iocon_before_other_registers():
    registers.clear_writes()
    
    chip.reset()
    assert chip.registers.writes[0][0] in (IOCONA, IOCONB)


@forall(intpol=bits, odr=bits, mirror=bits, samples=4)
def test_can_set_configuration_of_chip_on_reset(intpol, odr, mirror):
    """Note: IOCON is duplicated in both banks so only need to test the contents in one bank"""
    
    chip.reset(interrupt_polarity=intpol, interrupt_open_drain=odr, interrupt_mirror=mirror)
    
    assert registers.register_bit(0, IOCON, IOCON_INTPOL) == intpol
    assert registers.register_bit(0, IOCON, IOCON_ODR) == odr
    assert registers.register_bit(0, IOCON, IOCON_MIRROR) == mirror



@forall(b=bank_ids, p=pin_ids, samples=3)
def test_can_read_logical_value_of_input_pin(b,p):
    chip.reset()
    
    with chip[b][p] as pin:
        pin.direction = In
    
        registers.given_gpio_inputs(b, 1 << p)
        assert pin.value == 1
        
        registers.given_gpio_inputs(b, 0)
        assert pin.value == 0



@forall(b=bank_ids)
def test_initially_banks_are_in_immediate_mode(b):
    assert chip[b].read_mode == immediate_read
    assert chip[b].write_mode == immediate_write


@forall(b = bank_ids, p=pin_ids, samples=2)
def test_in_deferred_read_mode_bank_must_be_read_explicitly_before_pin_value_is_visible(b, p):
    chip.reset()
    
    bank = chip[b]
    
    bank.read_mode = deferred_read
    
    with bank[p] as pin:
        assert pin.value == 0
        
        registers.given_gpio_inputs(b, 1<<p)
        assert pin.value == 0
        
        bank.read()
        assert pin.value == 1
        
        registers.given_gpio_inputs(b, 0)        
        assert pin.value == 1
        
        bank.read()
        assert pin.value == 0


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_can_set_pin_to_output_mode_and_set_its_logical_value(b,p):
    with chip[b][p] as pin:
        pin.direction = Out
        
        pin.value = 1
        assert registers.read_banked_register(b, OLAT) == (1 << p)
    
        pin.value = 0
        assert registers.read_banked_register(b, OLAT) == (0 << p)


@forall(ps=pin_pairs, p2_value=bits, samples=5)
def test_can_write_value_of_pin_without_affecting_other_output_pins(ps, p2_value):
    (b1,p1), (b2,p2) = ps
    
    with chip[b1][p1] as pin1, chip[b2][p2] as pin2:
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
        

@forall(ps=pin_pairs, inpin_value=bits, samples=3)
def test_can_read_an_input_bit_then_write_then_read_same_bit(ps, inpin_value):
    (inb, inp), (outb, outp) = ps
    
    registers.given_gpio_inputs(inb, inpin_value<<inp)
    
    with chip[inb][inp] as inpin, chip[outb][outp] as outpin:
        inpin.direction = In
        outpin.direction = Out
        
        assert inpin.value == inpin_value
        
        outpin.value = 1
        assert inpin.value == inpin_value
        
        outpin.value = 0
        assert inpin.value == inpin_value
        
        outpin.value = 1
        assert inpin.value == inpin_value


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_can_configure_polarity(b, p):
    chip.reset()
    
    registers.given_register_value(b, IPOL, 0x00)
    
    with chip[b][p] as pin:
        assert not pin.inverted
        pin.inverted = True
        assert pin.inverted
        assert registers.read_banked_register(b, IPOL) == (1<<p)
        
        registers.given_register_value(b, IPOL, 0xFF)
        
        registers.clear_writes()
        
        assert pin.inverted
        pin.inverted = False
        assert not pin.inverted
        
        assert registers.read_banked_register(b, IPOL) == ~(1<<p) & 0xFF


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_can_configure_pull_up_resistors(b, p):
    chip.reset()
    
    registers.given_register_value(b, GPPU, 0x00)
    
    with chip[b][p] as pin:
        assert not pin.pull_up
        pin.pull_up = True
        assert pin.pull_up
        assert registers.read_banked_register(b, GPPU) == (1<<p)
        
        registers.given_register_value(b, GPPU, 0xFF)
        
        registers.clear_writes()
        
        assert pin.pull_up
        pin.pull_up = False
        assert not pin.pull_up
        
        assert registers.read_banked_register(b, GPPU) == ~(1<<p) & 0xFF


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_can_set_pin_to_interrupt_when_input_changes(b, p):
    with chip[b][p] as pin:
        registers.given_register_value(b, GPINTEN, 0)
        registers.given_register_value(b, INTCON, 0xFF)
        
        pin.bank.read_mode = deferred_read
        pin.enable_interrupts()
        
        assert registers.register_bit(b, GPINTEN, p) == 1
        assert registers.register_bit(b, INTCON, p) == 0


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_can_set_pin_to_interrupt_when_input_changes_to_specific_value(b, p):
    with chip[b][p] as pin:
        registers.given_register_value(b, GPINTEN, 0)
        registers.given_register_value(b, INTCON, 0)
        
        pin.bank.read_mode = deferred_read
        pin.enable_interrupts(value=1)
        
        assert registers.register_bit(b, GPINTEN, p) == 1
        assert registers.register_bit(b, INTCON, p) == 1

@forall(b=bank_ids, p=pin_ids, samples=3)
def test_can_disable_interrupts(b, p):
    with chip[b][p] as pin:
        pin.bank.read_mode = deferred_read
        pin.enable_interrupts()
        
        pin.disable_interrupts()
        
        assert registers.register_bit(b, GPINTEN, p) == 0\


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_issues_warning_if_interrupt_enabled_when_pin_is_in_immediate_read_mode(b, p):
    with chip[b][p] as pin:
        pin.bank.read_mode = immediate_read
        
        with catch_warnings(record=True) as warnings:
            issue_warnings("always")
            
            pin.enable_interrupts(value=1)
            
            assert len(warnings) > 0


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_issues_no_warning_if_interrupt_enabled_when_pin_is_in_deferred_read_mode(b, p):
    with chip[b][p] as pin:
        pin.bank.read_mode = deferred_read
        
        with catch_warnings(record=True) as warnings:
            issue_warnings("always")
            
            pin.enable_interrupts()
            
            print(warnings)
            assert len(warnings) == 0


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_issues_no_warning_if_interrupt_enabled_when_pin_is_in_custom_read_mode(b, p):
    def custom_read_mode(f):
        pass
    
    with chip[b][p] as pin:
        pin.bank.read_mode = custom_read_mode
        
        with catch_warnings(record=True) as warnings:
            issue_warnings("always")
            
            pin.enable_interrupts()
            
            assert len(warnings) == 0


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_must_explicitly_read_to_update_interrupt_state(b, p):
    chip.reset()
    
    with chip[b][p] as pin:
        pin.direction = In
        pin.bank.read_mode = deferred_read
        
        pin.enable_interrupts()
        
        registers.given_register_value(b, INTCAP, 1<<p)
        
        assert not pin.interrupt
        pin.bank.read()
        assert pin.interrupt


@forall(b=bank_ids, p1=pin_ids, p2=pin_ids, where=lambda b,p1,p2: p1 != p2, samples=3)
def test_in_deferred_write_mode_the_bank_caches_pin_states_until_written_to_chip(b, p1, p2):
    chip.reset()
    
    with chip[b][p1] as pin1, chip[b][p2] as pin2:
        chip[b].write_mode = deferred_write
        
        pin1.direction = Out
        pin2.direction = Out
        
        assert registers.register_value(b, IODIR) == 0xFF
        assert registers.register_value(b, OLAT) == 0x00
        
        pin1.value = True
        
        assert registers.register_value(b, OLAT) == 0x00
        
        pin1.bank.write()
        
        assert registers.register_bit(b, IODIR, p1) == 0
        assert registers.register_bit(b, IODIR, p2) == 0
        assert registers.register_bit(b, OLAT, p1) == 1



@forall(b=bank_ids, p=pin_ids, samples=3)
def test_in_deferred_write_mode_can_set_value_of_input_pin_without_explicit_reset(b,p):
    chip = PinBanks(registers)
    bank = chip[b]
    
    with bank[p] as pin:
        bank.write_mode = deferred_write
        
        pin.value = 1 
        bank.write()
        assert registers.register_bit(b, OLAT, p) == 1


@forall(b=bank_ids, p=pin_ids, samples=3)
def test_in_deferred_write_mode_a_reset_discards_outstanding_writes(b, p):
    chip.reset()
    
    bank = chip[b]
    with bank[p] as pin:
        pin.direction = Out
        bank.write_mode = deferred_write
        
        pin.value = 1
        chip.reset()
        
        registers.clear_writes()
        bank.write()
        
        assert registers.writes == []


class FakeRegisters(Registers):
    """Note - does not simulate effect of the IPOL{A,B} registers."""
    
    def __init__(self):
        self.registers = [0]*(BANK_SIZE*2)
        self.writes = []
        self.reset()
    
    def write_register(self, reg, value):
        self.writes.append((reg, value))
        
        if reg in (IOCONA, IOCONB):
            self.registers[IOCONA] = value
            self.registers[IOCONB] = value
        elif reg == GPIOA:
            self.registers[OLATA] = value
        elif reg == GPIOB:
            self.registers[OLATB] = value
        elif reg not in (INTFA, INTFB, INTCAPA, INTCAPB):
            self.registers[reg] = value
    
    def read_register(self, reg):
        if reg == GPIOA:
            value = (self.registers[GPIOA] & self.registers[IODIRA]) | (self.registers[OLATA] & ~self.registers[IODIRA])
        elif reg == GPIOB:
            value = (self.registers[GPIOB] & self.registers[IODIRB]) | (self.registers[OLATB] & ~self.registers[IODIRB])
        else:
            value = self.registers[reg]

        if reg in (INTCAPA, GPIOA):
            self.registers[INTCAPA] = 0
        elif reg in (INTCAPB, GPIOB):
            self.registers[INTCAPB] = 0
          
        return value
    
    def register_value(self, bank, reg):
        return self.registers[_banked_register(bank,reg)]
    
    def register_bit(self, bank, reg, bit):
        return (self.register_value(bank,reg) >> bit) & 0x01
    
    def given_gpio_inputs(self, bank, value):
        self.given_register_value(bank, GPIO, value)
    
    def given_register_value(self, bank, reg, value):
        self.registers[_banked_register(bank,reg)] = value
    
    def print_registers(self):
        for reg, value in zip(count(), self.registers):
            print(register_names[reg].ljust(8) + " = " + "%02X"%value)
    
    def print_writes(self):
        for reg, value in self.writes:
            print(register_names[reg].ljust(8) + " := " + "%02X"%value)

    def clear_writes(self):
        self.writes = []
        
    def __repr__(self):
        return type(self).__name__ + "()"
    
    def __str__(self):
        return repr(self)


