import simpy as sp
from . import server as pyfarmsrv
from abc import abstractmethod, ABC


class LoadBalancer(sp.resources.store.Store, ABC):
    """
    This class stores the incoming requests and forwards them at a rate
    defined by the user. A user can specify the admission rate (the rate at
    which requests are forwarded) by the its property setter.

    Since there might be multiple servers to which to forward the requests,
    the route() function is used to accomplish this task.

    The route() function, as well as the add_server() functions are not defined.
    The user must subclass the LoadBalancer to define them and exploit the
    features of this class.

    After subclassing and creating an instance of the subclass, in order to
    start the request routing activity, the user must start() it.
    """
    def __init__(self, env, capacity=float('inf'), admission_rate=1):
        super().__init__(env, capacity)
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

    def __submit_request(self, request):
        e = self.put(request)
        yield e
        if not (e.triggered and e.ok):
            self.active_process.fail(
                SubmitRequestError(f"Impossible to store request {request}")
            )
            return
        if not self._request_available.triggered:
            self._request_available.succeed()

    def submit_request(self, request):
        return self._env.process(self.__submit_request(request))

    @abstractmethod
    def add_server(self, *servers):
        pass

    @abstractmethod
    def route(self, request):
        pass

    def worker_loop(self):
        if not self._request_available.triggered:
            yield self._request_available

        while True:
            if self.items and len(self.items):
                request = yield self.get()
                self.route(request)
                yield self._env.timeout(1/self._admission_rate)
            else:
                del self._request_available
                self._request_available = sp.events.Event(self._env)
                yield self._request_available

    def start(self):
        self._env.process(self.worker_loop())


class LocalLoadBalancer(LoadBalancer):
    """
    This class forwards the requests to the only server it knows.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_server(self, server):
        if not isinstance(server, pyfarmsrv.Server):
            raise TypeError(f"{server} is not a Server")
        self._server = server

    def route(self, request):
        # Raises AttributeError if add_server has not been called successfully
        self._server.submit_request(request)


class SubmitRequestError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
