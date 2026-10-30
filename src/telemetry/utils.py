"""General utilities including execution timing decorators."""

import functools
import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def timed(func: F) -> F:
    """Decorator to log function execution duration in milliseconds."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info("%s took %.2f ms", func.__name__, elapsed_ms)

    return wrapper  # type: ignore[return-value]