# cc_agent_sdk Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-27

## Active Technologies

- Python 3.11+ + FastAPI (web framework), Claude Agent SDK Python, pydantic (validation), uvicorn (ASGI server), Claude Code pdf skill (PDF processing), structlog (structured logging), tenacity (retry logic) (001-cv-cybersecurity-analyzer-api)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes

- 001-cv-cybersecurity-analyzer-api: Added Python 3.11+ with FastAPI framework, Claude Agent SDK Python for autonomous CV analysis, pydantic for validation, uvicorn ASGI server, Claude Code pdf skill for PDF processing, structlog for structured JSON logging, tenacity for exponential backoff retry logic. Stateless API architecture with no database persistence.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
