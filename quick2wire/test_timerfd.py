
from time import time
from contextlib import closing
from quick2wire.timerfd import Timer, timespec, itimerspec


def test_timespec_can_be_created_from_seconds():
    t = timespec.from_seconds(4.125)
    assert t.tv_sec == 4
    assert t.tv_nsec == 125000000

def test_itimerspec_can_be_created_from_seconds():
    t = itimerspec.from_seconds(offset=4.125, interval=1.25)
    assert t.it_value.tv_sec == 4
    assert t.it_value.tv_nsec == 125000000
    assert t.it_interval.tv_sec == 1
    assert t.it_interval.tv_nsec == 250000000

def test_timer_waits_for_time_to_pass():
    with closing(Timer()) as timer:
        start = time()
        timer.schedule(0.125)
        n = timer.wait()
        duration = time() - start
        
        assert duration / n >= 0.125
