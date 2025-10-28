"""
Health check router for CV Cybersecurity Analyzer API.

This module provides the /health endpoint for monitoring service availability
and operational metrics.
"""

import time
from typing import Literal

import anthropic
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter()

# Application constants (avoiding circular import with main.py)
APP_VERSION = "1.0.0"
_app_start_time = time.time()


def get_uptime_seconds() -> int:
    """
    Get application uptime in seconds.

    Returns:
        int: Number of seconds since application started
    """
    return int(time.time() - _app_start_time)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: Literal["healthy", "unhealthy"] = Field(
        ..., description="Service health status"
    )

    version: str = Field(..., description="API version")

    agent_sdk_version: str = Field(..., description="Claude Agent SDK version")

    uptime_seconds: int = Field(..., ge=0, description="Application uptime in seconds")

    environment: str = Field(..., description="Runtime environment")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "healthy",
                    "version": "1.0.0",
                    "agent_sdk_version": "0.40.0",
                    "uptime_seconds": 3600,
                    "environment": "production",
                }
            ]
        }
    }


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check service health and get operational metrics",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "agent_sdk_version": "0.40.0",
                        "uptime_seconds": 3600,
                        "environment": "production",
                    }
                }
            },
        },
        503: {
            "description": "Service is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "version": "1.0.0",
                        "agent_sdk_version": "0.40.0",
                        "uptime_seconds": 120,
                        "environment": "production",
                        "error": "Unable to connect to Claude API",
                    }
                }
            },
        },
    },
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse: Service health status and metrics

    Checks:
    - Application is running (always passes if endpoint is reachable)
    - Claude Agent SDK version is available
    - Uptime tracking is working
    """
    try:
        # Get Agent SDK version
        try:
            sdk_version = anthropic.__version__
        except AttributeError:
            sdk_version = "unknown"
            logger.warning("Unable to detect Claude Agent SDK version")

        # Get uptime
        uptime = get_uptime_seconds()

        # Determine environment
        environment = "production" if not settings.debug else "development"

        # Log health check
        logger.debug(
            "Health check performed",
            status="healthy",
            version=APP_VERSION,
            uptime_seconds=uptime,
        )

        return HealthResponse(
            status="healthy",
            version=APP_VERSION,
            agent_sdk_version=sdk_version,
            uptime_seconds=uptime,
            environment=environment,
        )

    except Exception as e:
        # If health check itself fails, log and return unhealthy
        logger.error("Health check failed", exception=str(e))

        # Try to return partial health information
        return HealthResponse(
            status="unhealthy",
            version=APP_VERSION,
            agent_sdk_version="unknown",
            uptime_seconds=get_uptime_seconds(),
            environment="unknown",
        )
