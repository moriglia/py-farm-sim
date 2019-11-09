import simpy as sp


class WebRequest(sp.Event):
    next_id = 0

    def __init__(self, env, time=0, timeout=0):
        self.id = self.__class__.next_id
        self.__class__.next_id += 1

        super().__init__(env)
        self._timeout = timeout
        self._time = time

    @property
    def time(self):
        return self._time

    def submit_to(self, proc):
        self.env.process(proc(self.env, self))

    def set_timeout(self, timeout):
        self._timeout = timeout

    def wait_for_completion(self):
        if not self._timeout:
            return self

        return self | self.env.timeout(self._timeout)
