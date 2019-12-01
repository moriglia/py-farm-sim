from context import pyfarmsim
from pyfarmsim.server import Server
from pyfarmsim.loadbalancer import GlobalLoadBalancer
from pyfarmsim.webrequest import WebRequest
import simpy as sp
import random
from savecsv import savecsv

random.seed(object())

env = sp.RealtimeEnvironment(factor=0.1, strict=False)

# Create 2 servers
server_sautron = Server(env=env, capacity=2, length=100, name="Sautron")
server_tenibres = Server(env=env, capacity=3, length=100, name="Tenibres")

# Create a load balancer
gll = GlobalLoadBalancer(
    route_config=GlobalLoadBalancer.TURNING,
    env=env,
    autostart=True
)

gll.add_server(server_sautron, server_tenibres)
gll.admission_rate = 5


def request_generator(env, cloud_access, rate, number):
    for i in range(number):
        # Get inter request time interval
        interval = random.expovariate(rate)

        # Generate a request
        wr = WebRequest(env, time=0.5, timeout=1)

        # Submit request to cloud access host
        cloud_access.submit_request(wr)
        yield env.timeout(interval)


REQUEST_PER_SECOND = 125
REQUEST_NUMBER = 1000
env.process(request_generator(env, gll, REQUEST_PER_SECOND, REQUEST_NUMBER))

# Run simulation
env.run()

# Extract and save statistics
sautron_usage = server_sautron.usage_samples(interval=0.25)
tenibres_usage = server_tenibres.usage_samples(interval=0.25)

savecsv([('Time','Sautron usage'), *sautron_usage],
        '05_smallfarm_sautron_usage.csv')
savecsv([('Time','Tenibres usage'), *tenibres_usage],
        '05_smallfarm_tenibres_usage.csv')

savecsv([('Time','Sautron queue'), *server_sautron.queue_log],
        '05_smallfarm_sautron_queue.csv')
savecsv([('Time','Tenibres queue'), *server_tenibres.queue_log],
        '05_smallfarm_tenibres_queue.csv')
