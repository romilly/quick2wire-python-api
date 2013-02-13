
from time import time, sleep
from quick2wire.timerfd import Timer, timespec, itimerspec
import pytest


@pytest.mark.loopback
@pytest.mark.timer
def test_timespec_can_be_created_from_seconds():
    t = timespec.from_seconds(4.125)
    assert t.sec == 4
    assert t.nsec == 125000000


@pytest.mark.loopback
@pytest.mark.timer
def test_itimerspec_can_be_created_from_seconds():
    t = itimerspec.from_seconds(offset=4.125, interval=1.25)
    assert t.value.sec == 4
    assert t.value.nsec == 125000000
    assert t.interval.sec == 1
    assert t.interval.nsec == 250000000


@pytest.mark.loopback
@pytest.mark.timer
def test_timer_waits_for_time_to_pass():
    with Timer(offset=0.125) as timer:
        start = time()
        
        timer.start()
        timer.wait()
        
        duration = time() - start
        
        assert duration >= 0.125


@pytest.mark.loopback
@pytest.mark.timer
def test_timer_can_repeat_with_interval():
    with Timer(interval=0.125) as timer:
        start = time()
        
        timer.start()
        timer.wait()
        timer.wait()
        
        duration = time() - start
        
        assert duration >= 0.25


@pytest.mark.loopback
@pytest.mark.timer
def test_timer_can_repeat_with_interval_after_offset():
    with Timer(offset=0.25, interval=0.125) as timer:
        start = time()
        
        timer.start()
        timer.wait()
        timer.wait()
        timer.wait()
        
        duration = time() - start
        
        assert duration >= 0.5


@pytest.mark.loopback
@pytest.mark.timer
def test_can_change_offset_while_timer_is_running():
    with Timer(offset=1.0) as timer:
        start = time()
        timer.start()
        timer.offset = 0.125
        timer.wait()
        
        duration = time() - start
        
        assert duration < 1


@pytest.mark.loopback
@pytest.mark.timer
def test_can_change_interval_while_timer_is_running():
    with Timer(offset=0.125, interval=1.0) as timer:
        start = time()
        timer.start()
        timer.wait()
        timer.interval = 0.125
        timer.wait()
        
        duration = time() - start
        
        assert duration < 1


@pytest.mark.loopback
@pytest.mark.timer
def test_timer_cannot_be_started_if_offset_and_interval_are_both_zero():
    with Timer() as timer:
        try:
            timer.start()
            assert False, "should have thrown ValueError"
        except ValueError:
            # expected
            pass


@pytest.mark.loopback
@pytest.mark.timer
def test_timer_reports_how_many_times_it_triggered_since_last_wait():
    with Timer(interval=0.0125) as timer:
        timer.start()
        sleep(0.5)
        n = timer.wait()
        
        assert n >= 4
