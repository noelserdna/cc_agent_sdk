"""
Recommendation models for CV analysis.

This module defines models for career development recommendations.
"""

from pydantic import BaseModel, Field


class Recommendations(BaseModel):
    """Career development suggestions tailored to the candidate's profile."""

    certifications: list[str] = Field(
        default_factory=list,
        description="Suggested professional certifications to pursue",
        examples=[
            [
                "OSCP - Offensive Security Certified Professional",
                "CISSP - Certified Information Systems Security Professional",
                "AWS Certified Security - Specialty",
            ]
        ],
    )

    training: list[str] = Field(
        default_factory=list,
        description="Recommended courses or training programs",
        examples=[
            [
                "Advanced Web Application Security course",
                "Cloud Security Architecture bootcamp",
                "Incident Response and Forensics training",
            ]
        ],
    )

    experience_areas: list[str] = Field(
        default_factory=list,
        description="Domains to gain hands-on experience",
        examples=[
            [
                "Kubernetes security and container hardening",
                "Threat hunting and detection engineering",
                "Security automation and orchestration (SOAR)",
            ]
        ],
    )

    next_role_suggestions: list[str] = Field(
        default_factory=list,
        description="Potential next career moves based on current profile",
        examples=[
            [
                "Senior Security Engineer",
                "Security Architect",
                "Principal Security Consultant",
            ]
        ],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "certifications": [
                        "OSCP - Offensive Security Certified Professional",
                        "GIAC Cloud Security Automation (GCSA)",
                    ],
                    "training": [
                        "Advanced Kubernetes security course",
                        "Cloud-native security architecture",
                    ],
                    "experience_areas": [
                        "Cloud security posture management (CSPM)",
                        "Infrastructure as Code security scanning",
                    ],
                    "next_role_suggestions": [
                        "Cloud Security Architect",
                        "DevSecOps Lead",
                    ],
                }
            ]
        }
    }


class InterviewSuggestions(BaseModel):
    """Tailored technical interview questions based on CV analysis."""

    technical_questions: list[str] = Field(
        ...,
        min_length=3,
        description="Domain-specific technical questions",
        examples=[
            [
                "Explain your approach to securing a Kubernetes cluster in production",
                "Describe a recent penetration test you performed and the most critical vulnerability you discovered",
                "How would you design a zero-trust architecture for a multi-cloud environment?",
            ]
        ],
    )

    scenario_questions: list[str] = Field(
        ...,
        min_length=2,
        description="Situational and behavioral questions",
        examples=[
            [
                "Tell me about a time you identified a critical security flaw that others missed",
                "Describe how you would handle a situation where development teams resist security requirements",
            ]
        ],
    )

    verification_questions: list[str] = Field(
        default_factory=list,
        description="Questions to verify specific claims or certifications",
        examples=[
            [
                "Can you walk me through your OSCP lab experience and methodology?",
                "You mentioned implementing zero-trust at your previous company - what specific technologies did you use?",
            ]
        ],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "technical_questions": [
                        "How would you secure a serverless application architecture in AWS?",
                        "Explain the difference between symmetric and asymmetric encryption in TLS",
                        "Describe your approach to threat modeling for a web application",
                    ],
                    "scenario_questions": [
                        "Tell me about a time you had to respond to a security incident under pressure",
                        "How do you balance security requirements with business needs?",
                    ],
                    "verification_questions": [
                        "You hold the OSCP - can you explain the buffer overflow exploitation process?",
                        "Walk me through your experience with AWS GuardDuty",
                    ],
                }
            ]
        }
    }
