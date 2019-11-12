import simpy as sp
from abc import abstractmethod, ABC


class LoadBalancer(sp.resources.store.Store, ABC):
    def __init__(self, env, capacity=float('inf'), admission_rate=1):
        super().__init__(env, capacity)
        self._servers = []
        self.admission_rate = admission_rate
        self._request_available = sp.events.Event(env).succeed()

    @property
    def admission_rate(self):
        return self._admission_rate

    @admission_rate.setter
    def admission_rate(self, u_adm):
        if u_adm <= 0:
            raise ValueError(
                f"Admission rate must be positive, but passed value is {u_adm}"
            )
        self._admission_rate = u_adm

    def submit_request(self, request):
        e = self.put(request)
        if not self._request_available.triggered:
            self._request_available.succeed()
        return e

    def add_server(self, *servers):
        self._servers = list(set([*self._servers, *servers]))

    def worker_loop(self):
        while True:
            if self.items and len(self.items):
                request = yield self.get()
                self.route(request)
                yield self._env.timeout(1/self._admission_rate)
            else:
                del self._request_available
                self._request_available = sp.events.Event(self._env)
                yield self._request_available

    @abstractmethod
    def route(self, request):
        pass
