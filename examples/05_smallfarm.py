from context import pyfarmsim
from pyfarmsim.server import Server
from pyfarmsim.loadbalancer import GlobalLoadBalancer
from pyfarmsim.webrequest import WebRequest
import simpy as sp
import random

random.seed(object())

env = sp.RealtimeEnvironment(factor=0.1, strict=False)

server_sautron = Server(env=env, capacity=2, length=100, name="Sautron")
server_tenibres = Server(env=env, capacity=3, length=100, name="Tenibres")

gll = GlobalLoadBalancer(
    route_config=GlobalLoadBalancer.TURNING,
    env=env,
    autostart=True
)

gll.add_server(server_sautron, server_tenibres)

def request_generator(env, cloud_access, rate, number):
    for i in range(number):
        interval = random.expovariate(rate)
        wr = WebRequest(env, time=0.5, timeout=1)
        cloud_access.submit_request(wr)
        yield env.timeout(interval)

REQUEST_PER_SECOND = 4
REQUEST_NUMBER = 150
env.process(request_generator(env, gll, REQUEST_PER_SECOND, REQUEST_NUMBER))

env.run()
