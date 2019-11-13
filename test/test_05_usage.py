import unittest
from pyfarmsim.server import Server
from pyfarmsim.utils import DebugPrint
import simpy as sp
import random
import time
from .request_utils import incoming_request, usage_ask, capacity_setter


debug = DebugPrint()


class UsageTest(unittest.TestCase):
    def setUp(self):
        DebugPrint.DEBUG = True
        self.e = sp.RealtimeEnvironment(factor=0.1, strict=False)
        self.s = Server(self.e, 4, 10, "Corborant")
        self.e.process(usage_ask(self.e, self.s, 50, 0.5))
        self.e.process(capacity_setter(self.e, self.s))

    def tearDown(self):
        DebugPrint.DEBUG = False
        del self.s
        del self.e

    def generate_requests(self):
        REQUEST_RATE = 3
        proc_time = 0.8
        for i in range(100):
            yield self.e.timeout(random.expovariate(REQUEST_RATE))
            self.e.process(incoming_request(i, self.e, self.s, proc_time))
            debug(f"Created process with ID: {i} \
                and processing time {proc_time} units")

    def test(self):
        self.e.process(self.generate_requests())
        self.e.run()


if __name__ == "__main__":
    random.seed(time.time())
    unittest.main()
