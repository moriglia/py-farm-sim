import unittest
from pyfarmsim.server import Server, FullQueue
from pyfarmsim.webrequest import WebRequest
import simpy as sp
import random
from pyfarmsim.utils import t
import time


def usage_ask(env, s):
    for i in range(20):
        yield env.timeout(0.2)
        u = s._usage_manager.usage_last_interval(0.5)
        print(f"[T: {t()}] {s} CPU utilization: {u*100}%, sample {i} ")


def incoming_request(idn, env, server, processing_time):
    yield env.timeout(processing_time)  # wait a bit before making request
    wr = WebRequest(env, processing_time, None)
    try:
        print(f"[T: {t()}] Sending REQ {wr.id} to {server.name}")
        server.request(wr)
        err = yield wr.wait_for_completion()
        if err == 0:
            print(f"[T: {t()}] REQ {wr.id} successful")
        else:
            raise err
    except FullQueue as fq:
        print(f"[T: {t()}] REQ {wr.id} rejected: {fq}")

    return


def capacity_setter(env, server):
    for i in range(5):
        yield env.timeout(0.5)
        print(f"[T: {t()}] Updating capacity: {server}")
        server.set_capacity(5+i)
        print(f"[T: {t()}] Updated  capacity: {server}")

    for i in range(5):
        yield env.timeout(0.5)
        print(f"[T: {t()}] Updating capacity {server}")
        server.set_capacity(10-i)
        print(f"[T: {t()}] Updated  capacity {server}")


class UsageTest(unittest.TestCase):
    def setUp(self):
        self.e = sp.RealtimeEnvironment()
        self.s = Server(self.e, 4, 10, "Corborant")
        self.e.process(usage_ask(self.e, self.s))
        self.e.process(capacity_setter(self.e, self.s))
        for i in range(100):
            proc_time = random.expovariate(1.5) + 0.5
            self.e.process(incoming_request(i, self.e, self.s, proc_time))
            print(f"Created process with ID: {i} \
                and processing time {proc_time} units")

    def test(self):
        self.e.run()


if __name__ == "__main__":
    random.seed(time.time())
    unittest.main()
