"""
Metadata models for CV analysis.

This module defines models for analysis metadata and candidate summary.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisMetadata(BaseModel):
    """Metadata about the CV analysis process."""

    timestamp: datetime = Field(
        ..., description="Analysis completion timestamp in ISO 8601 format"
    )

    parsing_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Text extraction quality score (0.0-1.0)",
    )

    cv_language: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Detected CV language (ISO 639-1 code)",
        examples=["es", "en", "fr", "de"],
    )

    analysis_version: str = Field(
        ...,
        pattern=r"^\d+\.\d+\.\d+$",
        description="API version used for analysis (semver)",
        examples=["1.0.0", "1.2.3"],
    )

    processing_duration_ms: int = Field(
        ..., ge=0, description="Processing time in milliseconds"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "timestamp": "2025-10-27T15:30:00Z",
                    "parsing_confidence": 0.95,
                    "cv_language": "es",
                    "analysis_version": "1.0.0",
                    "processing_duration_ms": 12543,
                }
            ]
        }
    }


class YearsExperience(BaseModel):
    """Experience breakdown in years."""

    total_it: float = Field(..., ge=0, description="Total years in IT/technology")

    cybersecurity: float = Field(..., ge=0, description="Years specifically in cybersecurity")

    current_role: float = Field(..., ge=0, description="Years in current role")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"total_it": 8.5, "cybersecurity": 5.0, "current_role": 2.5}
            ]
        }
    }
