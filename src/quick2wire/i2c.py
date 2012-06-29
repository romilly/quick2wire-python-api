
from contextlib import closing
import posix
from fcntl import ioctl
from quick2wire.i2c_ctypes import *
from ctypes import create_string_buffer, sizeof, c_int, byref, pointer, addressof


def read(addr, n_bytes):
    return read_into(addr, create_string_buffer(n_bytes))

def read_into(addr, buf):
    return _new_i2c_msg(addr, I2C_M_RD, buf)

def write_bytes(addr, *bytes):
    return write(addr, bytes)

def write(addr, byte_seq):
    buf = bytes(byte_seq)
    return _new_i2c_msg(addr, 0, create_string_buffer(buf, len(buf)))

def _new_i2c_msg(addr, flags, buf):
    return i2c_msg(addr=addr, flags=flags, len=sizeof(buf), buf=buf)



_I2CFuncs = (
    ("I2C_FUNC_I2C", I2C_FUNC_I2C),
    ("I2C_FUNC_10BIT_ADDR", I2C_FUNC_10BIT_ADDR),
    ("I2C_FUNC_PROTOCOL_MANGLING", I2C_FUNC_PROTOCOL_MANGLING))


class I2CBus:
    def __init__(self, n=0, extra_open_flags=0):
        self.fd = posix.open("/dev/i2c-%i"%n, posix.O_RDWR|extra_open_flags)
    
    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        posix.close(self.fd)
    
    def funcs(self):
        flags = c_int()
        ioctl(self.fd, I2C_FUNCS, addressof(flags))
        return [name for (name, flag) in _I2CFuncs if flags.value&flag]
    
    def transaction(self, *msgs):
        msg_count = len(msgs)
        msg_array = (i2c_msg*msg_count)(*msgs)
        ioctl_arg = i2c_rdwr_ioctl_data(msgs=msg_array, nmsgs=msg_count)
        
        ioctl(self.fd, I2C_RDWR, addressof(ioctl_arg))
        
        return [bytes(m.buf.contents) for m in msgs if (m.flags & I2C_M_RD)]
    
    def _write_bytes(self, *bytes_as_list):
        return self._write(bytes(bytes_as_list))
    
    def _write(self, bytes):
        return posix.write(self.fd, bytes)
    
    def _read(self, n_bytes):
        return posix.read(self.fd, n_bytes)

