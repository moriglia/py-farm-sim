import unittest
from pyfarmsim.server import Server, FullQueue
from pyfarmsim.webrequest import WebRequest
import simpy as sp
from .config import rtEnvFastConfig


class Test_10_Server(unittest.TestCase):
    def setUp(self):
        self.e = sp.RealtimeEnvironment(**rtEnvFastConfig)
        self.s = Server(env=self.e, capacity=2, length=3, name="TestServer")

    def tearDown(self):
        del self.e
        del self.s

    def test_10_submit_request(self):
        wr = []
        procs = []
        for i in range(5):
            wr.append(WebRequest(self.e, 5))
            procs.append(self.s.submit_request(wr[i]))

        wr_expected_fail = WebRequest(self.e, 1)
        self.s.submit_request(wr_expected_fail)
        while not wr_expected_fail.triggered:
            self.e.step()

        self.assertTrue(isinstance(wr_expected_fail.value, FullQueue))
        wr_expected_fail.defused = True

        allreqs = sp.events.AllOf(self.e, wr)
        while not allreqs.processed:
            self.e.step()

    def test_20_set_capacity(self):
        self.s.set_capacity(3)
        self.assertEqual(self.s._capacity_changes[0][1], 3, msg=f"\
            Capacity changes: {self.s._capacity_changes}")

        wr = []
        for i in range(3):
            wr.append(WebRequest(self.e, 2))
            self.s.submit_request(wr[-1])

        while not wr[0].triggered:
            self.e.step()

        self.s.set_capacity(1)

        # Since 2 other requests are keeping the VMs busy
        # the capacity changes records that the capacity has goes down to 2
        self.assertEqual(self.s._capacity_changes[0][1], 2)
        self.assertEqual(self.s._capacity, 1)

        while not wr[1].triggered:
            self.e.step()

        # Now capacity should have been logged to be 1
        self.assertEqual(self.s._capacity_changes[0][1], 1)

        # There should be one more request to be served
        self.assertFalse(wr[2].triggered)

        self.s.set_capacity(5)
        self.assertEqual(self.s._capacity_changes[0][1], 5)

        wr = [wr[2]]  # Re create webrequest list

        for i in range(7):
            wr.append(WebRequest(self.e, 2))
            self.s.submit_request(wr[-1])
            self.e.step()  # Needed to put the requests in queue

        self.s.set_capacity(2)
        self.assertNotEqual(self.s._capacity_changes[0][1], 2)
        for i in range(3):
            while not wr[i].triggered:
                self.e.step()
            self.assertEqual(self.s._capacity_changes[0][1], 5-i-1)

        self.e.run()  # Serve all remaining requests
