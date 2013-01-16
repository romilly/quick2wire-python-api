

import select

INPUT = select.EPOLLIN
OUTPUT = select.EPOLLOUT
ERROR = select.EPOLLERR
HANGUP = select.EPOLLHUP
PRIORITY_INPUT = select.EPOLLPRI

LEVEL = 0
EDGE = 1


class Selector:
    def __init__(self, size_hint=-1):
        self._epoll = select.epoll(size_hint)
        self._sources = {}
        self.ready = None
        self.events = 0
        
    def fileno(self):
        return self._epoll.fileno()
    
    def add(self, source, eventmask, trigger=LEVEL, identifier=None):
        fileno = source.fileno()
        self._sources[fileno] = identifier if identifier is not None else source
        self._epoll.register(fileno, eventmask|(select.EPOLLET*trigger))
    
    def remove(self, source):
        fileno = source.fileno()
        self._epoll.unregister(source)
        del self._sources[fileno]

    def wait(self, timeout=-1):
        self.ready = None
        self.events = 0
        
        readies = self._epoll.poll(timeout, maxevents=1)
        if readies:
            fileno, self.events = readies[0]
            self.ready = self._sources[fileno]
            
    @property
    def has_input(self):
        return bool(self.events & INPUT)
    
    @property
    def has_output(self):
        return bool(self.events & OUTPUT)
    
    @property
    def has_error(self):
        return bool(self.events & ERROR)
    
    @property
    def has_hangup(self):
        return bool(self.events & HANGUP)
    
    @property
    def has_priority_input(self):
        return bool(self.events & PRIORITY_INPUT)
    
    def close(self):
        self._epoll.close()
        
