from ctypes import addressof, create_string_buffer, sizeof, string_at
import posix
from fcntl import ioctl
from quick2wire.spi_ctypes import *
from quick2wire.spi_ctypes import spi_ioc_transfer, SPI_IOC_MESSAGE


class SPIDevice:
    def __init__(self, chip_select, bus):
        self.fd = posix.open("/dev/spidev%i.%i"%(bus,chip_select), posix.O_RDWR)

    def transaction(self, *transfers):
        transfer_count = len(transfers)
        ioctl_arg = (spi_ioc_transfer*transfer_count)()

        # populate array from transfers
        for i, transfer in enumerate(transfers):
            ioctl_arg[i] = transfers[i].to_spi_ioc_transfer()

        ioctl(self.fd, SPI_IOC_MESSAGE(transfer_count), addressof(ioctl_arg))

        return [transfer.to_read_bytes() for t in transfers if t.has_read_buf]

    def close(self):
        posix.close(self.fd)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class _SPITransfer:
    def __init__(self, write_byte_seq = None, read_byte_count = None):
        if write_byte_seq is not None:
            self.write_bytes = bytes(write_byte_seq)
            self.write_buf = create_string_buffer(self.write_bytes, len(self.write_bytes))
        else:
            self.write_bytes = None
            self.write_buf = None
        
        if read_byte_count is not None:
            self.read_buf = create_string_buffer(read_byte_count)
        else:
            self.read_buf = None
    
    def to_spi_ioc_transfer(self):
        return spi_ioc_transfer(
            tx_buf=_safe_address_of(self.write_buf),
            rx_buf=_safe_address_of(self.read_buf),
            len=_safe_size_of(self.write_buf, self.read_buf))

    @property
    def has_read_buf(self):
        return self.read_buf is not None

    def to_read_bytes(self):
        return string_at(self.read_buf, sizeof(self.read_buf))


def _safe_size_of(write_buf, read_buf):
    if write_buf is not None and read_buf is not None:
        assert sizeof(write_buf) == sizeof(read_buf)
        return sizeof(write_buf)
    elif write_buf is not None:
        return sizeof(write_buf)
    else:
        return sizeof(read_buf)

def _safe_address_of(buf):
    return 0 if buf is None else addressof(buf)

def duplex(write_byte_sequence):
    return _SPITransfer(write_byte_seq=write_byte_sequence, read_byte_count=len(write_byte_sequence))

def duplex_bytes(*write_bytes):
    return duplex(write_bytes)

def reading(byte_count):
    return _SPITransfer(read_byte_count=byte_count)

def writing(byte_sequence):
    return _SPITransfer(write_byte_seq=byte_sequence)

def writing_bytes(*byte_values):
    return writing(byte_values)

