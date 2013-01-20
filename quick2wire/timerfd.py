

import math
from ctypes import *

# From <time.h>

time_t = c_long

class timespec(Structure):
    _fields_ = [("tv_sec", time_t),
                ("tv_nsec", c_long)]

class itimerspec(Structure):
    _fields_ = [("it_interval", timespec), 
                ("it_value", timespec)]

clockid_t = c_ulong


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



_libc = CDLL(None, use_errno=True)

# Return file descriptor for new interval timer source.
#
# extern int timerfd_create (clockid_t __clock_id, int __flags)

timerfd_create = _libc.timerfd_create
timerfd_create.argtypes = [clockid_t, c_int]
timerfd_create.restype = c_int

# Set next expiration time of interval timer source UFD to UTMR.  If
# FLAGS has the TFD_TIMER_ABSTIME flag set the timeout value is
# absolute.  Optionally return the old expiration time in OTMR.
#
# extern int timerfd_settime (int __ufd, int __flags,
# 			      __const struct itimerspec *__utmr,
# 			      struct itimerspec *__otmr)
timerfd_settime = _libc.timerfd_settime
timerfd_settime.argtypes = [c_int, c_int, POINTER(itimerspec), POINTER(itimerspec)]
timerfd_settime.restype = c_int

# Return the next expiration time of UFD.
#
# extern int timerfd_gettime (int __ufd, struct itimerspec *__otmr)

timerfd_gettime = _libc.timerfd_gettime
timerfd_gettime.argtypes = [c_int, POINTER(itimerspec)]
timerfd_gettime.restype = c_int


def seconds_to_timespec(secs):
    fractional, whole = math.modf(secs)
    return timespec(tv_secs=time_t(int(whole)),
                    tv_nsecs=c_long(int(fractional*1000000.0)))

class Timer:
    def __init__(self, clock, blocking=True):
        self._fd = timerfd_create(clock, (not blocking)*TFD_NONBLOCK)
        if self._fd < 0:
            e = get_errno()
            raise OSError(e, errno.strerror(e))


    def schedule(offset=0, interval=0):
        pass
