"""
Request models for CV Cybersecurity Analyzer API.

This module defines Pydantic models for incoming HTTP requests.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CVAnalysisRequestForm(BaseModel):
    """
    Form data for CV analysis request.

    This model validates optional parameters for CV analysis.
    The file upload is handled separately by FastAPI's UploadFile.
    """

    role_target: str | None = Field(
        None,
        min_length=3,
        max_length=100,
        description="Optional target role for contextualized analysis",
        examples=["Senior Cloud Security Engineer", "Penetration Tester"],
    )

    language: Literal["es", "en"] = Field(
        default="es",
        description="Preferred output language for analysis",
    )

    @field_validator("role_target")
    @classmethod
    def validate_role_target(cls, v: str | None) -> str | None:
        """Validate role_target contains only safe characters."""
        if v and not v.replace(" ", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "role_target must contain only alphanumeric characters, spaces, hyphens, and underscores"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role_target": "Cloud Security Architect",
                    "language": "en",
                },
                {"language": "es"},
            ]
        }
    }
