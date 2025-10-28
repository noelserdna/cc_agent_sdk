"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

from src.main import app


@pytest_asyncio.fixture
async def async_client():
    """
    Async HTTP client for testing FastAPI application.

    Uses ASGITransport to properly test ASGI app without starting a server.
    Compatible with httpx 0.27.0+
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def client():
    """
    Sync HTTP client for testing FastAPI application.

    Uses TestClient for synchronous tests (e.g., performance tests).
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def valid_api_key():
    """Valid API key for testing (matches .env.example)"""
    return "test-api-key-123"


@pytest.fixture
def sample_cv_path(tmp_path):
    """Path to sample cybersecurity CV for testing"""
    from pathlib import Path
    # Use the actual sample CV path from fixtures
    cv_path = Path("tests/fixtures/sample_cvs/sample_cybersecurity_cv.pdf")
    if cv_path.exists():
        return cv_path
    # Fallback: create a minimal test PDF if sample doesn't exist
    test_pdf = tmp_path / "test_cv.pdf"
    test_pdf.write_text("Test CV content")
    return test_pdf
