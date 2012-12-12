
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
            with chip.banks[b][p] as pin:
                yield pin

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
def test_can_read_logical_value_of_input_pin(p):
    p.direction = In
    
    registers.given_gpio_inputs(p.bank.index, 1 << p.index)
    assert p.value == 1
    
    registers.given_gpio_inputs(p.bank.index, 0)
    assert p.value == 0


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
        

@forall(ps=permutations(product(bank_ids, pin_ids), 2), inpin_value=bits)
def test_can_read_an_input_bit_then_write_then_read_same_bit(ps, inpin_value):
    (inb, inp), (outb, outp) = ps
    
    registers.given_gpio_inputs(inb, inpin_value<<inp)
    
    with chip.banks[inb][inp] as inpin, chip.banks[outb][outp] as outpin:
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
    
    print("registers:")
    registers.print_registers()
    print("writes:")
    registers.print_writes()
    
    assert registers.read_banked_register(pin.bank.index, GPPU) == ~(1<<pin.index) & 0xFF



@forall(pin=all_pins_of_chip())
def test_can_set_pin_to_interrupt_on_change(pin):
    registers.given_register_value(pin.bank.index, GPINTEN, 0)
    registers.given_register_value(pin.bank.index, INTCON, 0xFF)
    
    pin.interrupt_on_change()
    
    assert registers.register_bit(pin.bank.index, GPINTEN, pin.index) == 1
    assert registers.register_bit(pin.bank.index, INTCON, pin.index) == 0




register_names = sorted([s for s in dir(mcp23x17) if s[-1] in ('A','B') and s.upper() == s], 
                        key=lambda s: getattr(mcp23x17, s))

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
        if reg in (INTCAPA, GPIOA):
            self.registers[INTCAPA] = 0
        
        if reg in (INTCAPB, GPIOB):
            self.registers[INTCAPB] = 0
        
        if reg == GPIOA:
            return (self.registers[GPIOA] & self.registers[IODIRA]) | (self.registers[OLATA] & ~self.registers[IODIRA])
        elif reg == GPIOB:
            return (self.registers[GPIOB] & self.registers[IODIRB]) | (self.registers[OLATB] & ~self.registers[IODIRB])
        else:
            return self.registers[reg]
    
    def register_bit(self, bank, register, bit):
        return (self.read_register(_banked_register(bank,register)) >> bit) & 0x01
    
    def given_gpio_inputs(self, bank, value):
        self.given_register_value(bank, GPIO, value)
    
    def given_register_value(self, bank, reg, value):
        self.registers[_banked_register(bank,reg)] = value
    
    def print_registers(self):
        for reg,value in zip(count(), self.registers):
            print(register_names[reg].ljust(8) + " = " + "%02X"%value)

    def print_writes(self):
        for reg,value in self.writes:
            print(register_names[reg].ljust(8) + " := " + "%02X"%value)

    def clear_writes(self):
        self.writes = []
