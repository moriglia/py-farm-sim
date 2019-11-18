import unittest
import time
from pyfarmsim.usagemanager import UsageManager as UM
from collections import deque


class Test_10_UsageManager(unittest.TestCase):
    def setUp(self):
        pass

    def test_10_CPU_record_usage(self):
        um = UM(4)
        for i in range(5):
            with um.CPU_record_usage():
                time.sleep(0.5)

            last_exec_interval = um._exec_intervals[-1]
            self.assertGreaterEqual(
                last_exec_interval[1] - last_exec_interval[0],
                0.5
            )
        del um

    def test_20__usage_interval_constant_vm(self):
        um = UM(4)

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
        um = UM(2)
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
