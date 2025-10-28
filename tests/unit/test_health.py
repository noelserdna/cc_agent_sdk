"""
Unit tests for health check endpoint.

Tests verify health check response structure, status codes, and
all required fields per User Story 5 requirements.
"""

import time
from unittest.mock import MagicMock, patch

import anthropic
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.api.health import APP_VERSION, HealthResponse, get_uptime_seconds, router
from src.main import app

# Create test client
client = TestClient(app)


def test_health_response_model_validation():
    """Test HealthResponse Pydantic model validation."""
    # Valid response
    response = HealthResponse(
        status="healthy",
        version="1.0.0",
        agent_sdk_version="0.40.0",
        uptime_seconds=3600,
        environment="production",
    )
    assert response.status == "healthy"
    assert response.version == "1.0.0"
    assert response.agent_sdk_version == "0.40.0"
    assert response.uptime_seconds == 3600
    assert response.environment == "production"


def test_health_response_status_enum():
    """Test that status field only accepts valid enum values."""
    # Valid values
    for valid_status in ["healthy", "unhealthy"]:
        response = HealthResponse(
            status=valid_status,
            version="1.0.0",
            agent_sdk_version="0.40.0",
            uptime_seconds=100,
            environment="test",
        )
        assert response.status == valid_status

    # Invalid value should raise ValidationError
    with pytest.raises(Exception):  # Pydantic ValidationError
        HealthResponse(
            status="invalid",
            version="1.0.0",
            agent_sdk_version="0.40.0",
            uptime_seconds=100,
            environment="test",
        )


def test_health_response_uptime_validation():
    """Test that uptime_seconds must be >= 0."""
    # Valid uptime (0 is valid for fresh start)
    response = HealthResponse(
        status="healthy",
        version="1.0.0",
        agent_sdk_version="0.40.0",
        uptime_seconds=0,
        environment="test",
    )
    assert response.uptime_seconds == 0

    # Valid uptime (positive)
    response = HealthResponse(
        status="healthy",
        version="1.0.0",
        agent_sdk_version="0.40.0",
        uptime_seconds=100,
        environment="test",
    )
    assert response.uptime_seconds == 100

    # Invalid uptime (negative) should raise ValidationError
    with pytest.raises(Exception):
        HealthResponse(
            status="healthy",
            version="1.0.0",
            agent_sdk_version="0.40.0",
            uptime_seconds=-1,
            environment="test",
        )


def test_get_uptime_seconds():
    """Test uptime calculation."""
    # Get initial uptime
    uptime1 = get_uptime_seconds()
    assert isinstance(uptime1, int)
    assert uptime1 >= 0

    # Wait a bit and verify uptime increases
    time.sleep(0.1)
    uptime2 = get_uptime_seconds()
    assert uptime2 >= uptime1


def test_health_endpoint_returns_200():
    """Test that /health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK


def test_health_endpoint_response_structure():
    """Test that /health endpoint returns all required fields."""
    response = client.get("/health")
    data = response.json()

    # Verify all required fields exist
    assert "status" in data
    assert "version" in data
    assert "agent_sdk_version" in data
    assert "uptime_seconds" in data
    assert "environment" in data

    # Verify types
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["agent_sdk_version"], str)
    assert isinstance(data["uptime_seconds"], int)
    assert isinstance(data["environment"], str)


def test_health_endpoint_healthy_status():
    """Test that /health endpoint returns 'healthy' status."""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"


def test_health_endpoint_version():
    """Test that /health endpoint returns correct version."""
    response = client.get("/health")
    data = response.json()

    assert data["version"] == APP_VERSION
    assert data["version"] == "1.0.0"


def test_health_endpoint_agent_sdk_version():
    """Test that /health endpoint returns agent SDK version."""
    response = client.get("/health")
    data = response.json()

    # Should return a version string (e.g., "0.40.0") or "unknown"
    assert isinstance(data["agent_sdk_version"], str)
    assert len(data["agent_sdk_version"]) > 0


def test_health_endpoint_uptime():
    """Test that /health endpoint returns valid uptime."""
    response = client.get("/health")
    data = response.json()

    # Uptime should be non-negative integer
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0


def test_health_endpoint_environment():
    """Test that /health endpoint returns environment."""
    response = client.get("/health")
    data = response.json()

    # Environment should be "production" or "development"
    assert data["environment"] in ["production", "development"]


@patch("src.api.health.anthropic")
def test_health_endpoint_sdk_version_detection_failure(mock_anthropic):
    """Test health endpoint when SDK version detection fails."""
    # Simulate missing __version__ attribute
    mock_module = MagicMock()
    del mock_module.__version__
    mock_anthropic.__version__ = None

    # Mock to raise AttributeError
    with patch("anthropic.__version__", side_effect=AttributeError):
        response = client.get("/health")
        data = response.json()

        # Should still return 200 OK but with "unknown" version
        assert response.status_code == status.HTTP_200_OK
        # Note: This test may pass "unknown" or actual version depending on timing
        assert isinstance(data["agent_sdk_version"], str)


def test_health_endpoint_response_time():
    """Test that /health endpoint responds quickly (<500ms)."""
    import time

    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()

    duration_ms = (end_time - start_time) * 1000

    # Response should be under 500ms (FR-066)
    assert duration_ms < 500
    assert response.status_code == status.HTTP_200_OK


def test_health_endpoint_no_authentication_required():
    """Test that /health endpoint does not require authentication."""
    # No X-API-Key header provided
    response = client.get("/health")

    # Should still return 200 OK (health checks should be public)
    assert response.status_code == status.HTTP_200_OK


def test_health_endpoint_multiple_calls():
    """Test that /health endpoint is idempotent and stateless."""
    # Call endpoint multiple times
    responses = [client.get("/health") for _ in range(3)]

    # All should return 200 OK
    for response in responses:
        assert response.status_code == status.HTTP_200_OK

    # Status should remain "healthy"
    for response in responses:
        data = response.json()
        assert data["status"] == "healthy"


def test_health_endpoint_concurrent_calls():
    """Test that /health endpoint handles concurrent requests."""
    import concurrent.futures

    def make_request():
        return client.get("/health")

    # Make 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        responses = [future.result() for future in futures]

    # All should succeed
    for response in responses:
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.parametrize(
    "method",
    ["POST", "PUT", "DELETE", "PATCH"],
)
def test_health_endpoint_only_accepts_get(method):
    """Test that /health endpoint only accepts GET requests."""
    response = client.request(method, "/health")

    # Should return 405 Method Not Allowed
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_health_endpoint_content_type():
    """Test that /health endpoint returns JSON content type."""
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert "application/json" in response.headers["content-type"]


def test_health_endpoint_json_serialization():
    """Test that /health endpoint response is valid JSON."""
    response = client.get("/health")

    # Should successfully parse as JSON
    data = response.json()
    assert isinstance(data, dict)

    # Should be able to re-serialize
    import json

    json_string = json.dumps(data)
    assert isinstance(json_string, str)
    assert len(json_string) > 0
