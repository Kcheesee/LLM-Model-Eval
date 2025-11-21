"""
Retry logic for provider API calls with exponential backoff.
"""
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import TypeVar, Callable
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def with_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
    exponential_multiplier: int = 2
):
    """
    Decorator to add retry logic with exponential backoff to async functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds between retries
        max_wait: Maximum wait time in seconds between retries
        exponential_multiplier: Multiplier for exponential backoff
    
    Usage:
        @with_retry(max_attempts=3)
        async def call_api():
            ...
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=exponential_multiplier,
            min=min_wait,
            max=max_wait
        ),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"Retry {retry_state.attempt_number}/{max_attempts} "
            f"after {retry_state.outcome.exception()}"
        )
    )


# Specific exceptions that should trigger retries
RETRIABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    # Add provider-specific exceptions here as needed
)


def with_provider_retry(max_attempts: int = 3):
    """
    Decorator specifically for provider API calls.
    
    Only retries on specific exceptions (connection errors, timeouts).
    Does NOT retry on validation errors or auth failures.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=2, min=1, max=10),
        retry=retry_if_exception_type(RETRIABLE_EXCEPTIONS),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            f"Provider call failed, retry {retry_state.attempt_number}/{max_attempts}: "
            f"{retry_state.outcome.exception()}"
        )
    )
