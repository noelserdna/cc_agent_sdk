"""
Candidate models for CV analysis.

This module defines models for candidate summary and profile information.
"""

from typing import Literal

from pydantic import BaseModel, Field

from src.models.metadata import YearsExperience


class CandidateSummary(BaseModel):
    """High-level candidate profile summary."""

    name: str = Field(..., min_length=2, description="Extracted candidate name")

    total_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Weighted average score across all 24 parameters",
    )

    percentile: int = Field(
        ...,
        ge=0,
        le=100,
        description="Ranking vs market benchmarks (0-100 percentile)",
    )

    detected_role: str = Field(
        ..., min_length=1, description="Primary cybersecurity specialization"
    )

    seniority_level: Literal["Junior", "Mid", "Senior", "Lead", "Executive"] = Field(
        ..., description="Career level based on experience and responsibilities"
    )

    years_experience: YearsExperience = Field(..., description="Experience breakdown by category")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Jane Candidate",
                    "total_score": 8.2,
                    "percentile": 85,
                    "detected_role": "Cloud Security Architect",
                    "seniority_level": "Senior",
                    "years_experience": {
                        "total_it": 10.0,
                        "cybersecurity": 6.5,
                        "current_role": 3.0,
                    },
                }
            ]
        }
    }
