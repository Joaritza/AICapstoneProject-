"""Retry logic and exponential backoff implementation."""

import time
import logging
from typing import TypeVar, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator for retry logic with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function with retry logic

    Example:
        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        def api_call():
            return requests.get(url)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = base_delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )

            # If we got here, all retries failed
            raise last_exception

        return wrapper

    return decorator


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
) -> float:
    """
    Calculate exponential backoff delay.

    Args:
        attempt: Current attempt number (1-indexed)
        base_delay: Initial delay in seconds
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay to return

    Returns:
        Delay in seconds

    Example:
        delay = exponential_backoff(attempt=2)  # Returns 2.0 seconds
    """
    delay = base_delay * (backoff_factor ** (attempt - 1))
    return min(delay, max_delay)
