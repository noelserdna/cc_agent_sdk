"""
Response models for CV Cybersecurity Analyzer API.

This module defines the complete CVAnalysisResponse model that integrates
all analysis components.
"""

from pydantic import BaseModel, Field

from src.models.candidate import CandidateSummary
from src.models.improvement import ImprovementArea
from src.models.metadata import AnalysisMetadata
from src.models.recommendations import InterviewSuggestions, Recommendations
from src.models.redflag import RedFlag
from src.models.scores import DetailedScores
from src.models.strength import Strength


class CVAnalysisResponse(BaseModel):
    """Complete CV analysis result returned to client."""

    analysis_metadata: AnalysisMetadata = Field(
        ..., description="Metadata about the analysis process"
    )

    candidate_summary: CandidateSummary = Field(
        ..., description="High-level candidate profile and overall score"
    )

    detailed_scores: DetailedScores = Field(
        ..., description="Scores across all 24 cybersecurity parameters"
    )

    strengths: list[Strength] = Field(
        ...,
        min_length=5,
        max_length=5,
        description="Top 5 candidate strengths",
    )

    improvement_areas: list[ImprovementArea] = Field(
        ...,
        min_length=0,
        description="Prioritized development opportunities",
    )

    red_flags: list[RedFlag] = Field(
        default_factory=list,
        description="Detected concerns or inconsistencies",
    )

    recommendations: Recommendations = Field(
        ..., description="Career development suggestions"
    )

    interview_suggestions: InterviewSuggestions = Field(
        ..., description="Tailored technical interview questions"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "analysis_metadata": {
                        "timestamp": "2025-10-27T15:30:00Z",
                        "parsing_confidence": 0.95,
                        "cv_language": "es",
                        "analysis_version": "1.0.0",
                        "processing_duration_ms": 12543,
                    },
                    "candidate_summary": {
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
                    },
                    "detailed_scores": {
                        "certifications": {
                            "score": 9.0,
                            "justification": "Holds OSCP, CISSP, and AWS Security Specialty",
                            "evidence": ["OSCP", "CISSP", "AWS Security Specialty"],
                            "weight": 1.2,
                        },
                        # ... (other 23 parameters)
                    },
                    "strengths": [
                        {
                            "area": "Cloud Security",
                            "description": "Extensive AWS security experience",
                            "score": 9.0,
                            "market_value": "high",
                        },
                        # ... (4 more strengths)
                    ],
                    "improvement_areas": [
                        {
                            "area": "Forensics",
                            "current_score": 4.0,
                            "gap_description": "Limited digital forensics experience",
                            "recommendations": ["Take SANS FOR500 course"],
                            "priority": "medium",
                        }
                    ],
                    "red_flags": [],
                    "recommendations": {
                        "certifications": ["GIAC Cloud Security Automation"],
                        "training": ["Advanced Kubernetes security"],
                        "experience_areas": ["Container security"],
                        "next_role_suggestions": ["Principal Security Architect"],
                    },
                    "interview_suggestions": {
                        "technical_questions": [
                            "How would you secure a serverless application?",
                            "Explain your approach to threat modeling",
                            "Describe IAM best practices in AWS",
                        ],
                        "scenario_questions": [
                            "Tell me about a security incident you handled",
                            "How do you balance security and usability?",
                        ],
                        "verification_questions": [
                            "Walk me through your OSCP lab experience",
                        ],
                    },
                }
            ]
        }
    }
