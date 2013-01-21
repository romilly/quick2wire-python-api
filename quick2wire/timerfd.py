

import math
import os
from ctypes import *
import struct
import quick2wire.syscall as syscall


# From <time.h>

time_t = c_long

clockid_t = c_ulong

class timespec(Structure):
    _fields_ = [("tv_sec", time_t),
                ("tv_nsec", c_long)]
    
    __slots__ = [name for name,type in _fields_]
    
    @classmethod
    def from_seconds(cls, secs):
        t = cls()
        t.seconds = secs
        return t
    
    @property
    def seconds(self):
        if self.tv_nsec == 0:
            return self.tv_sec
        else:
            return self.tv_sec + self.tv_nsec / 1000000000.0
        
    @seconds.setter
    def seconds(self, secs):
        fractional, whole = math.modf(secs)
        self.tv_sec = int(whole)
        self.tv_nsec = int(fractional * 1000000000)


class itimerspec(Structure):
    _fields_ = [("it_interval", timespec), 
                ("it_value", timespec)]
    
    __slots__ = [name for name,type in _fields_]
    
    @classmethod
    def from_seconds(cls, offset, interval):
        spec = cls()
        spec.it_value.seconds = offset
        spec.it_interval.seconds = interval
        return spec


# from <bits/time.h>

CLOCK_REALTIME           = 0 # Identifier for system-wide realtime clock.
CLOCK_MONOTONIC	         = 1 # Monotonic system-wide clock.
CLOCK_PROCESS_CPUTIME_ID = 2 # High-resolution timer from the CPU
CLOCK_THREAD_CPUTIME_ID	 = 3 # Thread-specific CPU-time clock. 
CLOCK_MONOTONIC_RAW      = 4 # Monotonic system-wide clock, not adjusted for frequency scaling. 
CLOCK_REALTIME_COARSE    = 5 # Identifier for system-wide realtime clock, updated only on ticks. 
CLOCK_MONOTONIC_COARSE   = 6 # Monotonic system-wide clock, updated only on ticks. 
CLOCK_BOOTTIME	         = 7 # Monotonic system-wide clock that includes time spent in suspension. 
CLOCK_REALTIME_ALARM     = 8 # Like CLOCK_REALTIME but also wakes suspended system.
CLOCK_BOOTTIME_ALARM     = 9 # Like CLOCK_BOOTTIME but also wakes suspended system.


# From <sys/timerfd.h>

# Bits to be set in the FLAGS parameter of `timerfd_create'.
TFD_CLOEXEC = 0o2000000,
TFD_NONBLOCK = 0o4000

# Bits to be set in the FLAGS parameter of `timerfd_settime'.
TFD_TIMER_ABSTIME = 1 << 0



# Return file descriptor for new interval timer source.
#
# extern int timerfd_create (clockid_t __clock_id, int __flags)

timerfd_create = syscall.lookup(c_int, "timerfd_create", (clockid_t, c_int))

# Set next expiration time of interval timer source UFD to UTMR.  If
# FLAGS has the TFD_TIMER_ABSTIME flag set the timeout value is
# absolute.  Optionally return the old expiration time in OTMR.
#
# extern int timerfd_settime (int __ufd, int __flags,
# 			      __const struct itimerspec *__utmr,
# 			      struct itimerspec *__otmr)
timerfd_settime = syscall.lookup(c_int, "timerfd_settime", (c_int, c_int, POINTER(itimerspec), POINTER(itimerspec)))

# Return the next expiration time of UFD.
#
# extern int timerfd_gettime (int __ufd, struct itimerspec *__otmr)

timerfd_gettime = syscall.lookup(c_int, "timerfd_gettime", (c_int, POINTER(itimerspec)))


class Timer:
    def __init__(self, clock=CLOCK_REALTIME, blocking=True):
        self._fd = timerfd_create(clock, (not blocking)*TFD_NONBLOCK)
        if self._fd < 0:
            e = get_errno()
            raise OSError(e, errno.strerror(e))
    
    def close(self):
        os.close(self._fd)
    
    def schedule(self, offset=0, interval=0):
        spec = itimerspec(it_value=timespec.from_seconds(offset), 
                          it_interval=timespec.from_seconds(interval))
        
        print(spec)
        
        status = timerfd_settime(self._fd, 0, byref(spec), None)
        if status < 0:
            e = get_errno()
            raise OSError(e, errno.strerror(e))
    
    def wait(self):
        try:
            buf = os.read(self._fd, 8)
            return struct.unpack("Q", buf)[0]
        except OSError as e:
            if e.errno == errno.EAGAIN:
                return 0
            else:
                raise e
        
