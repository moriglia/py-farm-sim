from contextlib import contextmanager
from collections import deque


class UsageManager:
    def __init__(self, capacity, env):
        # setup capacity log
        self._capacity_changes = deque([(env.now, capacity)])
        self._exec_intervals = deque([])
        self._env = env

    @contextmanager
    def CPU_record_usage(self):
        l_ei = len(self._exec_intervals)
        self._exec_intervals.appendleft([self._env.now])
        try:
            yield
        finally:
            new_l = len(self._exec_intervals)
            assert new_l >= l_ei
            self._exec_intervals[new_l - l_ei - 1].append(self._env.now)

    def __usage_interval_constant_vm(self, start, stop, vm_count):
        if start > stop:
            raise ValueError(f"start ({start}) \
                must be smaller than stop ({stop})")
        if vm_count < 1:
            raise ValueError(f"vm_count = {vm_count}, but should be > 0")

        interval = stop - start
        exec_time = 0
        for record in self._exec_intervals:
            if record[0] > stop:
                """
                If the CPU utilization interval started after the end of the
                interval we are interested in, skip it
                """
                continue
            if len(record) > 1:
                assert type(record[1]) == float, f"record[1] type is \
                    {type(record[1])}\nrecord[1] = {record[1]}"
            if ((len(record) == 2) and (record[1] < start)):
                """
                If the CPU utilization ended before
                """
                continue
            """
            The remaining cases are those in which the computation started
            before the iterval end and finished after the interval start
            """
            stop_interval = min(stop, record[1]) if len(record) == 2 else stop
            start_interval = max(start, record[0])
            sub_interval = stop_interval - start_interval
            assert sub_interval <= interval
            exec_time += sub_interval

        usage = exec_time / (vm_count * interval)
        assert usage <= 1.0, f"Utilization = {usage}"
        return usage

    def __usage_interval(self, start, stop):

        if start > stop:
            raise ValueError(f"start ({start}) \
                must be smaller than stop ({stop})")

        usage = 0

        # get times in which the capacity has changed
        change_record_index = 0
        change_record_len = len(self._capacity_changes)
        stop_i = stop
        while change_record_index < change_record_len:
            change_record = self._capacity_changes[change_record_index]

            if change_record[0] >= stop:
                change_record_index += 1
                continue
            if change_record[0] < start:
                # we went too far into the past
                break

            start_i = change_record[0]
            num_i = change_record[1]
            usage += self.__usage_interval_constant_vm(
                start_i,
                stop_i,
                num_i
            ) * (stop_i - start_i)

            stop_i = start_i
            change_record_index += 1

        if change_record_index < change_record_len:
            # this happens wen we go too far in the past
            num_i = self._capacity_changes[change_record_index][1]
            usage += self.__usage_interval_constant_vm(
                start,
                stop_i,
                num_i
            )*(stop_i - start)

        assert usage <= (stop - start)
        return usage/(stop - start)

    def usage_since(self, since_time):
        return self.__usage_interval(since_time, self._env.now)

    def usage_last_interval(self, interval):
        t = self._env.now
        return self.__usage_interval(t - interval, t)
