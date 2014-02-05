class PinAPI(object):
    def __init__(self, bank, index):
        self._bank = bank
        self._index = index

    @property
    def index(self):
        return self._index

    @property
    def bank(self):
        return self._bank

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    value = property(lambda p: p.get(),
                     lambda p,v: p.set(v),
                     doc="""The value of the pin: 1 if the pin is high, 0 if the pin is low.""")


class PinBankAPI(object):
    def __getitem__(self, n):
        if 0 < n < len(self):
            raise ValueError("no pin index {n} out of range", n=n)
        return self.pin(n)

    def write(self):
        pass

    def read(self):
        pass