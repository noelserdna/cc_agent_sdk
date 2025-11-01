"""
Retry logic with exponential backoff using tenacity.

This module provides configurable retry decorators for Claude API calls
with exponential backoff, timeout enforcement, and structured logging.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from anthropic import APIError as AnthropicAPIError
from anthropic import APIStatusError
from anthropic import RateLimitError as AnthropicRateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_chain,
    wait_fixed,
)

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Type variable for generic function return types
T = TypeVar("T")


class APIError(Exception):
    """
    Base exception for API errors.

    Attributes:
        status_code: HTTP status code (optional)
        retry_after: Retry-After header value in seconds (optional)
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        retry_after: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


class RateLimitError(APIError):
    """
    Exception raised when API rate limit is exceeded.

    Attributes:
        status_code: HTTP status code (typically 429)
        retry_after: Retry-After header value in seconds (optional)
    """

    pass


class ServiceUnavailableError(APIError):
    """
    Exception raised when a service is temporarily unavailable.

    This is used to signal that a retry should be attempted for
    transient failures like rate limits or temporary API outages.

    Attributes:
        status_code: HTTP status code (typically 503)
        retry_after: Retry-After header value in seconds (optional)
    """

    pass


def should_retry_exception(exception: Exception) -> bool:
    """
    Determine if an exception should trigger a retry.

    Args:
        exception: The exception to evaluate

    Returns:
        bool: True if the exception is retryable, False otherwise
    """
    # Retryable exceptions (both our custom and anthropic's)
    retryable_types = (
        APIError,
        AnthropicAPIError,
        APIStatusError,
        RateLimitError,
        AnthropicRateLimitError,
        ServiceUnavailableError,
    )

    return isinstance(exception, retryable_types)


def create_retry_decorator(
    max_attempts: int | None = None,
    max_total_seconds: int | None = None,
    delays: list[float] | None = None,
    callback: Callable[[Any], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Create a retry decorator with custom configuration.

    Args:
        max_attempts: Maximum number of retry attempts (default from settings)
        max_total_seconds: Maximum total time for retries (default from settings)
        delays: List of delays between retries in seconds (default from settings)
        callback: Optional callback function called on each retry attempt

    Returns:
        Callable: Retry decorator configured with specified parameters
    """
    # Use settings defaults if not provided
    max_attempts = max_attempts or settings.retry_max_attempts
    max_total_seconds = max_total_seconds or settings.retry_max_total_seconds
    delays = delays or settings.retry_delays_list

    # Create wait strategy with explicit delays
    # Example: [1, 2, 4] → wait 1s, then 2s, then 4s
    wait_strategies = [wait_fixed(delay) for delay in delays]

    # Add a final wait strategy for any attempts beyond the explicit delays
    if len(wait_strategies) < max_attempts:
        # Continue with the last delay for remaining attempts
        final_delay = delays[-1] if delays else 1.0
        wait_strategies.append(wait_fixed(final_delay))

    wait_strategy = wait_chain(*wait_strategies)

    def before_sleep_log(retry_state: Any) -> None:
        """Log retry attempts with context."""
        attempt = retry_state.attempt_number
        exception = retry_state.outcome.exception()

        logger.warning(
            "Retrying API call",
            attempt=attempt,
            max_attempts=max_attempts,
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            next_wait_seconds=retry_state.next_action.sleep if retry_state.next_action else 0,
        )

        # Call custom callback if provided
        if callback:
            callback(retry_state)

    # Create retry decorator
    return retry(
        # Stop conditions: either max attempts OR max total time
        stop=(stop_after_attempt(max_attempts) | stop_after_delay(max_total_seconds)),
        # Wait strategy with explicit delays
        wait=wait_strategy,
        # Only retry on specific API exceptions (both custom and anthropic)
        retry=retry_if_exception_type(
            (
                APIError,
                AnthropicAPIError,
                APIStatusError,
                RateLimitError,
                AnthropicRateLimitError,
                ServiceUnavailableError,
            )
        ),
        # Logging callbacks
        before_sleep=before_sleep_log,
        # No retry_error_callback: tenacity will raise RetryError when all attempts exhausted
    )


# Default retry decorator for Claude API calls
claude_api_retry = create_retry_decorator()


def with_retry(
    func: Callable[..., T] | None = None,
    *,
    max_attempts: int | None = None,
    max_total_seconds: int | None = None,
    delays: list[float] | None = None,
    callback: Callable[[Any], None] | None = None,
) -> Callable[..., T] | Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator factory for adding retry logic to async functions.

    This is a convenience wrapper around create_retry_decorator that can be
    used directly as a decorator with optional parameters.

    Can be used with or without parameters:
        @with_retry
        async def func1(): ...

        @with_retry(max_attempts=5)
        async def func2(): ...

    Args:
        func: Function to decorate (when used without parameters)
        max_attempts: Maximum number of retry attempts
        max_total_seconds: Maximum total time for retries
        delays: List of delays between retries in seconds
        callback: Optional callback function called on each retry attempt

    Returns:
        Callable: Decorated function or decorator

    Example:
        @with_retry(max_attempts=5, delays=[1, 2, 4, 8])
        async def call_claude_api():
            ...
    """

    def decorator_wrapper(fn: Callable[..., T]) -> Callable[..., T]:
        decorator = create_retry_decorator(
            max_attempts=max_attempts,
            max_total_seconds=max_total_seconds,
            delays=delays,
            callback=callback,
        )

        # Apply decorator once to the function
        return decorator(fn)

    # Support both @with_retry and @with_retry()
    if func is not None:
        # Used without parentheses: @with_retry
        return decorator_wrapper(func)
    else:
        # Used with parentheses: @with_retry(...)
        return decorator_wrapper


# Example usage for testing
if __name__ == "__main__":
    import asyncio

    from anthropic import AsyncAnthropic

    @with_retry(max_attempts=3, delays=[1, 2, 4])
    async def test_claude_call() -> str:
        """Test function that calls Claude API with retry logic."""
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)

        message = await client.messages.create(
            model=settings.claude_model,
            max_tokens=100,
            messages=[{"role": "user", "content": "Say hello"}],
        )

        return message.content[0].text  # type: ignore

    async def main() -> None:
        try:
            result = await test_claude_call()
            logger.info("API call succeeded", result=result)
        except Exception as e:
            logger.error("API call failed after retries", exception=str(e))

    # Run test
    asyncio.run(main())
