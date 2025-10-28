"""
Scoring models for CV analysis.

This module defines models for cybersecurity parameter scoring and detailed scores.
"""

from pydantic import BaseModel, Field


class CybersecurityParameter(BaseModel):
    """Individual cybersecurity evaluation dimension with score and justification."""

    score: float = Field(
        ..., ge=0.0, le=10.0, description="Numerical score for this parameter (0.0-10.0)"
    )

    justification: str = Field(
        ..., min_length=20, description="Written explanation for the assigned score"
    )

    evidence: list[str] = Field(
        default_factory=list,
        description="Specific CV quotes or paraphrases supporting the score",
    )

    weight: float = Field(
        ...,
        ge=0.5,
        le=1.5,
        description="Parameter weight for total score calculation",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "score": 8.5,
                    "justification": "Strong penetration testing background with 5 years of experience. OSCP and OSCE certifications demonstrate practical offensive skills.",
                    "evidence": [
                        "Led red team engagements for Fortune 500 companies",
                        "OSCP, OSCE, and GXPN certifications",
                        "Developed custom exploit modules for Metasploit",
                    ],
                    "weight": 1.1,
                }
            ]
        }
    }


class DetailedScores(BaseModel):
    """Container for all 24 cybersecurity parameters."""

    # Technical skills (offensive & defensive)
    certifications: CybersecurityParameter = Field(
        ..., description="Professional certifications (OSCP, CISSP, CEH, GIAC, etc.)"
    )

    offensive_skills: CybersecurityParameter = Field(
        ..., description="Penetration testing, red teaming, exploit development"
    )

    defensive_skills: CybersecurityParameter = Field(
        ..., description="SOC operations, incident response, threat hunting"
    )

    governance: CybersecurityParameter = Field(
        ..., description="GRC, compliance, policy development (ISO 27001, NIST, etc.)"
    )

    cloud_security: CybersecurityParameter = Field(
        ..., description="AWS/Azure/GCP security, container security, cloud-native"
    )

    tools: CybersecurityParameter = Field(
        ..., description="Security tools proficiency (Burp, Nessus, Splunk, Wireshark)"
    )

    programming: CybersecurityParameter = Field(
        ..., description="Scripting and development skills (Python, PowerShell, Go)"
    )

    architecture: CybersecurityParameter = Field(
        ..., description="Security architecture and design, threat modeling"
    )

    # Education & soft skills
    education: CybersecurityParameter = Field(
        ..., description="Academic background (degrees, relevant coursework)"
    )

    soft_skills: CybersecurityParameter = Field(
        ..., description="Communication, leadership, teamwork, presentation skills"
    )

    languages: CybersecurityParameter = Field(
        ..., description="Spoken languages (for international roles)"
    )

    # Specialized domains
    devsecops: CybersecurityParameter = Field(
        ..., description="CI/CD security, SAST/DAST, secure software development"
    )

    forensics: CybersecurityParameter = Field(
        ..., description="Digital forensics, malware analysis, reverse engineering"
    )

    cryptography: CybersecurityParameter = Field(
        ..., description="Encryption, PKI, cryptographic protocols"
    )

    ot_ics: CybersecurityParameter = Field(
        ..., description="OT/ICS/SCADA security for industrial environments"
    )

    mobile_iot: CybersecurityParameter = Field(
        ..., description="Mobile app security, IoT security, embedded systems"
    )

    threat_intel: CybersecurityParameter = Field(
        ..., description="Threat intelligence, OSINT, adversary tracking"
    )

    # Professional contributions
    contributions: CybersecurityParameter = Field(
        ..., description="Open source contributions, community involvement"
    )

    publications: CybersecurityParameter = Field(
        ..., description="Research papers, blog posts, conference talks"
    )

    # Leadership & management
    management: CybersecurityParameter = Field(
        ..., description="People management, team leadership, mentoring"
    )

    crisis: CybersecurityParameter = Field(
        ..., description="Crisis management, incident command, business continuity"
    )

    transformation: CybersecurityParameter = Field(
        ..., description="Digital transformation, program management, change leadership"
    )

    # Experience & specialization
    niche_specialties: CybersecurityParameter = Field(
        ..., description="Specialized domains (fintech, healthcare, critical infrastructure)"
    )

    experience: CybersecurityParameter = Field(
        ..., description="Depth and breadth of professional experience"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "certifications": {
                        "score": 9.0,
                        "justification": "Holds OSCP, CISSP, and CEH certifications",
                        "evidence": ["OSCP", "CISSP", "CEH"],
                        "weight": 1.2,
                    },
                    "offensive_skills": {
                        "score": 8.5,
                        "justification": "Extensive pentesting experience",
                        "evidence": ["Red team lead", "Exploit development"],
                        "weight": 1.1,
                    },
                    # ... (other parameters)
                }
            ]
        }
    }
