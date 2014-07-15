
from contextlib import closing
from itertools import islice
from quick2wire.selector import Selector, INPUT, OUTPUT, ERROR, Semaphore, Timer


def test_selector_is_a_convenient_api_to_epoll():
    selector = Selector()
    ev1 = Semaphore(blocking=False)
    with selector, ev1:
        selector.add(ev1, INPUT)
        
        ev1.signal()
        
        selector.wait()
        assert selector.ready == ev1
        assert selector.has_input == True
        assert selector.has_output == False
        assert selector.has_error == False
        assert selector.has_hangup == False
        assert selector.has_priority_input == False


def test_event_mask_defaults_to_input_and_error():
    selector = Selector()
    ev1 = Semaphore(blocking=False)
    with selector, ev1:
        selector.add(ev1)
        ev1.signal()
        
        selector.wait(timeout=0)
        assert selector.ready == ev1
        assert selector.has_input == True


def test_selecting_from_multiple_event_sources():
    selector = Selector()
    ev1 = Semaphore(blocking=False)
    ev2 = Semaphore(blocking=False)
    with selector, ev1, ev2:
        selector.add(ev1, INPUT)
        selector.add(ev2, INPUT)
        
        ev1.signal()
        ev2.signal()
        
        selector.wait()
        first = selector.ready
        first.wait()
        
        selector.wait()
        second = selector.ready
        second.wait()
        
        assert first in (ev1, ev2)
        assert second in (ev1, ev2)
        assert first is not second
        
        
def test_can_use_a_different_value_to_identify_the_event_source():
    selector = Selector()
    ev1 = Semaphore(blocking=False)
    with selector, ev1:
        selector.add(ev1, INPUT, identifier=999)
        
        ev1.signal()
        
        selector.wait()
        assert selector.ready == 999

        
def test_can_wait_with_a_timeout():
    selector = Selector()
    ev1 = Semaphore(blocking=False)
    with selector, ev1:
        selector.add(ev1, INPUT, identifier=999)
        
        selector.wait(timeout=0)
        assert selector.ready == None


def test_can_remove_source_from_selector():
    selector = Selector()
    ev1 = Semaphore(blocking=False)
    with selector, ev1:
        selector.add(ev1, INPUT)
        
        ev1.signal()
        
        selector.wait(timeout=0)
        assert selector.ready == ev1
        
        selector.remove(ev1)
        
        selector.wait(timeout=0)
        assert selector.ready == None


def test_can_wait_for_timer():
    selector = Selector()
    timer = Timer(blocking=False,offset=0.0125)
    with selector, timer:
        selector.add(timer, INPUT)
        
        timer.start()
        
        selector.wait()
        
        assert selector.ready == timer
