import unittest
from pyfarmsim.server import Server
from pyfarmsim.webrequest import WebRequest
from pyfarmsim.utils import DebugPrint
import simpy as sp
from .config import rtEnvFastConfig


debug = DebugPrint()


@unittest.skip("Test case is not controllable at an acceptable detail level")
class Test_10_Server(unittest.TestCase):
    def setUp(self):
        self.e = sp.RealtimeEnvironment(**rtEnvFastConfig)
        self.s = Server(env=self.e, capacity=2, length=20, name="TestServer")

    def tearDown(self):
        del self.e
        del self.s

    def test_10_queue_monitor(self):
        wr = []
        REQ_COUNT = 20
        for i in range(REQ_COUNT):
            wr.append(WebRequest(self.e, 0.5))
            self.s.submit_request(wr[-1])

        allserved = sp.events.AllOf(self.e, wr)

        while not allserved.triggered:
            self.e.step()

        for i in range(REQ_COUNT - 2):
            self.assertEqual(self.s._queue_log[i][1], i + 1)
