import unittest
from pyfarmsim.loadbalancer import GlobalLoadBalancer as GLL
from pyfarmsim.webrequest import WebRequest
import simpy as sp
from .config import rtEnvFastConfig
from .request_utils import MockServer, MockLoadBalancer
import random


class Test_20_GlobalLoadBalancer(unittest.TestCase):
    def setUp(self):
        self.env = sp.RealtimeEnvironment(**rtEnvFastConfig)

        self.SERVER_COUNT = 20
        self.servers = []
        for i in range(self.SERVER_COUNT):
            self.servers.append(MockServer())

    def test_05_route_config(self):
        gll = GLL(env=self.env)
        self.assertEqual(gll.route, None)

        gll.route_config("Invalid argument")
        self.assertEqual(gll.route, None)

        gll.route_config(GLL.TURNING)
        self.assertEqual(gll.route, gll.route_turning)

        gll.route_config(GLL.LEAST_LOADED)
        self.assertEqual(gll.route, gll.route_least_loaded)

        del gll

    def test_10_add_server(self):
        gll = GLL(env=self.env)

        gll.add_server(*self.servers)
        self.assertEqual(gll._server_count, self.SERVER_COUNT)
        for i in range(self.SERVER_COUNT):
            self.assertTrue(self.servers[i] in gll._server)

        # Check no duplicates are inserted
        gll.add_server(*self.servers)
        self.assertEqual(gll._server_count, self.SERVER_COUNT)
        for i in range(self.SERVER_COUNT):
            self.assertTrue(self.servers[i] in gll._server)

        del gll

    def test_15_route_turning(self):
        gll = GLL(env=self.env, route_config=GLL.TURNING)
        gll.add_server(*self.servers)
        gll.start()

        self.assertFalse(hasattr(gll, '_next_turn'))

        wr = []
        for i in range(10):
            wr.append(WebRequest(self.env))
            gll.submit_request(wr[-1])

        all_served = sp.events.AllOf(self.env, wr)
        while not all_served.triggered:
            self.env.step()

        for i in range(10):
            srv_i = i % self.SERVER_COUNT
            req_i = i // self.SERVER_COUNT
            self.assertEqual(gll._server[srv_i]._request_list[req_i], wr[i])

        del gll

    def test_20_route_least_loaded(self):
        gll = GLL(env=self.env, route_config=GLL.LEAST_LOADED)
        gll.add_server(*self.servers)
        gll.start()

        for s in self.servers:
            s._usage_manager.usage = 1

        wr = []
        index = []
        for i in range(50):
            # Define which server should be the next chosen
            index.append(random.randrange(0, self.SERVER_COUNT))
            gll._server[index[-1]]._usage_manager._usage = 0

            # Create the request we want to submit
            wr.append(WebRequest(self.env))

            gll.submit_request(wr[-1])

            while not wr[-1].triggered:
                self.env.step()

            gll._server[index[-1]]._usage_manager._usage = 1

        for i in range(50):
            self.assertTrue(wr[i] in gll._server[index[i]]._request_list)

    def test_25_route_least_queue(self):
        gll = GLL(env=self.env, route_config=GLL.LEAST_QUEUE)

        loadbalancers = [MockLoadBalancer(i) for i in range(1, 50)]

        # this will be the one will always be chosen
        least_queue_load_balancer = MockLoadBalancer(0)

        loadbalancers.append(least_queue_load_balancer)
        random.shuffle(loadbalancers)

        gll.add_server(*loadbalancers)
        gll.start()

        for i in range(50):
            wr = WebRequest(self.env)
            gll.submit_request(wr)

            while not wr.triggered:
                self.env.step()

            self.assertEqual(wr, least_queue_load_balancer._request_list[-1])
