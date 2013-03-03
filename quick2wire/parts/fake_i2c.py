__author__ = 'stuart'

class FakeI2CMaster:
    def __init__(self):
        self._requests = []
        self._responses = []
        self._next_response = 0
        self.message_precondition = lambda m: True

    def all_messages_must(self, p):
        self.message_precondition

    def clear(self):
        self.__init__()

    def transaction(self, *messages):
        for m in messages:
            self.message_precondition(m)

        self._requests.append(messages)
        return []

    def add_response(self, *messages):
        self._responses.append(messages)


    @property
    def request_count(self):
        return len(self._requests)

    def request(self, n):
        return self._requests[n]

    def request_at(self, n):
        return I2CRequestWrapper(self._requests[n])

    def message(self, message_index):
        request = self.request(0)
        return I2CMessageWrapper(request[message_index])

class I2CRequestWrapper:
    def __init__(self, i2c_request):
            self._i2c_request = i2c_request

    def message(self, index):
        return I2CMessageWrapper(self._i2c_request[index])


class I2CMessageWrapper:
    def __init__(self, i2_message):
        self._i2c_message = i2_message
        self.len = i2_message.len

    def byte(self, index):
        return self._i2c_message.buf[index][0]

