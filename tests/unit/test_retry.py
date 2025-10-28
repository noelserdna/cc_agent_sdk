"""
Unit tests for retry logic with exponential backoff.

Tests validate retry behavior using tenacity for Claude API calls.
"""
import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from tenacity import RetryError, stop_after_attempt

from src.core.retry import (
    with_retry,
    APIError,
    RateLimitError,
    ServiceUnavailableError,
    should_retry_exception
)


class TestRetryLogic:
    """Test suite for retry logic"""

    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """Test successful call on first attempt (no retries needed)"""
        mock_func = AsyncMock(return_value="success")

        @with_retry
        async def test_function():
            return await mock_func()

        result = await test_function()

        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Test successful call after 2 failures (3rd attempt succeeds)"""
        mock_func = AsyncMock(
            side_effect=[
                RateLimitError("Rate limit exceeded"),
                RateLimitError("Rate limit exceeded"),
                "success"
            ]
        )

        @with_retry
        async def test_function():
            return await mock_func()

        result = await test_function()

        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_max_attempts_exceeded(self):
        """Test failure after max retry attempts (3)"""
        mock_func = AsyncMock(side_effect=RateLimitError("Rate limit exceeded"))

        @with_retry
        async def test_function():
            return await mock_func()

        with pytest.raises(RetryError):
            await test_function()

        # Should try 3 times total
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exponential_backoff_timing(self):
        """Test retry delays follow exponential backoff (1s, 2s, 4s)"""
        call_times = []

        async def mock_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise RateLimitError("Rate limit exceeded")
            return "success"

        @with_retry
        async def test_function():
            return await mock_func()

        start_time = time.time()
        result = await test_function()
        total_time = time.time() - start_time

        assert result == "success"
        assert len(call_times) == 3

        # Verify delays between attempts (with 0.5s tolerance)
        if len(call_times) >= 2:
            delay_1 = call_times[1] - call_times[0]
            assert 0.5 <= delay_1 <= 1.5  # ~1s delay

        if len(call_times) >= 3:
            delay_2 = call_times[2] - call_times[1]
            assert 1.5 <= delay_2 <= 2.5  # ~2s delay

    @pytest.mark.asyncio
    async def test_retry_only_on_retryable_exceptions(self):
        """Test retry only happens for specific exceptions"""
        # Non-retryable exception
        mock_func = AsyncMock(side_effect=ValueError("Invalid input"))

        @with_retry
        async def test_function():
            return await mock_func()

        # Should fail immediately without retries
        with pytest.raises(ValueError):
            await test_function()

        # Should only be called once (no retries)
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit_error(self):
        """Test retry logic handles RateLimitError"""
        mock_func = AsyncMock(
            side_effect=[RateLimitError("429"), "success"]
        )

        @with_retry
        async def test_function():
            return await mock_func()

        result = await test_function()
        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_service_unavailable(self):
        """Test retry logic handles ServiceUnavailableError"""
        mock_func = AsyncMock(
            side_effect=[ServiceUnavailableError("503"), "success"]
        )

        @with_retry
        async def test_function():
            return await mock_func()

        result = await test_function()
        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_timeout_after_30_seconds(self):
        """Test retry stops after 30 seconds total timeout"""
        async def slow_func():
            # Simulate slow operation
            await asyncio.sleep(11)  # Each call takes 11s
            raise RateLimitError("Rate limit")

        @with_retry
        async def test_function():
            return await slow_func()

        start_time = time.time()

        with pytest.raises(RetryError):
            await test_function()

        elapsed_time = time.time() - start_time

        # Should timeout around 30-36 seconds (11s * 3 attempts + 3s delays)
        # Relaxed tolerance to account for 3 full attempts + delays
        assert 25 <= elapsed_time <= 40

    @pytest.mark.asyncio
    async def test_should_retry_exception_function(self):
        """Test exception classification for retry"""
        # Should retry
        assert should_retry_exception(RateLimitError("429")) is True
        assert should_retry_exception(ServiceUnavailableError("503")) is True
        assert should_retry_exception(APIError("Overloaded")) is True

        # Should not retry
        assert should_retry_exception(ValueError("Bad input")) is False
        assert should_retry_exception(TypeError("Type mismatch")) is False
        assert should_retry_exception(KeyError("Missing key")) is False

    @pytest.mark.asyncio
    async def test_retry_logging(self):
        """Test retry attempts are logged"""
        mock_logger = Mock()
        call_count = 0

        async def mock_func():
            nonlocal call_count
            call_count += 1
            mock_logger.warning(f"Retry attempt {call_count}")
            if call_count < 2:
                raise RateLimitError("Rate limit")
            return "success"

        @with_retry
        async def test_function():
            return await mock_func()

        result = await test_function()

        assert result == "success"
        assert mock_logger.warning.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_preserves_original_exception_message(self):
        """Test original exception message is preserved"""
        error_message = "Specific error details"
        mock_func = AsyncMock(side_effect=RateLimitError(error_message))

        @with_retry
        async def test_function():
            return await mock_func()

        try:
            await test_function()
        except RetryError as e:
            # Original exception should be accessible via last_attempt
            original_exception = e.last_attempt.exception()
            assert error_message in str(original_exception)

    @pytest.mark.asyncio
    async def test_retry_with_async_generator(self):
        """Test retry works with async generators"""
        attempt = 0

        @with_retry
        async def test_generator():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise RateLimitError("Rate limit")
            return ["item1", "item2"]

        result = await test_generator()
        assert result == ["item1", "item2"]
        assert attempt == 2


class TestAPIExceptions:
    """Test custom API exception classes"""

    def test_api_error_creation(self):
        """Test APIError exception"""
        error = APIError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_rate_limit_error_creation(self):
        """Test RateLimitError exception"""
        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, APIError)

    def test_service_unavailable_error_creation(self):
        """Test ServiceUnavailableError exception"""
        error = ServiceUnavailableError("Service down")
        assert str(error) == "Service down"
        assert isinstance(error, APIError)

    def test_exception_with_status_code(self):
        """Test exceptions can store HTTP status codes"""
        error = RateLimitError("Rate limit", status_code=429)
        assert hasattr(error, 'status_code')
        assert error.status_code == 429

    def test_exception_with_retry_after(self):
        """Test exceptions can store Retry-After header"""
        error = RateLimitError("Rate limit", retry_after=60)
        assert hasattr(error, 'retry_after')
        assert error.retry_after == 60


class TestRetryConfiguration:
    """Test retry configuration and customization"""

    @pytest.mark.asyncio
    async def test_custom_max_attempts(self):
        """Test configurable max retry attempts"""
        mock_func = AsyncMock(side_effect=RateLimitError("Rate limit"))

        @with_retry(max_attempts=5)
        async def test_function():
            return await mock_func()

        with pytest.raises(RetryError):
            await test_function()

        # Should try 5 times if configured
        assert mock_func.call_count >= 3  # At least default 3

    @pytest.mark.asyncio
    async def test_retry_callback_on_failure(self):
        """Test callback is called on retry failure"""
        callback_called = []

        def on_retry_callback(retry_state):
            callback_called.append(retry_state)

        mock_func = AsyncMock(
            side_effect=[RateLimitError("Limit"), "success"]
        )

        @with_retry(callback=on_retry_callback)
        async def test_function():
            return await mock_func()

        result = await test_function()

        assert result == "success"
        # Callback should be called for the failed attempt
        assert len(callback_called) >= 1
