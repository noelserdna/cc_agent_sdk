# Feature Specification: CV Cybersecurity Analyzer API

**Feature Branch**: `001-cv-cybersecurity-analyzer-api`
**Created**: 2025-10-27
**Status**: Draft
**Input**: User description: "Backend API system with autonomous agent for analyzing cybersecurity professional CVs using Claude Agent SDK"

## Clarifications

### Session 2025-10-27

- Q: What authentication/authorization mechanism should be used for the /analyze-cv endpoint? → A: API Key in header (X-API-Key)
- Q: What programming language and framework should be used to implement the API? → A: Python + FastAPI
- Q: Should completed CV analysis results be persisted in a database or only returned in HTTP response? → A: No persistir - Solo devolver en respuesta HTTP, sin almacenamiento
- Q: What logging format and level should be used for observability in production? → A: JSON estructurado + niveles estándar (DEBUG/INFO/WARNING/ERROR)
- Q: What retry strategy should be used when Claude API is rate-limited or temporarily unavailable? → A: Exponential backoff con límite (3 reintentos, max 30s total)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit CV for Analysis (Priority: P1)

A technical recruiter needs to quickly evaluate a cybersecurity candidate's CV without spending 30-45 minutes on manual review. They upload the CV PDF through an HR tool that calls the API and receive a comprehensive analysis within seconds.

**Why this priority**: This is the core value proposition - automating the most time-consuming part of CV screening. Without this, the feature has no purpose.

**Independent Test**: Can be fully tested by uploading a sample cybersecurity CV PDF via API endpoint and receiving a complete JSON analysis response with scoring and recommendations. Delivers immediate value by replacing manual screening.

**Acceptance Scenarios**:

1. **Given** a valid cybersecurity professional CV in PDF format (2-4 pages) and valid API key, **When** recruiter uploads file via POST /analyze-cv endpoint with X-API-Key header, **Then** system returns 200 OK with complete analysis including candidate summary, detailed scores for 24 parameters, strengths, improvement areas, and recommendations within 30 seconds
2. **Given** a valid CV file but missing or invalid API key, **When** recruiter attempts upload, **Then** system returns 401 Unauthorized with descriptive error message before processing the file
3. **Given** a PDF file larger than 10MB, **When** recruiter attempts upload, **Then** system returns 413 Payload Too Large error with descriptive message
4. **Given** a corrupted or non-PDF file, **When** recruiter uploads file, **Then** system returns 400 Bad Request with specific error message indicating file format issue
5. **Given** a scanned PDF CV (OCR required), **When** recruiter uploads file, **Then** system extracts text successfully and returns analysis with parsing confidence score >= 0.8

---

### User Story 2 - Review Detailed Scoring Breakdown (Priority: P1)

A hiring manager reviews the detailed scoring across 24 technical parameters to identify specific strengths and gaps in the candidate's profile, enabling data-driven hiring decisions.

**Why this priority**: The 24-parameter scoring system is what differentiates this from generic CV parsing - it provides specialized cybersecurity domain expertise. This is essential for the first viable release.

**Independent Test**: Using the analysis response from User Story 1, verify that all 24 parameters have scores (0-10), justifications, and evidence extracted from the CV. Can be tested by examining the JSON structure and validating completeness.

**Acceptance Scenarios**:

1. **Given** a completed CV analysis, **When** hiring manager examines detailed_scores section, **Then** all 24 parameters (certifications, offensive_skills, defensive_skills, governance, cloud_security, tools, programming, architecture, education, soft_skills, languages, devsecops, forensics, cryptography, ot_ics, mobile_iot, threat_intel, contributions, publications, management, crisis, transformation, niche_specialties, experience) have score values between 0-10 with justification
2. **Given** detailed scores for a parameter, **When** manager reviews the details object, **Then** it contains specific evidence quoted or paraphrased from the CV supporting the score
3. **Given** a candidate with OSCP and CISSP certifications listed in CV, **When** analysis completes, **Then** certifications parameter score reflects these credentials appropriately (>= 7.0) with explicit mention in justification
4. **Given** all individual parameter scores, **When** calculating total_score, **Then** the weighted average produces accurate overall score matching the candidate_summary.total_score field

---

### User Story 3 - Identify Red Flags and Gaps (Priority: P2)

A talent acquisition specialist uses the red flags detection to prepare clarifying questions for interviews, and reviews improvement areas to guide candidate development conversations.

**Why this priority**: Enhances the quality of hiring decisions by surfacing potential concerns automatically. While valuable, the core analysis (P1) is still useful without this.

**Independent Test**: Can be tested independently by analyzing CVs with known issues (employment gaps, certification mismatches, skill inconsistencies) and verifying the red_flags array populates correctly with type, severity, description, and impact fields.

**Acceptance Scenarios**:

1. **Given** a CV with a 2-year employment gap, **When** analysis completes, **Then** red_flags array contains entry with type "employment_gap", severity "medium" or "high", and descriptive explanation
2. **Given** a CV claiming advanced certifications but minimal relevant experience, **When** analysis detects inconsistency, **Then** red_flags includes "certification_mismatch" with impact description
3. **Given** a candidate with 3+ areas scoring below 4.0, **When** reviewing improvement_areas, **Then** at least 3 prioritized recommendations appear with specific development suggestions
4. **Given** detected red flags, **When** talent specialist reviews interview_suggestions, **Then** targeted technical questions related to the flags are provided

---

### User Story 4 - Receive Career Development Recommendations (Priority: P3)

A recruiter or hiring manager uses the recommendations section to provide constructive feedback to candidates, suggesting relevant certifications or skill development areas aligned with their profile.

**Why this priority**: This is a nice-to-have that enhances candidate experience and employer branding, but not critical for the core screening functionality.

**Independent Test**: Can be tested independently by reviewing the recommendations object in the API response for completeness and relevance to the candidate's detected role and experience level.

**Acceptance Scenarios**:

1. **Given** a mid-level candidate (4-6 years experience) with strong offensive skills but low defensive scores, **When** analysis generates recommendations, **Then** suggestions include relevant defensive security certifications (e.g., GIAC, Security+) and training resources
2. **Given** a candidate with detected_role "Cloud Security Engineer" but limited cloud_security score, **When** reviewing recommendations, **Then** cloud-specific certifications (AWS Security Specialty, Azure Security) are suggested
3. **Given** a senior candidate (10+ years) with comprehensive skills, **When** recommendations are generated, **Then** suggestions focus on leadership, architecture certifications, or niche specializations rather than foundational skills

---

### User Story 5 - Monitor System Health (Priority: P2)

DevOps teams and system administrators monitor the API health endpoint to ensure service availability and track operational metrics.

**Why this priority**: Essential for production operations but not part of the core user-facing functionality. Can be added early for operational readiness.

**Independent Test**: Can be tested independently by calling GET /health endpoint and verifying response structure, status codes, and response time requirements.

**Acceptance Scenarios**:

1. **Given** the API server is running normally, **When** monitoring system calls GET /health, **Then** response returns 200 OK with status "healthy", version number, agent_sdk_version, and uptime_seconds within 500ms
2. **Given** the API server is experiencing issues, **When** health check runs, **Then** appropriate error status code (503 Service Unavailable) is returned with diagnostic information
3. **Given** continuous monitoring over 1 hour, **When** health endpoint is polled every 30 seconds, **Then** 99% of requests return successful responses meeting SLA

---

### Edge Cases

- What happens when a CV is in a language other than Spanish or English? System should either process it if Claude can handle the language, or return a specific error indicating unsupported language with parsing_confidence < 0.6.
- How does system handle a CV with no cybersecurity experience (e.g., wrong file uploaded)? Analysis completes but with low overall score (<3.0), most parameters scored 0-2, and a note in candidate_summary indicating limited cybersecurity background.
- What happens when Claude API is rate-limited or unavailable? System implements exponential backoff retry strategy (3 attempts: 1s, 2s, 4s delays) up to 30 seconds total. If all retries fail, returns 503 Service Unavailable with Retry-After header and logs the incident at ERROR level.
- How does system handle extremely long CVs (15+ pages)? System processes the file but may need to truncate or summarize content to fit within Claude's context window, noted in analysis_metadata with a warning about potential information loss.
- What happens when multiple identical CVs are uploaded in quick succession? Each request is processed independently and fully (no caching, no deduplication, no persistent storage to detect duplicates), but system handles concurrency without race conditions or crashes.
- How does system respond when uploaded PDF is password-protected? Returns 400 Bad Request with specific error message indicating the PDF is encrypted and cannot be processed.
- What happens if a CV contains no parseable text (images only, no OCR possible)? Returns 400 Bad Request with error indicating text extraction failed and parsing_confidence of 0.0.
- What happens when API key is missing or invalid? System returns 401 Unauthorized with clear error message before processing the file upload, preventing unauthorized access and resource waste.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept PDF file uploads via HTTP POST endpoint at /analyze-cv using multipart/form-data encoding
- **FR-002**: System MUST support PDF files up to 10MB in size
- **FR-003**: System MUST extract text content from uploaded PDF files, including support for OCR on scanned documents when possible
- **FR-004**: System MUST validate uploaded files are valid PDF format before processing
- **FR-005**: System MUST analyze extracted CV text across 24 predefined cybersecurity evaluation parameters
- **FR-006**: System MUST assign numerical scores (0-10 scale) to each of the 24 parameters with written justification
- **FR-007**: System MUST calculate an overall total_score as weighted average of individual parameter scores
- **FR-008**: System MUST extract candidate metadata including name, total years of experience, cybersecurity-specific experience, and current role duration
- **FR-009**: System MUST identify and list specific certifications mentioned in the CV using pattern matching (e.g., OSCP, CISSP, CEH, GIAC, Security+, etc.)
- **FR-010**: System MUST detect candidate's primary role/specialization (e.g., Penetration Tester, Cloud Security Engineer, SOC Analyst)
- **FR-011**: System MUST identify top 5 candidate strengths with scores, descriptions, and market value assessment
- **FR-012**: System MUST identify areas for improvement with prioritized recommendations
- **FR-013**: System MUST detect red flags including employment gaps, certification mismatches, and skill inconsistencies
- **FR-014**: System MUST classify detected red flags by severity level (low, medium, high)
- **FR-015**: System MUST generate career development recommendations based on candidate's profile and detected gaps
- **FR-016**: System MUST provide suggested technical interview questions tailored to the candidate's background
- **FR-017**: System MUST calculate candidate's percentile ranking compared to market benchmarks (0-100 scale)
- **FR-018**: System MUST return all analysis results as structured JSON response
- **FR-019**: System MUST include analysis metadata with timestamp, parsing confidence score, CV language, and analysis version
- **FR-020**: System MUST complete analysis and return response within 30 seconds for typical CVs (2-4 pages)
- **FR-021**: System MUST delete uploaded PDF files from temporary storage immediately after processing completes and MUST NOT persist analysis results beyond the HTTP response
- **FR-022**: System MUST handle up to 10 concurrent CV analysis requests without performance degradation
- **FR-023**: System MUST provide health check endpoint at GET /health returning service status, version, and uptime
- **FR-024**: System MUST return appropriate HTTP error codes (400, 401, 413, 500, 503) with descriptive error messages for failure scenarios
- **FR-025**: System MUST log analysis requests using structured JSON format with standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) and anonymized data (no personally identifiable information in logs)
- **FR-026**: System MUST support optional role_target parameter to contextualize analysis for specific job positions
- **FR-027**: System MUST support optional language parameter (default "es") to specify preferred output language (Spanish or English)
- **FR-028**: System MUST validate all input parameters and reject malformed requests with 400 Bad Request
- **FR-029**: Users MUST be able to determine if analysis completed successfully by examining HTTP status code and response structure
- **FR-030**: System MUST include parsing_confidence score (0.0-1.0) in metadata to indicate text extraction quality
- **FR-031**: System MUST require valid API key in X-API-Key header for all /analyze-cv requests
- **FR-032**: System MUST return 401 Unauthorized with descriptive error message when API key is missing or invalid
- **FR-033**: System MUST support API key rotation without service interruption
- **FR-034**: System MUST log API key usage for rate limiting and auditing purposes (key identifier only, not full key value)
- **FR-035**: System MUST be implemented using Python 3.11+ with FastAPI framework for REST API endpoints
- **FR-036**: System MUST use Claude Agent SDK (Python) for autonomous agent orchestration and CV analysis logic
- **FR-037**: System MUST use pydantic models for request/response validation and serialization
- **FR-038**: System MUST provide OpenAPI/Swagger documentation at /docs endpoint for API integration testing
- **FR-039**: System MUST operate as stateless API with no database persistence of CV content or analysis results
- **FR-040**: Clients MUST save analysis response if they need to retain results beyond the request-response cycle
- **FR-041**: System MUST include request_id (UUID), timestamp, log_level, endpoint, http_method, status_code, duration_ms, and api_key_id in structured log entries
- **FR-042**: System MUST log INFO level for successful requests, WARNING for parsing issues or degraded performance, and ERROR for failures
- **FR-043**: System MUST include Claude API response times and token usage in DEBUG level logs for cost and performance monitoring
- **FR-044**: System MUST implement exponential backoff retry strategy for Claude API failures with maximum 3 retry attempts
- **FR-045**: System MUST use retry delays of 1 second (first retry), 2 seconds (second retry), and 4 seconds (third retry) for exponential backoff
- **FR-046**: System MUST limit total retry duration to fit within the 30-second response time SLA
- **FR-047**: System MUST return 503 Service Unavailable with Retry-After header when all Claude API retry attempts are exhausted
- **FR-048**: System MUST log each retry attempt at WARNING level with attempt number, delay used, and error details

### Technical Constraints

- **TC-001**: Implementation language is Python 3.11 or higher
- **TC-002**: Web framework is FastAPI with uvicorn ASGI server
- **TC-003**: Claude Agent SDK (Python) must be used for agent orchestration
- **TC-004**: PDF processing must use Python libraries (e.g., PyPDF2, pdfplumber, or pypdf) with OCR support via pytesseract if needed
- **TC-005**: Async/await patterns must be used for I/O operations (file uploads, Claude API calls) to support concurrent request handling
- **TC-006**: No database or persistent storage is required; system operates as stateless service with ephemeral file storage only
- **TC-007**: Structured logging must use Python's logging module with JSON formatter (e.g., python-json-logger or structlog) for machine-readable output
- **TC-008**: Retry logic should use libraries like tenacity or backoff for robust exponential backoff implementation with Claude API calls

### Key Entities

- **CV Analysis Request**: Represents an incoming analysis request containing PDF file, X-API-Key header for authentication, optional role_target string, and optional language preference ("es" or "en")
- **CV Analysis Response**: Structured output containing analysis_metadata (timestamp, confidence, language, version), candidate_summary (name, scores, role, experience), detailed_scores (24 parameters with scores and justifications), strengths array, improvement_areas array, red_flags array, recommendations object, and interview_suggestions object
- **Cybersecurity Parameter**: One of 24 evaluation dimensions (certifications, offensive_skills, defensive_skills, governance, cloud_security, tools, programming, architecture, education, soft_skills, languages, devsecops, forensics, cryptography, ot_ics, mobile_iot, threat_intel, contributions, publications, management, crisis, transformation, niche_specialties, experience) with score, details, and evidence
- **Red Flag**: Detected inconsistency or concern with type classification (employment_gap, certification_mismatch, skill_inconsistency, etc.), severity level (low/medium/high), description, and impact statement
- **Strength**: Identified candidate advantage with area name, description, numerical score, and market_value assessment (high/medium/low)
- **Improvement Area**: Development opportunity with area name, current gap description, and specific recommendations
- **Candidate Summary**: High-level profile including extracted name, total_score, percentile ranking, detected_role, seniority_level, and years_experience breakdown (total_it, cybersecurity, current_role)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: CV screening time is reduced from 30-45 minutes manual review to under 5 minutes total (including upload, analysis wait time, and review of results) - target 85% reduction
- **SC-002**: System completes analysis and returns response within 30 seconds for 95th percentile of requests (CVs up to 4 pages)
- **SC-003**: System successfully processes at least 90% of uploaded valid PDF files with parsing confidence >= 0.8
- **SC-004**: Analysis accuracy (as validated by technical recruiters) achieves 80% agreement rate on scoring appropriateness and recommendations relevance
- **SC-005**: System handles 10 concurrent analysis requests without response time degradation beyond 10%
- **SC-006**: Health check endpoint responds within 500 milliseconds for 99% of requests
- **SC-007**: Zero candidate personally identifiable information (PII) appears in system logs when reviewed
- **SC-008**: System achieves 99% uptime during business hours (measured over 1-month period)
- **SC-009**: Recruiters report Net Promoter Score (NPS) above 50 based on post-usage survey
- **SC-010**: Support tickets related to manual CV screening errors decrease by 50% after system adoption
- **SC-011**: All 24 cybersecurity parameters receive scores and justifications for 100% of successfully analyzed CVs
- **SC-012**: Red flag detection identifies at least 80% of known CV inconsistencies when tested against validation dataset
- **SC-013**: System costs per CV analysis remain below $0.50 in API usage fees
- **SC-014**: Interview questions generated are rated as "relevant and useful" by hiring managers in 90% of cases
