"""
Red flag models for CV analysis.

This module defines models for detected inconsistencies and concerns.
"""

from typing import Literal

from pydantic import BaseModel, Field


class RedFlag(BaseModel):
    """Detected inconsistency or concern in the CV."""

    type: str = Field(
        ...,
        min_length=1,
        description="Red flag classification",
        examples=[
            "employment_gap",
            "certification_mismatch",
            "skill_inconsistency",
            "frequent_job_changes",
            "missing_fundamentals",
            "unclear_progression",
        ],
    )

    severity: Literal["low", "medium", "high"] = Field(
        ..., description="Risk level assessment"
    )

    description: str = Field(
        ..., min_length=20, description="Detailed explanation of the concern"
    )

    impact: str = Field(
        ..., min_length=20, description="Potential implications for hiring decision"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "employment_gap",
                    "severity": "medium",
                    "description": "Unexplained 8-month gap between June 2023 and February 2024. No explanation provided for this period.",
                    "impact": "May indicate unstable employment history or personal issues. Recommend clarifying during interview.",
                },
                {
                    "type": "certification_mismatch",
                    "severity": "high",
                    "description": "Claims OSCP certification but lacks evidence of practical penetration testing experience in work history.",
                    "impact": "Potential resume embellishment. Verification questions should be asked about specific OSCP lab scenarios.",
                },
            ]
        }
    }
