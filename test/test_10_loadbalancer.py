import unittest
from pyfarmsim.loadbalancer import LoadBalancer
import simpy as sp
from .config import rtEnvFastConfig


class LoadBalancerSingleServer(LoadBalancer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._routed_elements = []

    def add_server(self, server):
        self._server = server

    def route(self, request):
        self._routed_elements.append(request)
        return (self._server, request)


class FakeRequest:
    def __init__(self, id):
        self.id = id


class Test_00_LoadBalancer(unittest.TestCase):
    def setUp(self):
        self.env = sp.RealtimeEnvironment(**rtEnvFastConfig)

    def tearDown(self):
        del self.env

    def test_loadbalancer(self):
        with self.assertRaises(TypeError):
            lb = LoadBalancer(self.env)
            del lb


class Test_05_LoadBalancerSingleServer(unittest.TestCase):
    def setUp(self):
        self.env = sp.RealtimeEnvironment(**rtEnvFastConfig)
        self.lbss = LoadBalancerSingleServer(self.env)

    def tearDown(self):
        del self.env
        del self.lbss

    def test_00_add_server(self):
        self.assertFalse(hasattr(self.lbss, '_server'))
        with self.assertRaises(AttributeError):
            self.lbss.route(5)
        self.lbss.add_server(1)
        self.assertEqual(self.lbss.route('request'), (1, 'request'))

    def test_05_amission_rate(self):
        with self.assertRaises(ValueError):
            self.lbss.admission_rate = -5

        self.lbss.admission_rate = 10
        self.assertEqual(self.lbss.admission_rate, 10)

    def test_10_worker_loop(self):
        self.assertTrue(self.lbss._request_available.triggered)

        self.lbss.add_server("server")
        self.lbss.start()

        while self.lbss._request_available.triggered:
            self.env.step()

        submissions = []
        RANGE = 10
        for i in range(RANGE):
            # create submission requests
            w = FakeRequest(i)
            submissions.append(self.lbss.submit_request(w))

        anysubmitted = sp.events.AnyOf(self.env, submissions)
        while not (anysubmitted.processed and anysubmitted.ok):
            # wait for any submission to complete
            self.env.step()

        # before completing the submission should have triggered
        # the event self._request_available
        self.assertTrue(
            self.lbss._request_available.ok
        )

        # once there is no request left in store, the worker will create
        # a new self._request_available event
        while self.lbss._request_available.triggered:
            self.env.step()

        # all submitted requests should be in the _routed_elements list
        ids = [x.id for x in self.lbss._routed_elements]
        for i in range(RANGE):
            self.assertTrue(i in ids)
