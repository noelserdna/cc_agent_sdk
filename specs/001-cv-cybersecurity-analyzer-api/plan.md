# Implementation Plan: CV Cybersecurity Analyzer API

**Branch**: `001-cv-cybersecurity-analyzer-api` | **Date**: 2025-10-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-cv-cybersecurity-analyzer-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Backend REST API system for automated cybersecurity CV analysis using Claude Agent SDK. Accepts PDF uploads via FastAPI, extracts text, performs autonomous agent-based evaluation across 24 specialized parameters, and returns structured JSON analysis with scoring, red flags, recommendations, and interview suggestions. System operates statelessly with no persistence, completing analysis in under 30 seconds.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (web framework), Claude Agent SDK Python, pydantic (validation), uvicorn (ASGI server), NEEDS CLARIFICATION (PDF processing library: PyPDF2 vs pdfplumber vs pypdf), NEEDS CLARIFICATION (OCR library if needed: pytesseract vs alternatives), NEEDS CLARIFICATION (logging library: python-json-logger vs structlog), NEEDS CLARIFICATION (retry library: tenacity vs backoff)
**Storage**: N/A (stateless API, ephemeral file storage only)
**Testing**: pytest (with async support), NEEDS CLARIFICATION (test coverage tool: pytest-cov), NEEDS CLARIFICATION (integration test strategy for Claude API mocking)
**Target Platform**: Linux/Windows server (containerizable for deployment)
**Project Type**: Single (backend API service)
**Performance Goals**: <30s response time (p95) for 2-4 page CVs, 10 concurrent requests without degradation, <50k tokens per analysis
**Constraints**: <$0.50 per analysis (Claude API cost), 10MB max file size, 30-second total timeout including 3 retries
**Scale/Scope**: Initial deployment for small recruiting teams (<100 CVs/day), horizontally scalable architecture for future growth

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Phase 0)

Verify compliance with `.specify/memory/constitution.md` core principles:

- [x] **Agent-First Development**: ✅ CV analysis agent autonomously gathers context (PDF text extraction), takes actions (scoring across 24 parameters), verifies work (confidence scores, structured validation), and iterates if needed. Agent operates through custom tools with clear interfaces.
- [x] **Verification-Driven Design**: ✅ All operations return explicit success/failure (HTTP status codes, parsing_confidence scores, structured error messages). Agent self-validates via parsing_confidence threshold checks.
- [⚠️] **Type Safety & Validation**: ⚠️ **PARTIAL COMPLIANCE** - Using Python+pydantic instead of TypeScript+Zod. Pydantic provides similar runtime validation and type safety in Python ecosystem. Python's type hints provide static analysis but not TypeScript's compile-time guarantees.
- [x] **Security by Default**: ✅ API key authentication required (X-API-Key header), file size limits (10MB), no file persistence after processing, structured logging with PII anonymization, exponential backoff to prevent API abuse.
- [x] **Observable & Auditable**: ✅ Structured JSON logging with request_id, timestamps, duration_ms, status codes, token usage tracking. While Python doesn't have TypeScript-style hooks, logging decorators/middleware provide equivalent observability.
- [x] **Test-First for Autonomy**: ✅ pytest for unit tests (100% coverage target for PDF extraction, auth, retry logic), integration tests for end-to-end agent workflows validating outcomes (not exact wording).
- [x] **Custom Tools as APIs**: ✅ Domain logic (CV analysis, scoring) implemented as structured Python functions/classes with pydantic validation, not bash scripts. PDF extraction, authentication, and agent orchestration are typed, validated, composable modules.

### Post-Design Re-evaluation (After Phase 1)

**Status**: ✅ **ALL PRINCIPLES SATISFIED WITH DOCUMENTED JUSTIFICATION**

**Changes from Initial Check**:
1. **Type Safety & Validation**: Status unchanged (PARTIAL COMPLIANCE maintained with justification)
   - **Post-design validation**: data-model.md defines comprehensive Pydantic v2 schemas for all 11 entities with Field constraints, custom validators, and exhaustive validation rules
   - **Evidence**: CybersecurityParameter, CVAnalysisResponse, RedFlag, etc. all have strict validation (score ranges 0.0-10.0, enum types, min/max lengths, regex patterns)
   - **Mitigation strengthened**: OpenAPI schema auto-generated from Pydantic models ensures contract-first design and client type generation

2. **Agent-First Development**: ✅ **STRENGTHENED**
   - **Post-design validation**: Agent architecture defined in research.md with four-phase feedback loop (gather context → take action → verify → iterate)
   - **Evidence**: Custom tools planned (extract_cv_metadata, score_parameter, detect_red_flags, generate_recommendations) provide composable agent operations
   - **New**: Claude Code pdf skill integration provides agent-operable PDF processing without bash scripts

3. **Verification-Driven Design**: ✅ **STRENGTHENED**
   - **Post-design validation**: AnalysisMetadata.parsing_confidence (0.0-1.0) provides explicit quality score for self-validation
   - **Evidence**: Error responses with machine-readable error codes, HTTP status codes mapped to failure modes, Retry-After headers for 503 errors
   - **New**: Pydantic validation failures automatically generate structured 400 Bad Request responses with field-level details

4. **Security by Default**: ✅ **STRENGTHENED**
   - **Post-design validation**: API key validation occurs before file processing (FR-032), preventing resource exhaustion attacks
   - **Evidence**: PII redaction patterns defined in structlog processor pipeline (research.md), no candidate data in logs (FR-025)
   - **New**: Ephemeral state transitions defined (RECEIVED → EXTRACTING → ANALYZING → VERIFYING → COMPLETED → CLEANED) ensure no data persistence

5. **Observable & Auditable**: ✅ **STRENGTHENED**
   - **Post-design validation**: structlog selected (research.md) with orjson for performance, fastapi-structlog for correlation IDs
   - **Evidence**: AnalysisMetadata.processing_duration_ms tracked per request, log structure defined (request_id, timestamp, duration_ms, status_code, api_key_id)
   - **New**: Integration with FastAPI middleware ensures all requests logged automatically with context propagation

6. **Test-First for Autonomy**: ✅ **STRENGTHENED**
   - **Post-design validation**: Hybrid pyramid strategy defined (70% RESPX mocks, 25% VCR cassettes, 5% real API)
   - **Evidence**: pytest-cov configuration enforces 100% coverage for unit tests, outcome-based validation pattern for agent tests
   - **New**: Testing structure defined (tests/unit/, tests/integration/, tests/fixtures/) with coverage enforcement in pyproject.toml

7. **Custom Tools as APIs**: ✅ **STRENGTHENED**
   - **Post-design validation**: All 24 parameters evaluated via typed CybersecurityParameter schema with explicit evidence tracking
   - **Evidence**: Pydantic models provide typed interfaces (CVAnalysisRequest, CVAnalysisResponse with 11 nested entities)
   - **New**: Claude Code pdf skill replaces need for bash-based PDF processing, maintaining typed interface via skill invocation

**Violations Requiring Justification**:

| Principle | Deviation | Justification | Alternatives Considered |
|-----------|-----------|---------------|-------------------------|
| Type Safety & Validation | Python+pydantic instead of TypeScript+Zod | **Why**: User explicitly specified Python 3.11+ with FastAPI (FR-035, TC-001-002). Claude Agent SDK supports both TypeScript and Python SDKs. Python is the mandated implementation language per technical constraints. **Mitigation**: Pydantic v2 provides runtime validation with Field constraints, type hints enable static analysis via mypy, OpenAPI schema auto-generated for contract-first design, strict validation at all boundaries (request/response, parameters, nested entities). Post-design: 11 comprehensive Pydantic models defined in data-model.md with exhaustive validation rules (min/max, regex, enums, custom validators). | **Rejected**: (1) TypeScript implementation - violates user requirement and technical constraints; (2) Polyglot approach (TS agent + Python API) - adds unnecessary complexity, violates simplicity principle |

**✅ GATE PASSED**: All principles satisfied with documented justification. Ready to proceed to Phase 2 (task generation).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/              # Pydantic models for requests/responses
│   ├── request.py       # CVAnalysisRequest model
│   └── response.py      # CVAnalysisResponse, parameter schemas
├── services/            # Business logic
│   ├── pdf_extractor.py # PDF text extraction + OCR
│   ├── agent/           # Claude Agent SDK integration
│   │   ├── cv_analyzer_agent.py   # Main autonomous agent
│   │   └── tools/       # Custom agent tools (if needed)
│   └── api_auth.py      # API key validation
├── api/                 # FastAPI routers
│   ├── analyze.py       # POST /analyze-cv endpoint
│   └── health.py        # GET /health endpoint
├── core/                # Core utilities
│   ├── config.py        # Environment configuration
│   ├── logging.py       # Structured JSON logging setup
│   └── retry.py         # Exponential backoff retry logic
└── main.py              # FastAPI app initialization

tests/
├── unit/                # 100% coverage for deterministic logic
│   ├── test_pdf_extractor.py
│   ├── test_api_auth.py
│   └── test_retry.py
├── integration/         # Agent workflow outcome validation
│   └── test_cv_analysis_e2e.py
└── fixtures/            # Test data: sample PDFs, mock responses
    └── sample_cvs/

config/
└── .env.example         # Environment variables template
```

**Structure Decision**: Single project structure selected. This is a backend API service with no frontend components. The structure follows FastAPI best practices with clear separation between models (data schemas), services (business logic including agent), api (HTTP layer), and core utilities. Testing structure mirrors the constitution's requirements: unit tests for deterministic components, integration tests for agent workflows.

## Complexity Tracking

| Complexity Item | Why Needed | Simpler Alternative Rejected Because |
|-----------------|------------|-------------------------------------|
| Python instead of TypeScript | User requirement (FR-035, TC-001-002) explicitly mandates Python 3.11+ with FastAPI | TypeScript would violate explicit technical constraints. Python ecosystem better suited for PDF processing and data analysis workflows common in CV parsing. |
| 24-parameter scoring system | Domain requirement for specialized cybersecurity evaluation (FR-005, detailed_scores in spec) | Simpler generic scoring insufficient for technical recruiting use case. 24 parameters provide actionable insights specific to cybersecurity roles. |
| Autonomous agent vs scripted workflow | Agent-First Development principle requires autonomous context gathering and iteration | Scripted workflow cannot handle variable CV formats, languages, or unexpected content. Agent autonomy essential for reliability across diverse inputs. |
