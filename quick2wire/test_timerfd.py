
from time import time, sleep
from quick2wire.timerfd import Timer, timespec, itimerspec


def test_timespec_can_be_created_from_seconds():
    t = timespec.from_seconds(4.125)
    assert t.sec == 4
    assert t.nsec == 125000000


def test_itimerspec_can_be_created_from_seconds():
    t = itimerspec.from_seconds(offset=4.125, interval=1.25)
    assert t.value.sec == 4
    assert t.value.nsec == 125000000
    assert t.interval.sec == 1
    assert t.interval.nsec == 250000000


def test_timer_waits_for_time_to_pass():
    with Timer(offset=0.125) as timer:
        start = time()
        
        timer.start()
        timer.wait()
        
        duration = time() - start
        
        assert duration >= 0.125


def test_timer_can_repeat_with_interval():
    with Timer(interval=0.125) as timer:
        start = time()
        
        timer.start()
        timer.wait()
        timer.wait()
        
        duration = time() - start
        
        assert duration >= 0.25


def test_timer_can_repeat_with_interval_after_offset():
    with Timer(offset=0.25, interval=0.125) as timer:
        start = time()
        
        timer.start()
        timer.wait()
        timer.wait()
        timer.wait()
        
        duration = time() - start
        
        assert duration >= 0.5


def test_timer_cannot_be_started_if_offset_and_interval_are_both_zero():
    with Timer() as timer:
        try:
            timer.start()
            assert False, "should have thrown ValueError"
        except ValueError:
            # expected
            pass


def test_timer_reports_how_many_times_it_triggered_since_last_wait():
    with Timer(interval=0.0125) as timer:
        timer.start()
        sleep(0.5)
        n = timer.wait()
        
        assert n >= 4
