from context import pyfarmsim
from pyfarmsim.server import Server
from pyfarmsim.loadbalancer import GlobalLoadBalancer
from pyfarmsim.webrequest import WebRequest
import simpy as sp
import random
import csv

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
gll.admission_rate = 5


def request_generator(env, cloud_access, rate, number):
    for i in range(number):
        interval = random.expovariate(rate)
        wr = WebRequest(env, time=0.5, timeout=1)
        cloud_access.submit_request(wr)
        yield env.timeout(interval)


REQUEST_PER_SECOND = 125
REQUEST_NUMBER = 1000
env.process(request_generator(env, gll, REQUEST_PER_SECOND, REQUEST_NUMBER))

env.run()

sautron_usage = server_sautron.usage_samples(interval=0.25)
tenibres_usage = server_tenibres.usage_samples(interval=0.25)

with open('05_smallfarm_sautron_usage.csv', 'w') as usage_file:
    usage_writer = csv.writer(usage_file)
    usage_writer.writerow(['Time','Sautron usage'])
    usage_writer.writerows(sautron_usage)

with open('05_smallfarm_tenibres_usage.csv', 'w') as usage_file:
    usage_writer = csv.writer(usage_file)
    usage_writer.writerow(['Time','Tenibres usage'])
    usage_writer.writerows(tenibres_usage)
