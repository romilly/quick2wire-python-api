
from itertools import product, permutations, count
import quick2wire.parts.mcp23x17 as mcp23x17
from quick2wire.parts.mcp23x17 import *
from quick2wire.parts.mcp23x17 import _banked_register
from factcheck import *

print(dir(mcp23x17))

bits = (1,0)
bank_ids = range(2)
pin_ids = range(8)

def all_pins_of_chip():
    global chip
    
    for b in bank_ids:
        for p in pin_ids:
            with chip[b][p] as pin:
                yield pin

def setup_function(function=None):
    global chip, registers
    
    registers = FakeRegisters()
    chip = PinBanks(registers)
    chip.reset()


def test_has_two_banks_of_eight_pins():
    assert len(chip) == 2
    for b in bank_ids:
        assert len(chip[b]) == 8

@forall(b=bank_ids, p=pin_ids)
def test_all_pins_report_their_bank_and_index(b, p):
    assert chip[b][p].bank == chip[b]
    assert chip[b][p].index == p


@forall(b=bank_ids, p=pin_ids)
def test_can_use_a_context_manager_to_claim_ownership_of_a_pin_in_a_bank_and_release_it(b, p):
    with chip[b][p] as pin:
        try :
            with chip[b][p] as pin2:
                raise AssertionError("claiming the pin should have failed")
        except ValueError as e:
            pass


@forall(b=bank_ids, p=pin_ids)
def test_a_pin_can_be_claimed_after_being_released(b, p):
    with chip[b][p] as pin:
        pass
    
    with chip[b][p] as pin_again:
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
def test_can_read_logical_value_of_input_pin(p):
    chip.reset()
    
    p.direction = In
    
    registers.given_gpio_inputs(p.bank.index, 1 << p.index)
    assert p.value == 1
    
    registers.given_gpio_inputs(p.bank.index, 0)
    assert p.value == 0


@forall(b = bank_ids)
def test_initially_banks_are_in_automatic_mode(b):
    assert chip[b].read_mode == automatic_read
    assert chip[b].write_mode == automatic_write


@forall(b = bank_ids, p=pin_ids)
def test_in_explicit_read_mode_bank_must_be_read_explicitly_before_pin_value_is_visible(b, p):
    chip.reset()
    
    bank = chip[b]
    
    bank.read_mode = explicit_read
    
    with bank[p] as pin:
        registers.given_gpio_inputs(b, 0)
        
        assert pin.value == 0
        
        registers.given_gpio_inputs(b, 1<<p)
        
        assert pin.value == 0
        
        bank.read()
        
        assert pin.value == 1


@forall(p=all_pins_of_chip())
def test_can_set_pin_to_output_mode_and_set_its_logical_value(p):
    p.direction = Out
    p.value = 1
    
    assert registers.read_banked_register(p.bank.index, OLAT) == (1 << p.index)
    
    p.value = 0
    assert registers.read_banked_register(p.bank.index, OLAT) == (0 << p.index)


@forall(ps=permutations(product(bank_ids, pin_ids), 2), p2_value=bits)
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
        

@forall(ps=permutations(product(bank_ids, pin_ids), 2), inpin_value=bits)
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


@forall(pin=all_pins_of_chip())
def test_can_configure_pull_down_resistors(pin):
    chip.reset()
    
    registers.given_register_value(pin.bank.index, GPPU, 0x00)
    
    assert pin.pull_down == False
    pin.pull_down = True
    assert pin.pull_down == True
    assert registers.read_banked_register(pin.bank.index, GPPU) == (1<<pin.index)
    
    registers.given_register_value(pin.bank.index, GPPU, 0xFF)
    
    registers.clear_writes()
    
    assert pin.pull_down == True
    pin.pull_down = False
    assert pin.pull_down == False
    
    assert registers.read_banked_register(pin.bank.index, GPPU) == ~(1<<pin.index) & 0xFF


@forall(pin=all_pins_of_chip())
def test_can_set_pin_to_interrupt_on_change(pin):
    registers.given_register_value(pin.bank.index, GPINTEN, 0)
    registers.given_register_value(pin.bank.index, INTCON, 0xFF)
    
    pin.interrupt_on_change()
    
    assert registers.register_bit(pin.bank.index, GPINTEN, pin.index) == 1
    assert registers.register_bit(pin.bank.index, INTCON, pin.index) == 0


@forall(pin=all_pins_of_chip())
def test_can_set_pin_to_interrupt_when_input_set_to_specific_value(pin):
    registers.given_register_value(pin.bank.index, GPINTEN, 0)
    registers.given_register_value(pin.bank.index, INTCON, 0)
    
    pin.interrupt_when(1)
    
    assert registers.register_bit(pin.bank.index, GPINTEN, pin.index) == 1
    assert registers.register_bit(pin.bank.index, INTCON, pin.index) == 1


@forall(pin=all_pins_of_chip())
def test_must_explicitly_read_to_update_interrupt_state(pin):
    chip.reset()
    
    pin.direction = In
    pin.bank.read_mode = explicit_read
    
    pin.interrupt_on_change()
    
    registers.given_register_value(pin.bank.index, INTCAP, 1<<pin.index)
    
    assert not pin.interrupt
    pin.bank.read()
    assert pin.interrupt


@forall(b=bank_ids, p1=pin_ids, p2=pin_ids, where=lambda b,p1,p2: p1 != p2, samples=5)
def test_in_explicit_write_mode_the_bank_caches_pin_states_until_written_to_chip(b, p1, p2):
    chip.reset()
    
    with chip[b][p1] as pin1, chip[b][p2] as pin2:
        chip[b].write_mode = explicit_write
        
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



class FakeRegisters(Registers):
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
