import simpy as sp
from utils import t


class FullQueue(Exception):
    def __init__(self, message):
        super().__init__(message)

class Server(sp.resources.resource.Resource):
    """
    This class has been created to model a Virtualized Physical Machine.
    The capacity represents the number of Virtual Machines.
    """
    def __init__(self, nv=None, capacity=4, length=10, name=None):
        # Set environment and capacity
        e = env if env else sp.Environment()
        super().__init__(e, capacity)

        # define a maximum length
        self._queue_len_max = length

        self._name = name

    def __str__(self):
        return f"{self.name} usage: {self.count}/{self.capacity}VMs {self.queue_len}/{self._queue_len_max}"
    
    def set_capacity(self, new_capacity):
        """
        Tune the number of VMs
        """
        old_capacity = self._capacity
        self._capacity = new_capacity
        if old_capacity > new_capacity:
            # The VM number has shrinked 
            # Nothing to do ? Hope so...
            pass
        else:
            """
            If we increased the number of VMs, we must check the queue
            This function iterates over the queue and allocates the 
            available VMs to the first requests in queue
            """
            self._trigger_put(None)
        
        return


    @property
    def name(self):
        return self._name
    
    @property
    def queue_len(self):
        return len(self.queue)
    
    def __request_process(self, idn, processing_time):
        """
        The Request class has infinite queue. But real web servers have a finite queue.
        In this generator I implemented the limitedness of the queue
        """
        if (self.queue_len < self._queue_len_max):
            with super().request() as req:
                print(f"[T: {t()}] {self}, alloc VM to {idn}.")
                yield req
                print(f"[T: {t()}] {self}, alloc VM OK {idn} for {processing_time}.")
                yield env.timeout(processing_time)
            print(f"[T: {t()}] {self}, freed VM fr {idn}.")
        else:
            raise FullQueue(f"Server queue reached the maximum. {self}")

        return
    
    def request(self, idn, processing_time):
        """
        This function creates the event of "acquired VM" and returns it.
        The caller can yield the returned event to sleep and to be woken up 
        once the top of the queue is reached
        """
        return self._env.process(self.__request_process(idn, processing_time))


if __name__=="__main__":
    import numpy as np
    import random
    import time
    random.seed(time.time())
    
    env = sp.RealtimeEnvironment()

    # creating a server of capacity 4 and queue length 10
    s = Server(env, 4, 10, "Sautron")

    def incoming_request(idn,env, server, processing_time):
        yield env.timeout(processing_time)# wait a bit before making request 

        try:
            print(f"[T: {t()}] Sending REQ {idn} to {server.name}")
            yield server.request(idn, processing_time)
            print(f"[T: {t()}] REQ {idn} successful")
        except FullQueue as fq:
            print(f"[T: {t()}] REQ {idn} rejected: {fq}")
        
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

    env.process(capacity_setter(env,s))


    for i in range(100):
        proc_time = random.expovariate(1.5) + 0.5
        env.process(incoming_request(i, env, s, proc_time))
        print(f"Created process with ID: {i} and processing time {proc_time} units") 

    env.run()

