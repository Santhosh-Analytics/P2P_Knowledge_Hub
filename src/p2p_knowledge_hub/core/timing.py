from p2p_knowledge_hub.settings.main import get_settings
from p2p_knowledge_hub.core.logger import AppLogger

from functools import wraps
from time import perf_counter

settings = get_settings()
logger = AppLogger(settings.logs).get_logger(__name__)


def latency_decorator(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        start_time = perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = perf_counter()
            latency_ms = round(((end_time - start_time) * 1000), 2)
            logger.info(f"latency time for {func.__qualname__} is {latency_ms}")

    return wrapper_function
