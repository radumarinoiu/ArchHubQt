"""Performance utilities: timing decorators and helpers."""

import functools
import logging
import time

logger = logging.getLogger(__name__)


def log_duration(name: str | None = None):
    """Decorator that logs how long the function took to run.

    Args:
        name: Optional label for the log message. Defaults to the function's qualname.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            label = name or getattr(func, "__qualname__", func.__name__)
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                logger.info("%s took %.3f s", label, elapsed)

        return wrapper

    return decorator
