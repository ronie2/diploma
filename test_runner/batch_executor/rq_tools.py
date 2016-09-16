from rq import Queue
from redis import Redis
from .jmeter_script import *

class RQWorker:
    def __init__(self):
        self.redis_conn = Redis()
        self.queue = Queue(connection=self.redis_conn)

    def enqueue_calable(self, calable, *args, **kwargs):
        return self.queue.enqueue(calable, *args, **kwargs)
