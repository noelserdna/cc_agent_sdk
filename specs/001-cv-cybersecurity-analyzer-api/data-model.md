# Data Model: CV Cybersecurity Analyzer API

**Date**: 2025-10-27
**Branch**: 001-cv-cybersecurity-analyzer-api

## Overview

This document defines the data model for the CV Cybersecurity Analyzer API. All entities are implemented as Pydantic v2 models for runtime validation and automatic OpenAPI schema generation.

---

## Entity Relationship Diagram

```
CVAnalysisRequest
    │
    ├─> Validates API Key (X-API-Key header)
    └─> Uploads PDF File (multipart/form-data)
         │
         ▼
    CVAnalysisResponse
         ├─> AnalysisMetadata (1:1)
         ├─> CandidateSummary (1:1)
         │    └─> YearsExperience (1:1)
         ├─> DetailedScores (1:1)
         │    └─> CybersecurityParameter (24 instances)
         ├─> Strength (1:5)
         ├─> ImprovementArea (1:N)
         ├─> RedFlag (0:N)
         ├─> Recommendations (1:1)
         └─> InterviewSuggestions (1:1)
```

---

## Core Entities

### 1. CVAnalysisRequest

**Description**: Incoming HTTP request for CV analysis

**Source**: FR-001, FR-002, FR-026, FR-027, FR-031

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `file` | `UploadFile` | Yes | Content-Type: application/pdf, Max size: 10MB (FR-002) | PDF file containing CV |
| `x_api_key` | `str` | Yes | Header validation (FR-031) | Authentication token in X-API-Key header |
| `role_target` | `str \| None` | No | Min length: 3, Max length: 100 | Optional job position for contextualized analysis (FR-026) |
| `language` | `Literal["es", "en"]` | No | Default: "es" | Preferred output language (FR-027) |

**Validation Rules**:
- File must be valid PDF format (FR-004)
- File size must not exceed 10MB (FR-002, FR-003)
- `x_api_key` must match valid API key in system configuration (FR-032)
- `role_target` if provided must not contain special characters (security)
- `language` must be exactly "es" or "en"

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field, validator
from fastapi import UploadFile

class CVAnalysisRequestForm(BaseModel):
    role_target: str | None = Field(
        None,
        min_length=3,
        max_length=100,
        description="Optional target role for contextualized analysis"
    )
    language: Literal["es", "en"] = Field(
        default="es",
        description="Preferred output language for analysis"
    )

    @validator('role_target')
    def validate_role_target(cls, v):
        if v and not v.replace(' ', '').replace('-', '').isalnum():
            raise ValueError("role_target must contain only alphanumeric characters, spaces, and hyphens")
        return v

# File and API key validated separately in FastAPI endpoint
```

---

### 2. CVAnalysisResponse

**Description**: Complete analysis result returned to client

**Source**: FR-018, FR-019, FR-020

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `analysis_metadata` | `AnalysisMetadata` | Yes | Metadata about the analysis process |
| `candidate_summary` | `CandidateSummary` | Yes | High-level candidate profile |
| `detailed_scores` | `DetailedScores` | Yes | Scores across 24 cybersecurity parameters |
| `strengths` | `List[Strength]` | Yes | Top 5 candidate strengths (FR-011) |
| `improvement_areas` | `List[ImprovementArea]` | Yes | Prioritized development opportunities (FR-012) |
| `red_flags` | `List[RedFlag]` | Yes | Detected concerns or inconsistencies (FR-013) |
| `recommendations` | `Recommendations` | Yes | Career development suggestions (FR-015) |
| `interview_suggestions` | `InterviewSuggestions` | Yes | Tailored technical questions (FR-016) |

**Validation Rules**:
- Response must be valid JSON (FR-018)
- Response must be generated within 30 seconds (FR-020)
- All required fields must be present (FR-029)
- `strengths` must contain exactly 5 items (FR-011)
- `improvement_areas` must contain at least 1 item if any score < 7.0

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field

class CVAnalysisResponse(BaseModel):
    analysis_metadata: AnalysisMetadata
    candidate_summary: CandidateSummary
    detailed_scores: DetailedScores
    strengths: List[Strength] = Field(..., min_length=5, max_length=5)
    improvement_areas: List[ImprovementArea] = Field(..., min_length=0)
    red_flags: List[RedFlag] = Field(default_factory=list)
    recommendations: Recommendations
    interview_suggestions: InterviewSuggestions

    class Config:
        json_schema_extra = {
            "example": {
                "analysis_metadata": {...},
                "candidate_summary": {...},
                # ... full example
            }
        }
```

---

### 3. AnalysisMetadata

**Description**: Metadata about the analysis process

**Source**: FR-019, FR-030

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `timestamp` | `datetime` | Yes | ISO 8601 format | Analysis completion timestamp |
| `parsing_confidence` | `float` | Yes | 0.0 ≤ value ≤ 1.0 | Text extraction quality score (FR-030) |
| `cv_language` | `str` | Yes | ISO 639-1 code (2 letters) | Detected CV language |
| `analysis_version` | `str` | Yes | Semantic version format | API version used for analysis |
| `processing_duration_ms` | `int` | Yes | value > 0 | Time taken to complete analysis |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field
from datetime import datetime

class AnalysisMetadata(BaseModel):
    timestamp: datetime = Field(..., description="Analysis completion timestamp in ISO 8601")
    parsing_confidence: float = Field(..., ge=0.0, le=1.0, description="Text extraction quality (0.0-1.0)")
    cv_language: str = Field(..., min_length=2, max_length=2, description="Detected CV language (ISO 639-1)")
    analysis_version: str = Field(..., pattern=r'^\d+\.\d+\.\d+$', description="API version (semver)")
    processing_duration_ms: int = Field(..., gt=0, description="Processing time in milliseconds")
```

---

### 4. CandidateSummary

**Description**: High-level candidate profile

**Source**: FR-008, FR-010, FR-017

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `name` | `str` | Yes | Min length: 2 | Extracted candidate name |
| `total_score` | `float` | Yes | 0.0 ≤ value ≤ 10.0 | Weighted average of 24 parameters (FR-007) |
| `percentile` | `int` | Yes | 0 ≤ value ≤ 100 | Ranking vs market benchmarks (FR-017) |
| `detected_role` | `str` | Yes | Non-empty | Primary specialization (FR-010) |
| `seniority_level` | `Literal["Junior", "Mid", "Senior", "Lead", "Executive"]` | Yes | Enum validation | Career level based on experience |
| `years_experience` | `YearsExperience` | Yes | Nested validation | Experience breakdown (FR-008) |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field
from typing import Literal

class YearsExperience(BaseModel):
    total_it: float = Field(..., ge=0, description="Total years in IT/technology")
    cybersecurity: float = Field(..., ge=0, description="Years specifically in cybersecurity")
    current_role: float = Field(..., ge=0, description="Years in current role")

class CandidateSummary(BaseModel):
    name: str = Field(..., min_length=2)
    total_score: float = Field(..., ge=0.0, le=10.0)
    percentile: int = Field(..., ge=0, le=100)
    detected_role: str = Field(..., min_length=1)
    seniority_level: Literal["Junior", "Mid", "Senior", "Lead", "Executive"]
    years_experience: YearsExperience
```

---

### 5. DetailedScores

**Description**: Container for all 24 cybersecurity parameters

**Source**: FR-005, FR-006

**Fields**: All 24 parameters as `CybersecurityParameter` instances

| Parameter Name | Weight | Description |
|----------------|--------|-------------|
| `certifications` | 1.2x | Professional certifications (OSCP, CISSP, CEH, etc.) |
| `offensive_skills` | 1.1x | Penetration testing, red teaming, exploit development |
| `defensive_skills` | 1.1x | SOC operations, incident response, threat hunting |
| `governance` | 1.0x | GRC, compliance, policy development |
| `cloud_security` | 1.1x | AWS/Azure/GCP security, container security |
| `tools` | 1.0x | Security tools proficiency (Burp, Nessus, Splunk, etc.) |
| `programming` | 1.0x | Scripting and development skills |
| `architecture` | 1.0x | Security architecture and design |
| `education` | 0.9x | Academic background |
| `soft_skills` | 1.0x | Communication, leadership, teamwork |
| `languages` | 0.8x | Spoken languages (for international roles) |
| `devsecops` | 1.0x | CI/CD security, SAST/DAST integration |
| `forensics` | 1.0x | Digital forensics, malware analysis |
| `cryptography` | 1.0x | Encryption, PKI, cryptographic protocols |
| `ot_ics` | 1.0x | OT/ICS/SCADA security |
| `mobile_iot` | 1.0x | Mobile app security, IoT security |
| `threat_intel` | 1.0x | Threat intelligence, OSINT |
| `contributions` | 0.9x | Open source, community involvement |
| `publications` | 0.9x | Research papers, blog posts, talks |
| `management` | 1.0x | People management, team leadership |
| `crisis` | 1.1x | Crisis management, incident command |
| `transformation` | 1.0x | Digital transformation, program management |
| `niche_specialties` | 1.0x | Specialized domains (e.g., fintech security) |
| `experience` | 1.2x | Depth and breadth of experience |

**Pydantic Schema**:
```python
class DetailedScores(BaseModel):
    certifications: CybersecurityParameter
    offensive_skills: CybersecurityParameter
    defensive_skills: CybersecurityParameter
    governance: CybersecurityParameter
    cloud_security: CybersecurityParameter
    tools: CybersecurityParameter
    programming: CybersecurityParameter
    architecture: CybersecurityParameter
    education: CybersecurityParameter
    soft_skills: CybersecurityParameter
    languages: CybersecurityParameter
    devsecops: CybersecurityParameter
    forensics: CybersecurityParameter
    cryptography: CybersecurityParameter
    ot_ics: CybersecurityParameter
    mobile_iot: CybersecurityParameter
    threat_intel: CybersecurityParameter
    contributions: CybersecurityParameter
    publications: CybersecurityParameter
    management: CybersecurityParameter
    crisis: CybersecurityParameter
    transformation: CybersecurityParameter
    niche_specialties: CybersecurityParameter
    experience: CybersecurityParameter
```

---

### 6. CybersecurityParameter

**Description**: Individual evaluation dimension with score and justification

**Source**: FR-005, FR-006

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `score` | `float` | Yes | 0.0 ≤ value ≤ 10.0 | Numerical score (FR-006) |
| `justification` | `str` | Yes | Min length: 20 | Written explanation for score (FR-006) |
| `evidence` | `List[str]` | Yes | Min items: 0 | Specific CV quotes supporting score |
| `weight` | `float` | Yes | 0.5 ≤ value ≤ 1.5 | Parameter weight for total_score calculation |

**Pydantic Schema**:
```python
class CybersecurityParameter(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0)
    justification: str = Field(..., min_length=20)
    evidence: List[str] = Field(default_factory=list)
    weight: float = Field(..., ge=0.5, le=1.5)
```

---

### 7. Strength

**Description**: Identified candidate advantage

**Source**: FR-011

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `area` | `str` | Yes | Non-empty | Strength domain name |
| `description` | `str` | Yes | Min length: 20 | Detailed explanation |
| `score` | `float` | Yes | 7.0 ≤ value ≤ 10.0 | Associated parameter score |
| `market_value` | `Literal["high", "medium", "low"]` | Yes | Enum validation | Market demand assessment |

**Validation Rules**:
- Exactly 5 strengths must be identified (FR-011)
- Strengths must be sorted by score descending
- Score must be ≥ 7.0 (only high-scoring areas are strengths)

**Pydantic Schema**:
```python
class Strength(BaseModel):
    area: str = Field(..., min_length=1)
    description: str = Field(..., min_length=20)
    score: float = Field(..., ge=7.0, le=10.0)
    market_value: Literal["high", "medium", "low"]
```

---

### 8. ImprovementArea

**Description**: Development opportunity with recommendations

**Source**: FR-012

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `area` | `str` | Yes | Non-empty | Parameter needing improvement |
| `current_score` | `float` | Yes | 0.0 ≤ value ≤ 10.0 | Current parameter score |
| `gap_description` | `str` | Yes | Min length: 20 | Explanation of deficiency |
| `recommendations` | `List[str]` | Yes | Min items: 1 | Specific actionable suggestions |
| `priority` | `Literal["high", "medium", "low"]` | Yes | Enum validation | Improvement urgency |

**Validation Rules**:
- At least 3 improvement areas if candidate has 3+ parameters scoring < 4.0 (FR-012)
- Recommendations must be actionable (contain verbs like "obtain", "study", "practice")

**Pydantic Schema**:
```python
class ImprovementArea(BaseModel):
    area: str = Field(..., min_length=1)
    current_score: float = Field(..., ge=0.0, le=10.0)
    gap_description: str = Field(..., min_length=20)
    recommendations: List[str] = Field(..., min_length=1)
    priority: Literal["high", "medium", "low"]
```

---

### 9. RedFlag

**Description**: Detected inconsistency or concern

**Source**: FR-013, FR-014

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `type` | `str` | Yes | Predefined types | Classification (employment_gap, certification_mismatch, etc.) |
| `severity` | `Literal["low", "medium", "high"]` | Yes | Enum validation (FR-014) | Risk level |
| `description` | `str` | Yes | Min length: 20 | Detailed explanation |
| `impact` | `str` | Yes | Min length: 20 | Hiring decision implications |

**Predefined Types**:
- `employment_gap`: Unexplained gaps in work history
- `certification_mismatch`: Claims don't match experience level
- `skill_inconsistency`: Conflicting skill claims
- `frequent_job_changes`: Short tenures indicating instability
- `missing_fundamentals`: Advanced role but lacking basics
- `unclear_progression`: No clear career growth pattern

**Pydantic Schema**:
```python
class RedFlag(BaseModel):
    type: str = Field(..., min_length=1)
    severity: Literal["low", "medium", "high"]
    description: str = Field(..., min_length=20)
    impact: str = Field(..., min_length=20)
```

---

### 10. Recommendations

**Description**: Career development suggestions

**Source**: FR-015

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `certifications` | `List[str]` | Yes | Suggested professional certifications |
| `training` | `List[str]` | Yes | Recommended courses or training programs |
| `experience_areas` | `List[str]` | Yes | Domains to gain hands-on experience |
| `next_role_suggestions` | `List[str]` | Yes | Potential next career moves |

**Pydantic Schema**:
```python
class Recommendations(BaseModel):
    certifications: List[str] = Field(default_factory=list)
    training: List[str] = Field(default_factory=list)
    experience_areas: List[str] = Field(default_factory=list)
    next_role_suggestions: List[str] = Field(default_factory=list)
```

---

### 11. InterviewSuggestions

**Description**: Tailored technical interview questions

**Source**: FR-016

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `technical_questions` | `List[str]` | Yes | Domain-specific technical questions (min 3) |
| `scenario_questions` | `List[str]` | Yes | Situational/behavioral questions (min 2) |
| `verification_questions` | `List[str]` | Yes | Questions to verify specific claims or certs |

**Validation Rules**:
- `technical_questions` must contain at least 3 items
- `scenario_questions` must contain at least 2 items
- Questions must be relevant to detected_role and strengths

**Pydantic Schema**:
```python
class InterviewSuggestions(BaseModel):
    technical_questions: List[str] = Field(..., min_length=3)
    scenario_questions: List[str] = Field(..., min_length=2)
    verification_questions: List[str] = Field(default_factory=list)
```

---

## Validation Summary

### Request Validation (FastAPI Endpoint)
```python
# Validate file size
if file.size > 10 * 1024 * 1024:  # 10MB
    raise HTTPException(status_code=413, detail="File too large")

# Validate PDF format
if not file.content_type == "application/pdf":
    raise HTTPException(status_code=400, detail="File must be PDF")

# Validate API key
if x_api_key not in settings.VALID_API_KEYS:
    raise HTTPException(status_code=401, detail="Invalid API key")
```

### Response Validation (Automatic via Pydantic)
- All score fields: 0.0 ≤ value ≤ 10.0
- All percentile fields: 0 ≤ value ≤ 100
- All confidence scores: 0.0 ≤ value ≤ 1.0
- Strengths list: exactly 5 items
- Technical questions: minimum 3 items
- All datetime fields: ISO 8601 format
- All enum fields: must match Literal types

---

## State Transitions

The CV Analysis Request has no persistent state (stateless API per FR-039), but follows this ephemeral processing flow:

```
1. RECEIVED → File uploaded, API key validated
2. EXTRACTING → PDF text extraction in progress
3. ANALYZING → Agent scoring parameters
4. VERIFYING → Confidence checks, schema validation
5. COMPLETED → Response returned to client
6. CLEANED → Temporary file deleted (FR-021)

Error states:
- INVALID_FILE → 400 Bad Request
- UNAUTHORIZED → 401 Unauthorized
- FILE_TOO_LARGE → 413 Payload Too Large
- PARSING_FAILED → 400 Bad Request (low confidence)
- TIMEOUT → 503 Service Unavailable
- API_ERROR → 503 Service Unavailable
```

---

## Implementation Notes

1. **Pydantic v2**: Use Pydantic v2 for improved performance and better error messages
2. **Field validation**: Use `Field(...)` with constraints for automatic OpenAPI schema generation
3. **Custom validators**: Add `@field_validator` decorators for complex validation logic
4. **JSON schema**: Configure `model_config` with examples for better API docs
5. **Type hints**: Use Python 3.11+ union syntax (`str | None`) for cleaner code

---

## Next Steps

With data model defined:
1. Generate OpenAPI contract in `/contracts/` based on these schemas
2. Implement Pydantic models in `src/models/`
3. Use models for automatic request/response validation in FastAPI
