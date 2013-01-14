
from ctypes import *
import os

EFD_SEMAPHORE = 1
EFD_CLOEXEC = 0o2000000
EFD_NONBLOCK = 0o4000

_libc = cdll.LoadLibrary(None)

eventfd_t = c_uint64
eventfd = _libc.eventfd
eventfd_read = _libc.eventfd_read
eventfd_write = _libc.eventfd_write


class Semaphore:
    """A Semaphore implemented with eventfd so that it can be used with epoll."""
    def __init__(self):
        self._fd = eventfd(0, EFD_SEMAPHORE)
    
    def close(self):
        os.close(self._fd)
    
    def fileno(self):
        return self._fd
    
    def signal(self, n=1):
        eventfd_write(self._fd, c_int64(n))
    
    def ack(self, n=1):
        buf = c_int64()
        eventfd_read(self._fd, buf)
        
