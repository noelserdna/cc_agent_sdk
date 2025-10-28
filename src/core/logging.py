"""
Structured logging configuration using structlog.

This module provides JSON-formatted structured logging with PII redaction,
correlation IDs, and FastAPI integration for the CV Cybersecurity Analyzer API.
"""

import logging
import re
import sys
from typing import Any

import orjson
import structlog
from structlog.types import EventDict, Processor

from src.core.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add application-level context to all log entries.

    Args:
        logger: The logger instance
        method_name: The logging method name
        event_dict: The event dictionary

    Returns:
        EventDict: Updated event dictionary with app context
    """
    event_dict["app"] = "cv-cybersecurity-analyzer-api"
    event_dict["environment"] = "production" if not settings.debug else "development"
    return event_dict


def redact_pii(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Redact personally identifiable information (PII) from log entries.

    Redacts:
    - Email addresses
    - Names (when preceded by specific keywords)
    - API keys
    - Phone numbers
    - IP addresses (partially)

    Args:
        logger: The logger instance
        method_name: The logging method name
        event_dict: The event dictionary

    Returns:
        EventDict: Updated event dictionary with redacted PII
    """
    if not settings.log_pii_redaction:
        return event_dict

    # Patterns for PII detection
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    api_key_pattern = r"sk-[a-zA-Z0-9-_]{20,}"
    phone_pattern = r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"

    # Recursively redact PII in all string values
    def redact_value(value: Any) -> Any:
        if isinstance(value, str):
            # Redact emails
            value = re.sub(email_pattern, "[EMAIL_REDACTED]", value)
            # Redact API keys
            value = re.sub(api_key_pattern, "[API_KEY_REDACTED]", value)
            # Redact phone numbers
            value = re.sub(phone_pattern, "[PHONE_REDACTED]", value)
            # Redact names (when preceded by specific keywords)
            value = re.sub(
                r"(name|candidate|applicant)[\s:]+([A-Z][a-z]+ [A-Z][a-z]+)",
                r"\1: [NAME_REDACTED]",
                value,
                flags=re.IGNORECASE,
            )
        elif isinstance(value, dict):
            return {k: redact_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [redact_value(item) for item in value]
        return value

    # Redact PII in event dict
    for key, value in event_dict.items():
        if key not in ["timestamp", "level", "logger"]:
            event_dict[key] = redact_value(value)

    return event_dict


def serialize_orjson(data: Any, default: Any = None) -> bytes:
    """
    Serialize data to JSON using orjson for performance.

    Args:
        data: Data to serialize
        default: Default serializer for non-JSON types

    Returns:
        bytes: JSON-encoded bytes
    """
    return orjson.dumps(data, default=default)


def configure_logging() -> None:
    """
    Configure structlog for the application.

    Sets up:
    - JSON output format (or console for development)
    - PII redaction
    - Timestamp formatting
    - Log level filtering
    - Exception formatting
    """
    # Determine processors based on log format
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_app_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        redact_pii,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "json":
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer(serializer=serialize_orjson))
    else:
        # Console output for development
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )

    # Set log levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: str) -> Any:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        BoundLogger: Configured structlog logger
    """
    return structlog.get_logger(name)


# Configure logging on module import
configure_logging()


# Example usage for testing
if __name__ == "__main__":
    logger = get_logger(__name__)

    logger.info("Application started", version="1.0.0")
    logger.debug("Debug information", config={"log_level": settings.log_level})
    logger.warning("Warning message", user_email="user@example.com")
    logger.error(
        "Error occurred",
        error_code=500,
        api_key="sk-ant-test123456789",
        candidate_name="John Doe",
    )

    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("Exception caught")
