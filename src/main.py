"""
FastAPI application initialization for CV Cybersecurity Analyzer API.

This module sets up the FastAPI app with middleware, exception handlers,
CORS configuration, and routers.
"""

import asyncio
from contextlib import asynccontextmanager
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
import structlog

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# Concurrency control: limit to 10 concurrent requests (TC-001-005)
MAX_CONCURRENT_REQUESTS = 10
request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# Application metadata
APP_VERSION = "1.0.0"
APP_TITLE = "CV Cybersecurity Analyzer API"
APP_DESCRIPTION = """
Automated cybersecurity CV analysis using Claude Agent SDK.

This API accepts PDF CV uploads and provides:
- **24-parameter technical evaluation** across cybersecurity domains
- **Strengths identification** (top 5 candidate advantages)
- **Red flag detection** (gaps, inconsistencies, concerns)
- **Career development recommendations** (certifications, training, next roles)
- **Interview question suggestions** (technical, scenario, verification)

**Authentication**: All requests require `X-API-Key` header.

**Performance**: Analysis completes in <30 seconds (p95) for 2-4 page CVs.
"""

# Track application start time for uptime calculation
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Application starting",
        version=APP_VERSION,
        environment="production" if not settings.debug else "development",
        log_level=settings.log_level,
    )

    yield

    # Shutdown
    logger.info("Application shutting down")


# Initialize FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=settings.debug,
)


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def concurrency_limit_middleware(request: Request, call_next: Any) -> Any:
    """
    Middleware to enforce concurrency limit on requests.

    Limits concurrent requests to MAX_CONCURRENT_REQUESTS (10).
    Returns 503 Service Unavailable if limit is exceeded.
    """
    # Check if semaphore can be acquired (non-blocking check)
    if request_semaphore.locked() and request_semaphore._value == 0:
        logger.warning(
            "Concurrency limit reached",
            max_concurrent=MAX_CONCURRENT_REQUESTS,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": f"Server is currently handling maximum concurrent requests ({MAX_CONCURRENT_REQUESTS})",
                "error_code": "CONCURRENCY_LIMIT_REACHED",
                "status_code": 503,
            },
            headers={"Retry-After": "5"},
        )

    # Acquire semaphore and process request
    async with request_semaphore:
        return await call_next(request)


@app.middleware("http")
async def logging_middleware(request: Request, call_next: Any) -> Any:
    """
    Middleware for structured logging of all HTTP requests.

    Logs:
    - Request ID (X-Request-ID header or generated)
    - HTTP method and path
    - Processing duration
    - Status code
    - Client IP (if available)
    """
    # Generate or extract request ID
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")

    # Bind request context to logger
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None,
    )

    # Process request and measure duration
    start_time = time.time()

    try:
        response = await call_next(request)

        # Log successful request
        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "Request completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as e:
        # Log failed request
        duration_ms = int((time.time() - start_time) * 1000)

        logger.error(
            "Request failed",
            exception=str(e),
            exception_type=type(e).__name__,
            duration_ms=duration_ms,
        )

        raise


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom handler for HTTPException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Custom handler for request validation errors."""
    logger.warning("Request validation failed", errors=exc.errors())

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Request validation failed",
            "status_code": 400,
            "details": exc.errors(),
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Custom handler for Pydantic validation errors."""
    logger.warning("Data validation failed", errors=exc.errors())

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Data validation failed",
            "status_code": 422,
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Custom handler for unexpected exceptions."""
    logger.exception("Unhandled exception", exception=str(exc))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# Import and include routers
from src.api.analyze import router as analyze_router  # noqa: E402
from src.api.health import router as health_router  # noqa: E402

app.include_router(health_router, tags=["Health"])
app.include_router(analyze_router, tags=["Analysis"])

# Mount static files (frontend web application)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    """Root endpoint serves the frontend web application."""
    return FileResponse("static/index.html")


def get_uptime_seconds() -> int:
    """
    Get application uptime in seconds.

    Returns:
        int: Seconds since application started
    """
    return int(time.time() - app_start_time)


# Export for use in other modules
__all__ = ["app", "APP_VERSION", "get_uptime_seconds"]
