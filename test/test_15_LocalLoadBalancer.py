import unittest
from pyfarmsim.server import Server
from pyfarmsim.loadbalancer import LocalLoadBalancer
from pyfarmsim.webrequest import WebRequest
import simpy as sp
from .config import rtEnvFastConfig
from .request_utils import MockServer


class Test_10_LocalLoadBalancer(unittest.TestCase):
    def setUp(self):
        self.env = sp.RealtimeEnvironment(**rtEnvFastConfig)
        self.llb = LocalLoadBalancer(self.env)

    def tearDown(self):
        del self.llb
        del self.env

    def test_10_add_server(self):
        self.assertFalse(hasattr(self.llb, '_server'))
        with self.assertRaises(TypeError):
            self.llb.add_server(5)

        srv = Server(self.env, 5, 100)
        self.llb.add_server(srv)
        self.assertEqual(self.llb._server, srv)
        with self.assertRaises(TypeError):
            self.llb.add_server(MockServer())

    def test_15_route(self):
        mockserver = MockServer()
        self.llb._server = mockserver  # Bypass the type check on server
        self.llb.start()

        for i in range(50):
            wr = WebRequest(self.env)
            p = self.llb.submit_request(wr)

            while not (p.triggered and p.processed):
                self.env.step()

            self.assertFalse(wr.triggered)

            while not wr.triggered:
                self.env.step()

            self.assertEqual(wr, mockserver._request_list[-1])

    def test_20_usage_last_interval(self):
        self.assertEqual(self.llb.count, 1)
        ms = MockServer()
        ms._usage = 0.94
        self.llb._server = ms

        self.assertEqual(self.llb.usage_last_interval(0.2), 0.94)
