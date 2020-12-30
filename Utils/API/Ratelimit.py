from typing import Union, Iterable
from datetime import timedelta, datetime
from queue import SimpleQueue
from collections import deque
from threading import Lock
from time import sleep
from functools import wraps

DEFAULT_RATELIMIT_NAME = 'default'

# to be formatted as {name: [_Ratelimit(rule), ...]}
_ratelimits = {}


class RatelimitRule(object):
    def __init__(self, max_executions: int, interval: Union[int, timedelta], buffer_interval: Union[int, timedelta] = timedelta(milliseconds=100)):
        """
        A decorator that ratelimits the decorated function, so that it may only be executed a specified number of times in the given interval

        :param max_executions: The maximum number of calls that can be made to the decorated function in the given interval
        :param interval: The interval in which to limit the rate of execution. Can be represented as a timedelta, or an integer representing the number of milliseconds in the interval
        :param buffer_interval: An interval added to the slept time in the original, so that inaccuracies in the OS sleep timing do not cause the ratelimit to be exceeded. This is defaulted to 100 milliseconds, and can be represented as a timedelta, or an integer representing the number of milliseconds in the interval

        :return: The result of the decorated function
        """
        if isinstance(interval, int):
            interval = timedelta(seconds=interval)
        if isinstance(buffer_interval, int):
            buffer_interval = timedelta(seconds=buffer_interval)

        self.max_executions = max_executions
        self.interval = interval
        self.buffer_interval = buffer_interval

    def __str__(self):
        return f"RatelimitRule(Max Requests: {self.max_executions}, Interval: {self.interval}, Buffer Interval: {self.buffer_interval})"


def ratelimit(name: str = DEFAULT_RATELIMIT_NAME):
    """
    A decorator that ratelimits the decorated function, so that it may only be executed a specified number of times in the given interval

    :param interval: The interval in which to limit the rate of execution. Can be represented as a timedelta, or an integer representing the number of milliseconds in the interval
    :param max_executions: The maximum number of calls that can be made to the decorated function in the given interval
    :param buffer_interval: An interval added to the slept time in the original, so that inaccuracies in the OS sleep timing do not cause the ratelimit to be exceeded. This is defaulted to 100 milliseconds, and can be represented as a timedelta, or an integer representing the number of milliseconds in the interval
    :param name: The name of the desired ratelimiter. This can be used to group ratelimited functions
    :return: The result of the decorated function
    """

    def ratelimit_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _ratelimits[name].execute(func, args, kwargs)

        return wrapper

    return ratelimit_decorator


def create_ratelimit(rules: Union[RatelimitRule, Iterable[RatelimitRule]], name=DEFAULT_RATELIMIT_NAME):
    _ratelimits[name] = _Ratelimit(rules)


class _RequestTracker(object):
    def __init__(self, rule: RatelimitRule):
        self.requests = deque()
        self.rule = rule

    def clean_requests(self):
        # while tracker is not empty and the oldest request no longer matters
        while self.requests and self.requests[0] + self.rule.interval + self.rule.buffer_interval < datetime.utcnow():
            self.requests.popleft()

    def request_ratelimited_until(self) -> datetime:
        """
        Finds the UTC timestamp when the next request can be made

        :return: Timestamp when a new request may be executed, None if the request may be executed immediately
        """
        self.clean_requests()
        if len(self.requests) == self.rule.max_executions:
            return self.requests[0] + self.rule.interval + self.rule.buffer_interval
        else:
            return None

    def insert_request_timestamp(self, timestamp: datetime):
        self.requests.append(timestamp)


# An internal class designed to house API ratelimiting logic, meant for both individual and shared ratelimiting
class _Ratelimit(object):
    def __init__(self, rules: Union[RatelimitRule, Iterable[RatelimitRule]]):
        # create list of trackers for handling timestamp logic based on rules
        self.trackers = [_RequestTracker(rules)] if isinstance(rules, RatelimitRule) else [_RequestTracker(rule) for rule in rules]
        self.execution_lock = Lock()  # for limiting the requests to one at a time

    @property
    def rules(self) -> Iterable[RatelimitRule]:
        return [tracker.rule for tracker in self.trackers]

    def execute(self, func, args, kwargs):

        # handle request
        def execute_function(func, args, kwargs):

            # sleep until all trackers are valid for this ratelimiter
            for tracker in self.trackers:
                target_time = tracker.request_ratelimited_until()
                if target_time is not None:
                    wait_time = target_time - datetime.utcnow()
                    sleep(wait_time.total_seconds())

            # execute the request
            execution_timestamp = datetime.utcnow()
            result = func(*args, **kwargs)

            # add the request to the tracker
            for tracker in self.trackers:
                tracker.insert_request_timestamp(execution_timestamp)

            return result

        # lock before handling request
        self.execution_lock.acquire()
        result = execute_function(func, args, kwargs)
        self.execution_lock.release()
        return result
