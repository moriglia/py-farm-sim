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

    The route() function, as well as the add_server() functions are not defined
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

    @property
    def queue_length(self):
        if self.items:
            return len(self.items)

        return 0

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


class GlobalLoadBalancer(LoadBalancer):
    TURNING = 0
    LEAST_LOADED = 1
    LEAST_QUEUE = 2

    def __init__(self, route_config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.route_config(route_config)
        self._usage_interval = 0.5

    @property
    def usage_interval(self):
        return self._usage_interval

    @usage_interval.setter
    def usage_interval(self, interval):
        if not isinstance(interval, float):
            # If interval is neither a string representation of a number
            # nor a number, this will raise TypeError
            interval = float(interval)

        if interval <= 0:
            raise ValueError(f"interval parameter must be positive, \
                but got {interval}")

        self._usage_interval = interval

    def add_server(self, *servers):
        """
        Note: the _server name may be misleading. The _server list can either
        include Server instances or LoadBalancer instances. They must be
        omogeneous anyway, for they are treated in either way according to
        the route function that will be selected.

        It is up to the user to use this properly.
        """
        if hasattr(self, '_server'):
            # Add new servers without diplicates
            self._server = list(set([*self._server, *servers]))
        else:
            self._server = [*servers]

        self._server_count = len(self._server)

    def route(self, request):
        """
        This function must be implemented even though its implementation
        will be replaced according to the route_config() function
        """
        pass

    def route_turning(self, request):
        """
        Forward the request to the next server in turn among the _server list.

        Note: this works regardless of the _server items being servers or
        local load balancers
        """
        if not hasattr(self, '_next_turn'):
            self._next_turn = 0

        # Submit request to next in turn
        p = self._server[self._next_turn].submit_request(request)

        # Advance next index
        self._next_turn += 1
        self._next_turn %= self._server_count

        return p

    def route_least_loaded(self, request):
        """
        Forward the request to the server with the minimum CPU utilization
        among those that were added to the list.

        Note: the _server list must contain only servers
        """
        # 2 will be certainly greater than the CPU utilization of any server
        least_u = 2
        candidate = -1

        # Select the server with the least CPU utilization
        for i in range(self._server_count):
            current_u = self._server[i]._usage_manager.usage_last_interval(
                self._usage_interval
            )
            if current_u < least_u:
                # This condition will at least happen once for current_u < 1
                # by definition of CPU utilization
                least_u = current_u
                candidate = i

        return self._server[candidate].submit_request(request)

    def route_least_queue(self, request):
        """
        Forward the request to the Load Balancer with the least queue length
        """
        # Any queue is shorter than infinite
        least_queue = float('inf')
        candidate = -1

        # Find the Load Balancer with the least queue length
        for i in range(self._server_count):
            current_queue = self._server[i].queue_length
            if current_queue < least_queue:
                least_queue = current_queue
                candidate = i

        self._server[candidate].submit_request(request)

    def route_config(self, rc):
        """
        Select the forwarding function amng those available
        """
        if rc == self.__class__.TURNING:
            self.route = self.route_turning
        elif rc == self.__class__.LEAST_LOADED:
            self.route = self.route_least_loaded
        elif rc == self.__class__.LEAST_QUEUE:
            self.route = self.route_least_queue
        else:
            self.route = None


class SubmitRequestError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
