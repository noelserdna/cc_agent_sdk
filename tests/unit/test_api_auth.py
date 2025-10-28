"""
Unit tests for API key authentication middleware.

Tests validate API key authentication logic without making actual HTTP requests.
"""
import pytest
from fastapi import HTTPException, Request
from unittest.mock import Mock, AsyncMock

from src.services.api_auth import APIKeyAuth, validate_api_key


@pytest.fixture
def valid_api_keys():
    """List of valid API keys for testing"""
    return ["test-key-1", "test-key-2", "test-key-3"]


@pytest.fixture
def auth_service(valid_api_keys):
    """APIKeyAuth service instance"""
    return APIKeyAuth(valid_keys=valid_api_keys)


@pytest.fixture
def mock_request_with_valid_key():
    """Mock FastAPI request with valid API key"""
    request = Mock(spec=Request)
    request.headers = {"x-api-key": "test-key-1"}
    return request


@pytest.fixture
def mock_request_without_key():
    """Mock FastAPI request without API key"""
    request = Mock(spec=Request)
    request.headers = {}
    return request


@pytest.fixture
def mock_request_with_invalid_key():
    """Mock FastAPI request with invalid API key"""
    request = Mock(spec=Request)
    request.headers = {"x-api-key": "invalid-key"}
    return request


class TestAPIKeyAuth:
    """Test suite for API key authentication"""

    def test_validate_api_key_success(self, auth_service, mock_request_with_valid_key):
        """Test successful API key validation"""
        # Should not raise exception
        result = auth_service.validate(mock_request_with_valid_key)
        assert result is True

    def test_validate_api_key_missing(self, auth_service, mock_request_without_key):
        """Test validation fails when API key is missing"""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate(mock_request_without_key)

        assert exc_info.value.status_code == 401
        assert "api key" in str(exc_info.value.detail).lower()
        assert "missing" in str(exc_info.value.detail).lower()

    def test_validate_api_key_invalid(self, auth_service, mock_request_with_invalid_key):
        """Test validation fails with invalid API key"""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate(mock_request_with_invalid_key)

        assert exc_info.value.status_code == 401
        assert "invalid" in str(exc_info.value.detail).lower()

    def test_validate_api_key_case_sensitive(self, auth_service):
        """Test API key validation is case-sensitive"""
        request = Mock(spec=Request)
        request.headers = {"x-api-key": "TEST-KEY-1"}  # Uppercase

        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate(request)

        assert exc_info.value.status_code == 401

    def test_validate_api_key_header_case_insensitive(self, auth_service):
        """Test header name is case-insensitive (HTTP standard)"""
        request = Mock(spec=Request)
        # FastAPI normalizes headers to lowercase
        request.headers = {"X-API-Key": "test-key-1"}  # Mixed case header

        # Should work if headers dict is case-insensitive
        # In real FastAPI, headers are case-insensitive
        result = auth_service.validate(request)
        assert result is True

    def test_multiple_valid_keys(self, valid_api_keys):
        """Test authentication works with multiple valid keys"""
        auth_service = APIKeyAuth(valid_keys=valid_api_keys)

        for key in valid_api_keys:
            request = Mock(spec=Request)
            request.headers = {"x-api-key": key}
            result = auth_service.validate(request)
            assert result is True

    def test_empty_api_key(self, auth_service):
        """Test validation fails with empty API key"""
        request = Mock(spec=Request)
        request.headers = {"x-api-key": ""}

        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate(request)

        assert exc_info.value.status_code == 401

    def test_whitespace_api_key(self, auth_service):
        """Test validation fails with whitespace-only API key"""
        request = Mock(spec=Request)
        request.headers = {"x-api-key": "   "}

        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate(request)

        assert exc_info.value.status_code == 401

    def test_api_key_with_prefix(self, auth_service):
        """Test API key with Bearer prefix is rejected"""
        request = Mock(spec=Request)
        request.headers = {"x-api-key": "Bearer test-key-1"}

        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate(request)

        assert exc_info.value.status_code == 401

    def test_extract_api_key_from_request(self, auth_service, mock_request_with_valid_key):
        """Test extracting API key from request"""
        api_key = auth_service.extract_key(mock_request_with_valid_key)
        assert api_key == "test-key-1"

    def test_extract_api_key_returns_none_if_missing(self, auth_service, mock_request_without_key):
        """Test extracting API key returns None when missing"""
        api_key = auth_service.extract_key(mock_request_without_key)
        assert api_key is None

    @pytest.mark.asyncio
    async def test_middleware_integration(self, auth_service, mock_request_with_valid_key):
        """Test authentication middleware integration"""
        # Mock call_next function
        async def mock_call_next(request):
            return {"status": "success"}

        # Test middleware allows valid requests
        response = await auth_service.middleware(mock_request_with_valid_key, mock_call_next)
        assert response["status"] == "success"

    @pytest.mark.asyncio
    async def test_middleware_blocks_invalid_requests(self, auth_service, mock_request_without_key):
        """Test middleware blocks requests without valid API key"""
        async def mock_call_next(request):
            return {"status": "success"}

        # Should raise HTTPException before calling next
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.middleware(mock_request_without_key, mock_call_next)

        assert exc_info.value.status_code == 401

    def test_error_response_structure(self, auth_service, mock_request_without_key):
        """Test error response has proper structure"""
        try:
            auth_service.validate(mock_request_without_key)
        except HTTPException as exc:
            # Verify exception has required fields
            assert hasattr(exc, 'status_code')
            assert hasattr(exc, 'detail')
            assert exc.status_code == 401
            assert isinstance(exc.detail, str)

    def test_validate_with_www_authenticate_header(self, auth_service, mock_request_without_key):
        """Test response includes WWW-Authenticate header"""
        try:
            auth_service.validate(mock_request_without_key)
        except HTTPException as exc:
            # Should include WWW-Authenticate header for 401 responses
            if hasattr(exc, 'headers'):
                assert 'WWW-Authenticate' in exc.headers


class TestValidateAPIKeyFunction:
    """Test standalone validate_api_key function"""

    def test_standalone_validate_function(self, valid_api_keys):
        """Test standalone validation function"""
        assert validate_api_key("test-key-1", valid_api_keys) is True
        assert validate_api_key("invalid-key", valid_api_keys) is False
        assert validate_api_key("", valid_api_keys) is False
        assert validate_api_key(None, valid_api_keys) is False

    def test_validate_with_empty_valid_keys_list(self):
        """Test validation fails when no valid keys configured"""
        assert validate_api_key("any-key", []) is False
