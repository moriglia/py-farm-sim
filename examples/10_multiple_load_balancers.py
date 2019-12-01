from context import pyfarmsim
from pyfarmsim.server import Server, FullQueue
from pyfarmsim.loadbalancer import GlobalLoadBalancer, LocalLoadBalancer
from pyfarmsim.webrequest import WebRequest
import simpy as sp
import random
from savecsv import savecsv
from functools import partial

random.seed(object())

env = sp.RealtimeEnvironment(strict=False, factor=0.2)

# Create a Global Load Balancer
gll = GlobalLoadBalancer(env, route_config=GlobalLoadBalancer.TURNING)
gll.admission_rate = 50

# Create Local Load Balancers and Servers
llbs = []
srvs = []
for x in range(4):
    llbs.append(LocalLoadBalancer(env, autostart=True))
    llbs[-1].admission_rate = 10
    srvs.append(Server(env, capacity=2, length=50))
    llbs[-1].add_server(srvs[-1])

# Add the local load balancers to the list of VPMs the global loadbalancer
# can forward requests to
gll.add_server(*llbs)

for i in range(4):
    assert gll._server[i] is llbs[i]


def callback(event, env, timeout_list, fullqueue_list):
    # If the event did not succeed defuse the exception
    if not event.ok:
        event.defused = True

        # If the failed event was a webrequest, log whether the reason
        # for the failure was the queues were full or the request timed out
        if isinstance(event, WebRequest):
            if isinstance(event.value, FullQueue):
                log_list = fullqueue_list
            else:
                log_list = timeout_list
            log_list.append((env.now, len(log_list) + 1))
    return


def waiter_process(request):
    complete = request.wait_for_completion()
    complete.callbacks = [callback]
    try:
        yield complete
    except Exception as e:
        return

    # If the complete event succeded could be because of a timeout:
    # if request event is not triggered, it means it timed out
    if not request.triggered:
        exc = Exception("Timeout")
        request.fail(exc)
    return


def request_generator(env,
                      cloud_access, rate, count, requests,
                      mu=0.8, sigma=0.2):

    # Get a reference of the generated request list
    requests = WebRequest.request_list

    for i in range(count):
        # Define inter request interval
        interval = random.expovariate(rate)

        # define how long it will take a server to serve the request
        service_time = random.gauss(mu, sigma)
        if service_time < 0:
            service_time = 0

        # Generate request
        WebRequest(env=env, time=service_time, timeout=5.0)

        # Set request callback
        requests[-1].callbacks = [callback]

        # Wait for the proper time to send the request
        yield env.timeout(interval)

        # Send the request to the cloud access host
        cloud_access.submit_request(requests[-1])

        # Start a handler for request timeouts
        env.process(waiter_process(requests[-1]))


timeouts = [("Time", "Total Timeouts")]
fullqueues = [("Time", "Total FullQueue Exceptions")]
callback = partial(
    callback,
    env=env, timeout_list=timeouts, fullqueue_list=fullqueues
)

RATE = 15
NUM = 1000
requests = []
env.process(request_generator(env, gll, RATE, NUM, requests))
gll.start()
env.run()

for i in range(4):
    savecsv([("Time", f"Server {i}"), *srvs[i].queue_log],
            f"10_multiple_lb_srv{i}.csv")

savecsv(timeouts, f"10_multiple_lb_wr_timeouts.csv")
savecsv(fullqueues, f"10_multiple_lb_wr_fullqueues.csv")
