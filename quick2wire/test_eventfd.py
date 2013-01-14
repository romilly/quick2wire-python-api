
from select import epoll, EPOLLIN
from contextlib import closing
from quick2wire.eventfd import Semaphore



def test_can_signal_and_poll_an_eventfd():
    with closing(Semaphore()) as s, closing(epoll()) as poller:
        poller.register(s, EPOLLIN)
        
        s.signal()
        
        assert poller.poll(timeout=0) == [(s.fileno(), EPOLLIN)]

def test_can_acknowledge_a_signal():
    with closing(Semaphore()) as s, closing(epoll()) as poller:
        poller.register(s, EPOLLIN)
        
        s.signal()
        
        poller.poll(timeout=0)
        
        s.ack()
        
        assert poller.poll(timeout=0) == []

