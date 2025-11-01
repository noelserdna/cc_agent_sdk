"""CV Analysis API endpoint.

This module implements the POST /analyze-cv endpoint for uploading
and analyzing cybersecurity CVs.
"""

import asyncio
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

import structlog
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from src.core.config import Settings, get_settings
from src.models.response import CVAnalysisResponse
from src.services.agent.cv_analyzer_agent import CVAnalyzerAgent
from src.services.api_auth import validate_api_key

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["analysis"])

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPE = "application/pdf"


@router.post(
    "/analyze-cv",
    response_model=CVAnalysisResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "CV analysis completed successfully",
            "model": CVAnalysisResponse,
        },
        400: {
            "description": "Bad request - Invalid file format or low parsing quality",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File must be a PDF",
                        "error_code": "INVALID_FILE_FORMAT",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - Invalid or missing API key",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid API key",
                        "error_code": "UNAUTHORIZED",
                    }
                }
            },
        },
        413: {
            "description": "Payload too large - File exceeds 10MB limit",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File size exceeds 10MB limit",
                        "error_code": "FILE_TOO_LARGE",
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error",
                        "error_code": "INTERNAL_ERROR",
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - Claude API error or timeout",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Service temporarily unavailable",
                        "error_code": "SERVICE_UNAVAILABLE",
                        "retry_after": 60,
                    }
                }
            },
        },
    },
    summary="Analyze a cybersecurity CV",
    description="""
    Upload a PDF CV and receive a comprehensive cybersecurity analysis.

    The analysis includes:
    - Candidate summary with overall score and role detection
    - Detailed scoring across 24 cybersecurity parameters
    - Top 5 strengths
    - Improvement areas with recommendations
    - Red flags and inconsistencies
    - Career development suggestions
    - Tailored interview questions

    **Requirements:**
    - Valid API key in X-API-Key header
    - PDF file (max 10MB)
    - Digital PDF recommended (scanned PDFs may have lower quality)

    **Performance:**
    - Response time: <30 seconds (p95)
    - Timeout: 30 seconds total
    """,
)
async def analyze_cv(
    file: Annotated[UploadFile, File(description="PDF file containing the CV to analyze")],
    x_api_key: Annotated[str, Header(description="API key for authentication")],
    role_target: Annotated[
        str | None,
        Form(
            description="Optional target role for contextualized analysis",
            min_length=3,
            max_length=100,
        ),
    ] = None,
    language: Annotated[
        Literal["es", "en"],
        Form(description="Preferred output language for analysis"),
    ] = "es",
    settings: Settings = Depends(get_settings),
) -> CVAnalysisResponse:
    """Analyze a cybersecurity CV and return detailed evaluation.

    Args:
        file: Uploaded PDF file
        x_api_key: API key from header
        role_target: Optional target role for contextualized analysis
        language: Output language (es or en)
        settings: Application settings (injected)

    Returns:
        CVAnalysisResponse with complete analysis

    Raises:
        HTTPException: Various status codes for different error conditions
    """
    request_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    start_time = datetime.now(timezone.utc)

    logger.info(
        "cv_analysis_request_received",
        request_id=request_id,
        filename=file.filename,
        content_type=file.content_type,
        role_target=role_target,
        language=language,
    )

    # Validate API key first (before processing file)
    try:
        validate_api_key(x_api_key, settings)
    except ValueError as e:
        logger.warning(
            "api_key_validation_failed",
            request_id=request_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Invalid API key", "error_code": "UNAUTHORIZED"},
        ) from e

    # Validate file content type
    if file.content_type != ALLOWED_CONTENT_TYPE:
        logger.warning(
            "invalid_file_format",
            request_id=request_id,
            content_type=file.content_type,
            filename=file.filename,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": f"File must be a PDF (received: {file.content_type})",
                "error_code": "INVALID_FILE_FORMAT",
            },
        )

    # Read file content to check size
    file_content = await file.read()
    file_size = len(file_content)

    logger.debug("file_content_read", request_id=request_id, file_size_bytes=file_size)

    # Validate file size
    if file_size > MAX_FILE_SIZE:
        logger.warning(
            "file_too_large",
            request_id=request_id,
            file_size_bytes=file_size,
            max_size_bytes=MAX_FILE_SIZE,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "detail": f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds 10MB limit",
                "error_code": "FILE_TOO_LARGE",
            },
        )

    # Check for empty file
    if file_size == 0:
        logger.warning("empty_file", request_id=request_id, filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "File is empty",
                "error_code": "EMPTY_FILE",
            },
        )

    # Create temporary file for PDF extraction
    temp_file_path: Path | None = None
    try:
        # Write to temporary file
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pdf", delete=False
        ) as temp_file:
            temp_file.write(file_content)
            temp_file_path = Path(temp_file.name)

        logger.debug(
            "temp_file_created",
            request_id=request_id,
            temp_file_path=str(temp_file_path),
        )

        # Initialize agent and analyze CV with timeout enforcement
        # The Agent SDK internally uses the 'pdf' skill for extraction
        try:
            agent = CVAnalyzerAgent(settings)

            # Wrap agent call in timeout to enforce 30s SLA
            try:
                analysis_result = await asyncio.wait_for(
                    agent.analyze_cv(
                        pdf_path=str(temp_file_path),
                        role_target=role_target,
                        language=language,
                    ),
                    timeout=settings.analysis_timeout_seconds,
                )
            except asyncio.TimeoutError as timeout_err:
                logger.error(
                    "analysis_timeout",
                    request_id=request_id,
                    timeout_seconds=settings.analysis_timeout_seconds,
                    elapsed_seconds=(datetime.now(timezone.utc) - start_time).total_seconds(),
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "detail": f"Analysis timeout after {settings.analysis_timeout_seconds}s. Please try again with a shorter CV or contact support.",
                        "error_code": "ANALYSIS_TIMEOUT",
                        "timeout_seconds": settings.analysis_timeout_seconds,
                    },
                    headers={"Retry-After": "120"},  # Suggest retry after 2 minutes
                ) from timeout_err

            # Update processing duration in metadata
            end_time = datetime.now(timezone.utc)
            processing_duration_ms = int((end_time - start_time).total_seconds() * 1000)
            analysis_result.analysis_metadata.processing_duration_ms = processing_duration_ms

            logger.info(
                "cv_analysis_complete",
                request_id=request_id,
                processing_duration_ms=processing_duration_ms,
                total_score=analysis_result.candidate_summary.total_score,
                detected_role=analysis_result.candidate_summary.detected_role,
            )

            return analysis_result

        except ValueError as e:
            # Agent validation errors (e.g., low confidence)
            logger.error("agent_validation_error", request_id=request_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "detail": str(e),
                    "error_code": "VALIDATION_ERROR",
                },
            ) from e

        except RuntimeError as e:
            # Claude API errors
            logger.error("claude_api_error", request_id=request_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "detail": "Service temporarily unavailable. Please try again later.",
                    "error_code": "SERVICE_UNAVAILABLE",
                },
                headers={"Retry-After": "60"},
            ) from e

        except Exception as e:
            # Unexpected errors
            logger.exception(
                "unexpected_error",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "detail": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                },
            ) from e

    finally:
        # Always cleanup temporary file
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
                logger.debug(
                    "temp_file_deleted",
                    request_id=request_id,
                    temp_file_path=str(temp_file_path),
                )
            except Exception as e:
                logger.warning(
                    "temp_file_cleanup_failed",
                    request_id=request_id,
                    temp_file_path=str(temp_file_path),
                    error=str(e),
                )
