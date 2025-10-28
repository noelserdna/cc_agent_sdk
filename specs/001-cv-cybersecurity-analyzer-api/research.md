# Research: CV Cybersecurity Analyzer API

**Date**: 2025-10-27
**Branch**: 001-cv-cybersecurity-analyzer-api

## Executive Summary

This document consolidates research findings for technical decisions marked as NEEDS CLARIFICATION in the Technical Context. All decisions prioritize production-readiness, Python ecosystem best practices, and alignment with the Agent-First Development constitution.

---

## Decision 1: PDF Processing

**Decision**: Use Claude Code's **pdf skill** (managed skill)

**Rationale**:
- Claude Code provides a production-ready pdf skill specifically designed for comprehensive PDF manipulation including text extraction, table extraction, and form handling
- Eliminates need for manual library selection and maintenance
- Provides consistent API across different PDF processing tasks
- Skill is managed and tested by Claude team, reducing maintenance burden
- Integrates seamlessly with the agent-first workflow

**Alternatives Considered**:
- **pypdf (rejected)**: Would require manual integration, lacks table extraction capabilities needed for potential future enhancements, manual OCR integration required
- **pdfplumber (rejected)**: Slower performance (2.7x slower than pypdf), overkill for CV text extraction
- **PyPDF2 (rejected)**: Deprecated since December 2022, no longer maintained

**Implementation**: Agent will invoke the pdf skill directly for CV text extraction tasks.

---

## Decision 2: OCR Strategy

**Decision**: **Leverage pdf skill's built-in capabilities** + conditional fallback

**Rationale**:
- The pdf skill handles both digital PDFs and can work with text extraction from scanned documents
- For scanned CVs, rely on the pdf skill's text extraction capabilities first
- If parsing_confidence < 0.6, return explicit error to client indicating OCR quality issues
- Keeps implementation simple and delegates complexity to managed skill

**Alternatives Considered**:
- **pytesseract + pdf2image (rejected)**: Adds external system dependencies (Tesseract OCR, Ghostscript, poppler), increases deployment complexity, requires manual installation on Windows/Linux
- **OCRmyPDF (rejected)**: Heavyweight solution requiring Ghostscript + Tesseract 4.1.1+, unnecessary for simple text extraction

**Implementation**:
```python
# Use pdf skill for extraction
text = await invoke_pdf_skill("extract_text", cv_file)
confidence = calculate_parsing_confidence(text)

if confidence < 0.6:
    return {
        "error": "Low text extraction quality",
        "parsing_confidence": confidence,
        "suggestion": "Please provide a digital PDF or higher quality scan"
    }
```

---

## Decision 3: Structured Logging

**Decision**: **structlog**

**Rationale**:
- Industry standard for production FastAPI applications (4,092 GitHub stars vs 156 for python-json-logger)
- Superior performance with orjson integration (fastest JSON serializer)
- Mature FastAPI integration ecosystem via `fastapi-structlog` package
- Built-in correlation ID support via `StructlogMiddleware`
- Context variables for request-scoped logging (automatic propagation)
- Powerful processor pipeline for PII redaction
- Active development: Python 3.14 compatible, latest release October 27, 2025

**Alternatives Considered**:
- **python-json-logger (rejected)**: Smaller community (26x fewer stars), no built-in FastAPI middleware, manual correlation ID implementation, limited PII redaction support, no performance optimizations

**Implementation**:
```python
# Install: structlog, orjson, fastapi-structlog
# Configure once in main.py with processors for PII redaction
# Use StructlogMiddleware for automatic request context
```

---

## Decision 4: Retry Logic

**Decision**: **tenacity**

**Rationale**:
- More flexible configuration for complex retry scenarios
- Excellent async/await support (required for FastAPI)
- Can combine multiple retry/stop conditions elegantly
- Better integration with structured logging
- Widely adopted in production Python services
- Explicit timeout control with `stop_after_delay`

**Alternatives Considered**:
- **backoff (rejected)**: Simpler API but less flexible for complex scenarios like "3 retries with specific delays AND max 30s total timeout", decorator-based approach less flexible for dynamic configuration

**Implementation**:
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    stop_after_delay,
    retry_if_exception_type
)

@retry(
    stop=(stop_after_attempt(3) | stop_after_delay(30)),
    wait=wait_fixed(1) + wait_fixed(1) + wait_fixed(2),  # 1s, 2s, 4s
    retry=retry_if_exception_type(APIError),
    before_sleep=log_retry_attempt,
)
async def call_claude_api(prompt: str):
    # Claude API call here
    pass
```

---

## Decision 5: Testing Strategy

**Decision**: **Hybrid Pyramid Testing** with pytest-cov + RESPX + VCR.py

**Rationale**:
- Balances speed, cost, and reliability across test pyramid levels
- pytest-cov provides 100% coverage enforcement with async support
- RESPX for fast, deterministic unit tests (70% of tests)
- VCR.py for realistic integration tests with recorded responses (25% of tests)
- Real API calls reserved for pre-release validation (5% of tests)
- Outcome-based validation for agent tests (not exact wording)

**Testing Layers**:

1. **Unit Tests (70%)**: RESPX mocks
   - Fast, deterministic
   - 100% coverage enforced
   - Test PDF extraction, auth, retry logic in isolation

2. **Integration Tests (25%)**: VCR.py cassettes
   - Real Claude responses recorded once
   - Balance of realism and speed
   - Run on every PR

3. **E2E Tests (5%)**: Real API calls
   - Manual or pre-release only
   - Full validation with live Claude API
   - Controlled by environment flag

**Agent Outcome Validation Pattern**:
```python
# Validate OUTCOMES, not exact text
assert agent_response["detected_role"] in ["Penetration Tester", "Security Analyst"]
assert agent_response["parsing_confidence"] >= 0.8
assert "offensive_skills" in agent_response["detailed_scores"]
assert len(agent_response["strengths"]) >= 3

# NOT: assert agent_response["summary"] == "exact expected text"
```

**Alternatives Considered**:
- **Coverage.py directly (rejected)**: pytest-cov provides better integration with pytest-asyncio and multiprocessing
- **Only real API calls (rejected)**: Too slow and costly for CI/CD
- **Only mocks (rejected)**: Doesn't catch real API integration issues
- **DeepEval/LangSmith (deferred)**: Useful for advanced semantic validation but adds complexity; can be added later if needed

**Configuration**:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = ["--cov=src", "--cov-fail-under=100", "-m", "unit"]
markers = ["unit", "integration", "e2e"]

[tool.coverage.report]
fail_under = 100
```

---

## Decision 6: Claude Agent SDK Integration

**Decision**: **Use Claude Agent SDK Python** with custom tools pattern

**Rationale**:
- Agent SDK provides the four-phase feedback loop (gather context, take action, verify, iterate)
- Python SDK available alongside TypeScript version
- Custom tools provide typed, validated, composable interfaces for CV analysis
- Agent autonomy handles variable CV formats without scripted workflows
- Hooks equivalent via middleware/decorators for observability

**Architecture Pattern**:
```python
# src/services/agent/cv_analyzer_agent.py
from anthropic import AsyncAnthropic

class CVAnalyzerAgent:
    """Autonomous agent for CV analysis using Claude Agent SDK"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def analyze_cv(self, cv_text: str, role_target: Optional[str]) -> CVAnalysisResponse:
        """
        Four-phase agent loop:
        1. Gather Context: Parse CV, extract metadata
        2. Take Action: Score across 24 parameters
        3. Verify Work: Check parsing_confidence, validate schema
        4. Iterate: Refine scoring if needed
        """
        # Agent implementation with custom tools
        pass
```

**Custom Tools to Implement**:
- `extract_cv_metadata`: Parse name, experience, role from CV text
- `score_parameter`: Score a single cybersecurity parameter with justification
- `detect_red_flags`: Identify gaps, mismatches, inconsistencies
- `generate_recommendations`: Create career development suggestions

**Alternatives Considered**:
- **Direct Claude API calls (rejected)**: Loses agent autonomy and feedback loop capabilities
- **LangChain (rejected)**: Heavier framework, less aligned with Agent-First Development principles
- **Custom agent implementation (rejected)**: Reinventing the wheel, Claude Agent SDK provides production-tested patterns

---

## Summary Table

| Component | Decision | Primary Reason |
|-----------|----------|----------------|
| PDF Processing | Claude Code pdf skill | Managed, production-ready, comprehensive capabilities |
| OCR Strategy | pdf skill + confidence threshold | Simplicity, delegates complexity to managed skill |
| Structured Logging | structlog | Best-in-class performance, FastAPI ecosystem, active maintenance |
| Retry Logic | tenacity | Flexible async support, complex condition composition |
| Test Coverage | pytest-cov | Native pytest integration, 100% enforcement, async support |
| Test Strategy | Hybrid Pyramid (RESPX/VCR/Real) | Balance of speed, cost, reliability |
| Agent Framework | Claude Agent SDK Python | Agent-first design, feedback loops, production patterns |

---

## Next Steps (Phase 1)

With research complete, proceed to Phase 1:
1. Generate data-model.md with 24 parameter definitions
2. Create OpenAPI contract in /contracts/
3. Generate quickstart.md
4. Update agent context file

All NEEDS CLARIFICATION items are now resolved.
