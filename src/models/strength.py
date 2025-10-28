"""
Strength models for CV analysis.

This module defines models for candidate strengths identification.
"""

from typing import Literal

from pydantic import BaseModel, Field


class Strength(BaseModel):
    """Identified candidate strength or advantage."""

    area: str = Field(..., min_length=1, description="Strength domain name")

    description: str = Field(
        ..., min_length=20, description="Detailed explanation of this strength"
    )

    score: float = Field(
        ..., ge=7.0, le=10.0, description="Associated parameter score (must be >= 7.0)"
    )

    market_value: Literal["high", "medium", "low"] = Field(
        ..., description="Current market demand for this strength"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "area": "Cloud Security",
                    "description": "Extensive experience with AWS security services including GuardDuty, Security Hub, and IAM. Holds AWS Security Specialty certification.",
                    "score": 9.0,
                    "market_value": "high",
                }
            ]
        }
    }
