"""
API key authentication service.

This module provides API key validation middleware and utilities for
securing the CV Cybersecurity Analyzer API endpoints.
"""

from typing import Annotated, Callable

from fastapi import Header, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# API key header scheme for OpenAPI documentation
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyAuth:
    """
    API key authentication service class.

    This class provides a stateful authentication service that can be
    initialized with custom valid keys (useful for testing).
    """

    def __init__(self, valid_keys: list[str] | None = None):
        """
        Initialize the API key authentication service.

        Args:
            valid_keys: Optional list of valid API keys. If None, uses settings.
        """
        self.valid_keys = valid_keys if valid_keys is not None else settings.api_keys_list

    def validate(self, api_key_or_request: str | Request) -> bool:
        """
        Validate an API key against the configured valid keys.

        Supports two modes:
        1. Direct API key validation: validate(api_key: str) -> bool
        2. Request validation: validate(request: Request) -> bool (raises HTTPException)

        Args:
            api_key_or_request: Either an API key string or a FastAPI Request object

        Returns:
            bool: True if the API key is valid

        Raises:
            HTTPException: 401 if Request is provided and key is missing or invalid
        """
        # If it's a Request object, validate from headers
        if isinstance(api_key_or_request, Request):
            api_key = self.extract_key(api_key_or_request)

            if api_key is None:
                logger.warning("Missing API key in request")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing API key. Provide X-API-Key header.",
                    headers={"WWW-Authenticate": "ApiKey"},
                )

            # Handle empty or whitespace-only keys
            if not api_key or not api_key.strip():
                logger.warning("Empty or whitespace API key in request")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "ApiKey"},
                )

            if api_key not in self.valid_keys:
                key_preview = api_key[:8] if len(api_key) >= 8 else "[INVALID]"
                logger.warning("Invalid API key attempt", key_preview=key_preview)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "ApiKey"},
                )

            return True

        # String mode: simple boolean validation
        return api_key_or_request in self.valid_keys

    def extract_key(self, request: Request) -> str | None:
        """
        Extract API key from request headers.

        Args:
            request: FastAPI Request object

        Returns:
            str | None: API key if present, None otherwise
        """
        # Check both lowercase and original case headers
        # FastAPI normalizes headers to lowercase internally
        return request.headers.get("x-api-key") or request.headers.get("X-API-Key")

    async def middleware(self, request: Request, call_next: Callable) -> dict:
        """
        Middleware function for FastAPI to validate API keys.

        Args:
            request: FastAPI Request object
            call_next: Next middleware/endpoint in the chain

        Returns:
            Response from the next middleware/endpoint

        Raises:
            HTTPException: 401 if API key is missing or invalid
        """
        # Validate will raise HTTPException if invalid
        self.validate(request)

        # If validation passed, continue to next middleware/endpoint
        response = await call_next(request)
        return response

    async def __call__(self, x_api_key: Annotated[str | None, Header()] = None) -> str:
        """
        Dependency callable for FastAPI to validate API keys.

        Args:
            x_api_key: API key from X-API-Key header

        Returns:
            str: Validated API key

        Raises:
            HTTPException: 401 if API key is missing or invalid
        """
        if x_api_key is None:
            logger.warning("Missing API key in request")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API key. Provide X-API-Key header.",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        if not self.validate(x_api_key):
            key_preview = x_api_key[:8] if len(x_api_key) >= 8 else "[INVALID]"
            logger.warning("Invalid API key attempt", key_preview=key_preview)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        key_id = x_api_key[:8] if len(x_api_key) >= 8 else x_api_key
        logger.debug("API key validated", api_key_id=key_id)
        return x_api_key


def validate_api_key(api_key: str | None, valid_keys: list[str] | None = None) -> bool:
    """
    Validate an API key against configured valid keys.

    Args:
        api_key: The API key to validate
        valid_keys: Optional list of valid keys. If None, uses settings.

    Returns:
        bool: True if the API key is valid, False otherwise
    """
    if api_key is None:
        return False

    # Handle empty or whitespace-only keys
    if not api_key or not api_key.strip():
        return False

    # Use provided valid_keys or fall back to settings
    keys_to_check = valid_keys if valid_keys is not None else settings.api_keys_list
    return api_key in keys_to_check


async def get_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
) -> str:
    """
    FastAPI dependency to extract and validate API key from request headers.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        str: Validated API key

    Raises:
        HTTPException: 401 if API key is missing or invalid
    """
    if x_api_key is None:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not validate_api_key(x_api_key):
        # Get first 8 characters of invalid key for logging (don't log full key)
        key_preview = x_api_key[:8] if len(x_api_key) >= 8 else "[INVALID]"

        logger.warning(
            "Invalid API key attempt",
            key_preview=key_preview,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Log successful authentication (first 8 chars only for security)
    key_id = x_api_key[:8] if len(x_api_key) >= 8 else x_api_key
    logger.debug("API key validated", api_key_id=key_id)

    return x_api_key


def get_api_key_id(api_key: str) -> str:
    """
    Get a safe identifier for an API key (first 8 characters).

    This is used for logging and tracking without exposing the full API key.

    Args:
        api_key: The full API key

    Returns:
        str: First 8 characters of the API key or shortened version
    """
    return api_key[:8] if len(api_key) >= 8 else api_key


# Example usage for testing
if __name__ == "__main__":
    # Test API key validation
    print("Testing API key validation...")

    # Get valid keys from settings
    valid_keys = settings.api_keys_list
    print(f"Valid keys configured: {len(valid_keys)}")

    if valid_keys:
        test_key = valid_keys[0]
        print(f"Test key ID: {get_api_key_id(test_key)}")
        print(f"Validation result: {validate_api_key(test_key)}")

    # Test invalid key
    invalid_key = "invalid-key-12345"
    print(f"Invalid key test: {validate_api_key(invalid_key)}")
