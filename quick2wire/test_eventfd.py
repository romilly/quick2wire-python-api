
from select import epoll, EPOLLIN
from contextlib import closing
from quick2wire.eventfd import Semaphore



def test_can_signal_poll_and_receive_a_semaphore():
    with closing(Semaphore()) as s, closing(epoll()) as poller:
        poller.register(s, EPOLLIN)
        
        assert poller.poll(timeout=0) == []
        
        s.signal()
        
        assert poller.poll(timeout=0) == [(s.fileno(), EPOLLIN)]
        assert poller.poll(timeout=0) == [(s.fileno(), EPOLLIN)]
        
        assert s.wait() == True
        
        assert poller.poll(timeout=0) == []


def test_can_initialise_a_semaphore_with_a_count():
    with closing(Semaphore(1)) as s, closing(epoll()) as poller:
        poller.register(s, EPOLLIN)
        
        assert poller.poll(timeout=0) == [(s.fileno(), EPOLLIN)]
         

def test_a_semaphore_can_be_nonblocking():
    with closing(Semaphore(blocking=False)) as s, closing(epoll()) as poller:
        poller.register(s, EPOLLIN)
        
        assert s.wait() == False
        assert poller.poll(timeout=0) == []
        
        s.signal()
        
        assert poller.poll(timeout=0) == [(s.fileno(), EPOLLIN)]
        assert poller.poll(timeout=0) == [(s.fileno(), EPOLLIN)]
        
        assert s.wait() == True
        
        assert s.wait() == False
        assert poller.poll(timeout=0) == []
        

