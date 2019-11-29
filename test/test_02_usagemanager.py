import unittest
from pyfarmsim.usagemanager import UsageManager as UM
from pyfarmsim.utils import DebugPrint
import simpy as sp
from collections import deque
from .config import rtEnvFastConfig


debug = DebugPrint()


class Test_10_UsageManager(unittest.TestCase):
    def setUp(self):
        self.env = sp.RealtimeEnvironment(**rtEnvFastConfig)
        pass

    def test_10_CPU_record_usage(self):
        um = UM(4, self.env)

        def wait_for_timeout(env, t):
            yield env.timeout(t)

        # DebugPrint.DEBUG = True
        for i in range(100):
            p = self.env.process(wait_for_timeout(self.env, i/10))
            with um.CPU_record_usage(i):
                self.env.run(until=p)

            last_exec_interval = um._exec_intervals[0]
            self.assertAlmostEqual(
                last_exec_interval[1] - last_exec_interval[0],
                i/10
            )
            self.assertEqual(last_exec_interval[2], i)
            debug(i/10, last_exec_interval)
        # DebugPrint.DEBUG = False
        del um

    def test_20__usage_interval_constant_vm(self):
        um = UM(4, self.env)

        # non overlapping intervals
        um._exec_intervals = deque(
            [
                [1.0, 2.0],
                [3.0, 4.0]
            ]
        )
        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(1.0, 2.0, 4),
            (2.0 - 1.0) / (2.0 - 1.0) / 4
        )
        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(0.0, 2.0, 4),
            (2.0 - 1.0) / (2.0 - 0.0) / 4
        )
        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(0.0, 4.0, 4),
            (2.0 - 1.0 + 4.0 - 3.0) / (4.0 - 0.0) / 4
        )
        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(1.0, 4.0, 4),
            (2.0 - 1.0 + 4.0 - 3.0) / (4.0 - 1.0) / 4
        )

        # overlapping intervals
        um._exec_intervals = deque(
            [
                [1.0, 2.0],
                [1.5, 4.0]
            ]
        )

        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(1.0, 2.0, 4),
            (2.0 - 1.0 + 2.0 - 1.5) / (2.0 - 1.0) / 4
        )
        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(0.0, 2.0, 4),
            (2.0 - 1.0 + 2.0 - 1.5) / (2.0 - 0.0) / 4
        )
        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(0.0, 4.0, 4),
            (2.0 - 1.0 + 4.0 - 1.5) / (4.0 - 0.0) / 4
        )
        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(1.7, 4.0, 4),
            (2.0 - 1.7 + 4.0 - 1.7) / (4.0 - 1.7) / 4
        )

        self.assertEqual(
            um._UsageManager__usage_interval_constant_vm(2.5, 3.5, 4),
            (3.5 - 2.5) / (3.5 - 2.5) / 4
        )

        del um

    def test_30_test_usage_interval(self):
        um = UM(2, self.env)
        um._exec_intervals = deque(
            [
                [1.0, 2.0],
                [1.5, 4.0],
                [2.5, 4.5],
                [3.5, 5.0]
            ]
        )

        um._capacity_changes = deque(
            [
                (4.0, 4),
                (3.0, 3),
                (0.0, 2)
            ]
        )

        self.assertEqual(
            um._UsageManager__usage_interval(0.0, 2.0),
            (2.0 - 1.0 + 2.0 - 1.5) / (2.0 - 0.0) / 2
        )
        self.assertEqual(
            um._UsageManager__usage_interval(2.0, 4.0),
            ((3.0 - 2.0 + 3.0 - 2.5) / 2 +
                (4.0 - 3.0 + 4.0 - 3.0 + 4.0 - 3.5) / 3) / (4.0 - 2.0)
        )
        self.assertEqual(
            um._UsageManager__usage_interval(3.5, 5.0),
            ((4.0 - 3.5 + 4.0 - 3.5 + 4.0 - 3.5) / 3 +
                (4.5 - 4.0 + 5.0 - 4.0) / 4) / (5.0 - 3.5)
        )
