"""
Improvement area models for CV analysis.

This module defines models for candidate development opportunities.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ImprovementArea(BaseModel):
    """Development opportunity with actionable recommendations."""

    area: str = Field(..., min_length=1, description="Parameter needing improvement")

    current_score: float = Field(
        ..., ge=0.0, le=10.0, description="Current score for this parameter"
    )

    gap_description: str = Field(
        ..., min_length=20, description="Explanation of the deficiency or gap"
    )

    recommendations: list[str] = Field(
        ...,
        min_length=1,
        description="Specific actionable suggestions for improvement",
    )

    priority: Literal["high", "medium", "low"] = Field(
        ..., description="Improvement urgency based on role requirements"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "area": "Certifications",
                    "current_score": 4.5,
                    "gap_description": "Limited professional certifications. Only holds CompTIA Security+ which is entry-level for a senior role.",
                    "recommendations": [
                        "Obtain OSCP certification to demonstrate offensive security skills",
                        "Consider CISSP for comprehensive security knowledge",
                        "Pursue cloud security certifications (AWS Security Specialty or Azure Security Engineer)",
                    ],
                    "priority": "high",
                }
            ]
        }
    }
