from typing import Union
from datetime import timedelta, datetime
from queue import SimpleQueue
from threading import Lock
from time import sleep

_ratelimits = {}
DEFAULT_RATELIMIT_NAME = 'default'


# An internal class designed to house API ratelimiting logic, meant for both individual and shared ratelimiting
class _Ratelimit(object):
    def __init__(self, interval: Union[int, timedelta], max_executions: int, buffer_interval: Union[int, timedelta] = timedelta(milliseconds=100)):

        if isinstance(interval, int):
            interval = timedelta(milliseconds=interval)

        if isinstance(buffer_interval, int):
            buffer_interval = timedelta(milliseconds=buffer_interval)

        self.interval = interval
        self.buffer_interval = buffer_interval
        self.max_executions = max_executions
        self.previous_requests = SimpleQueue()
        self.oldest_request = None
        self.locks = {}

    def execute(self, func, args, kwargs):

        def execute_function(func, args, kwargs):

            if self.oldest_request is None:
                self.oldest_request = datetime.utcnow()
            elif self.previous_requests.qsize() < self.max_executions - 1:
                # if there is space for another request in the allotted timeframe
                self.previous_requests.put(datetime.utcnow())
            else:
                # if there is no space, wait until space is available
                current_timestamp = datetime.utcnow()
                # wait an extra amount of time specified in buffer interval
                target_time = self.oldest_request + self.interval + self.buffer_interval
                sleep_interval = target_time - current_timestamp
                sleep(sleep_interval.total_seconds())

                # add function execution time to queue
                self.previous_requests.put(datetime.utcnow())

            return func(*args, **kwargs)

        lock = self.get_lock(execute_function.__name__)
        lock.acquire()
        self.update_requests()
        result = execute_function(func, args, kwargs)
        lock.release()
        return result

    def update_requests(self):
        while self.oldest_request is not None and self.oldest_request + self.interval < datetime.utcnow():
            if self.previous_requests.empty():
                self.oldest_request = None
            else:
                self.oldest_request = self.previous_requests.get()

    def get_lock(self, name):
        try:
            return self.locks[name]
        except KeyError:
            lock = Lock()
            self.locks[name] = lock
            return lock


def get_ratelimiter(interval: Union[int, timedelta], max_executions: int, buffer_interval: Union[int, timedelta] = timedelta(milliseconds=100), name: str = DEFAULT_RATELIMIT_NAME):
    try:
        ratelimiter = _ratelimits[name]
    except KeyError:
        ratelimiter = _Ratelimit(interval=interval, max_executions=max_executions, buffer_interval=buffer_interval)
        _ratelimits[name] = ratelimiter
    return ratelimiter
