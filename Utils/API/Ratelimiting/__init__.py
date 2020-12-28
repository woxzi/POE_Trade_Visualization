from typing import Union
from datetime import timedelta
from functools import wraps
from Utils.API.Ratelimiting.Ratelimit import get_ratelimiter, DEFAULT_RATELIMIT_NAME


def ratelimit(interval: Union[int, timedelta], max_executions: int, buffer_interval: Union[int, timedelta] = timedelta(milliseconds=100), name: str = DEFAULT_RATELIMIT_NAME):
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
            ratelimiter = get_ratelimiter(interval=interval, max_executions=max_executions, buffer_interval=buffer_interval, name=name)
            return ratelimiter.execute(func, args, kwargs)

        return wrapper

    return ratelimit_decorator
