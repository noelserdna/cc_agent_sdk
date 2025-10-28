# Quickstart Guide: CV Cybersecurity Analyzer API

**Date**: 2025-10-27
**Branch**: 001-cv-cybersecurity-analyzer-api
**For**: Developers, DevOps, QA Engineers

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the API](#running-the-api)
5. [Using the API](#using-the-api)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

**System Requirements:**
- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended for concurrent requests)
- 1GB free disk space

**Required Accounts:**
- Anthropic API key (sign up at https://console.anthropic.com/)

**Optional Tools:**
- Docker (for containerized deployment)
- Postman or curl (for API testing)

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd cc_agent_sdk
git checkout 001-cv-cybersecurity-analyzer-api
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected dependencies** (see research.md for rationale):
```txt
# Core framework
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-multipart>=0.0.6  # For file uploads

# Validation & models
pydantic>=2.9.0
pydantic-settings>=2.5.0

# Claude Agent SDK
anthropic>=0.40.0

# PDF processing - using Claude Code pdf skill
# (no additional library needed)

# Logging
structlog>=24.4.0
orjson>=3.10.0  # Performance
fastapi-structlog>=0.5.0

# Retry logic
tenacity>=9.0.0

# Testing
pytest>=8.3.0
pytest-cov>=6.0.0
pytest-asyncio>=0.25.0
httpx>=0.27.0
respx>=0.21.0
pytest-recording>=0.13.0
vcrpy>=7.0.0
```

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
cp config/.env.example .env
```

Edit `.env` with your configuration:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Authentication
API_KEYS=your-api-key-1,your-api-key-2,your-api-key-3

# Claude Agent SDK
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
CLAUDE_MAX_TOKENS=8192

# File Upload
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf

# Retry Configuration
RETRY_MAX_ATTEMPTS=3
RETRY_DELAYS=1,2,4
RETRY_MAX_TOTAL_SECONDS=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_PII_REDACTION=true

# Performance
ANALYSIS_TIMEOUT_SECONDS=30
CONCURRENT_REQUESTS_LIMIT=10
```

### 2. Configuration Validation

Verify your configuration:

```bash
python -m src.core.config --validate
```

---

## Running the API

### Development Mode

```bash
# With auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# With structured logging
uvicorn src.main:app --reload --log-config config/logging.yaml
```

### Production Mode

```bash
# Multi-worker mode
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --log-config config/logging.yaml
```

### Docker

```bash
# Build image
docker build -t cv-analyzer-api:1.0.0 .

# Run container
docker run -d \
  --name cv-analyzer \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env \
  cv-analyzer-api:1.0.0
```

### Verify Server is Running

```bash
curl http://localhost:8000/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agent_sdk_version": "0.40.0",
  "uptime_seconds": 42
}
```

---

## Using the API

### 1. API Documentation

Once the server is running, access interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### 2. Authentication

All `/analyze-cv` requests require an API key in the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/v1/analyze-cv \
  -H "X-API-Key: your-api-key-here" \
  -F "file=@path/to/cv.pdf"
```

### 3. Analyze a CV (Basic)

```bash
curl -X POST http://localhost:8000/v1/analyze-cv \
  -H "X-API-Key: your-api-key-here" \
  -F "file=@candidate_cv.pdf" \
  | jq '.'
```

### 4. Analyze with Target Role (Contextualized)

```bash
curl -X POST http://localhost:8000/v1/analyze-cv \
  -H "X-API-Key: your-api-key-here" \
  -F "file=@candidate_cv.pdf" \
  -F "role_target=Senior Cloud Security Engineer" \
  -F "language=en" \
  | jq '.'
```

### 5. Python Client Example

```python
import httpx
from pathlib import Path

async def analyze_cv(
    api_url: str,
    api_key: str,
    cv_path: Path,
    role_target: str | None = None,
    language: str = "es"
):
    """Analyze a CV using the API"""

    headers = {"X-API-Key": api_key}

    files = {
        "file": (cv_path.name, cv_path.open("rb"), "application/pdf")
    }

    data = {"language": language}
    if role_target:
        data["role_target"] = role_target

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{api_url}/v1/analyze-cv",
            headers=headers,
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()

# Usage
import asyncio

result = asyncio.run(
    analyze_cv(
        api_url="http://localhost:8000",
        api_key="your-api-key-here",
        cv_path=Path("candidate_cv.pdf"),
        role_target="Penetration Tester"
    )
)

print(f"Candidate: {result['candidate_summary']['name']}")
print(f"Total Score: {result['candidate_summary']['total_score']}/10")
print(f"Role: {result['candidate_summary']['detected_role']}")
print(f"Top Strength: {result['strengths'][0]['area']}")
```

### 6. JavaScript/TypeScript Client Example

```typescript
import fs from 'fs';
import FormData from 'form-data';
import fetch from 'node-fetch';

async function analyzeCv(
  apiUrl: string,
  apiKey: string,
  cvPath: string,
  roleTarget?: string,
  language: 'es' | 'en' = 'es'
) {
  const form = new FormData();
  form.append('file', fs.createReadStream(cvPath));
  form.append('language', language);

  if (roleTarget) {
    form.append('role_target', roleTarget);
  }

  const response = await fetch(`${apiUrl}/v1/analyze-cv`, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
      ...form.getHeaders(),
    },
    body: form,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}

// Usage
const result = await analyzeCv(
  'http://localhost:8000',
  'your-api-key-here',
  './candidate_cv.pdf',
  'Cloud Security Architect'
);

console.log(`Candidate: ${result.candidate_summary.name}`);
console.log(`Total Score: ${result.candidate_summary.total_score}/10`);
console.log(`Percentile: ${result.candidate_summary.percentile}th`);
```

---

## Testing

### Run Unit Tests

```bash
# Run all unit tests with coverage
pytest -m unit --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_pdf_extractor.py -v

# Run with coverage enforcement (100%)
pytest -m unit --cov=src --cov-fail-under=100
```

### Run Integration Tests

```bash
# Run integration tests (uses VCR cassettes)
pytest -m integration

# Re-record VCR cassettes (requires real API key)
export ANTHROPIC_API_KEY=your-key
pytest -m integration --record-mode=rewrite
```

### Run End-to-End Tests

```bash
# Run E2E tests with real Claude API
export ANTHROPIC_API_KEY=your-key
pytest -m e2e

# Note: E2E tests consume API credits
```

### Test Coverage Report

```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Manual API Testing with Sample CV

```bash
# Download sample CV (if not provided)
curl -o sample_cv.pdf https://example.com/sample-cybersecurity-cv.pdf

# Test analysis
curl -X POST http://localhost:8000/v1/analyze-cv \
  -H "X-API-Key: test-key" \
  -F "file=@sample_cv.pdf" \
  -o analysis_result.json

# Pretty print result
jq '.' analysis_result.json
```

---

## Deployment

### Docker Compose (Recommended for Production)

```yaml
# docker-compose.yml
version: '3.8'

services:
  cv-analyzer-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_KEYS=${API_KEYS}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/v1/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

```bash
docker-compose up -d
docker-compose logs -f
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cv-analyzer-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cv-analyzer-api
  template:
    metadata:
      labels:
        app: cv-analyzer-api
    spec:
      containers:
      - name: api
        image: cv-analyzer-api:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: cv-analyzer-secrets
              key: anthropic-api-key
        - name: API_KEYS
          valueFrom:
            secretKeyRef:
              name: cv-analyzer-secrets
              key: api-keys
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
          requests:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Environment-Specific Configuration

**Production Checklist:**
- [ ] Set `LOG_LEVEL=INFO` or `WARNING`
- [ ] Enable `LOG_PII_REDACTION=true`
- [ ] Use strong, unique API keys
- [ ] Configure rate limiting (reverse proxy level)
- [ ] Set up monitoring and alerting
- [ ] Configure backup API keys for rotation
- [ ] Enable HTTPS (TLS termination at load balancer)
- [ ] Set resource limits (memory, CPU)
- [ ] Configure log aggregation (ELK, CloudWatch, etc.)

---

## Troubleshooting

### Issue: "Invalid API key" (401 Unauthorized)

**Cause**: API key not configured or incorrect

**Solution**:
```bash
# Verify API_KEYS in .env
cat .env | grep API_KEYS

# Test with correct key
curl -X POST http://localhost:8000/v1/analyze-cv \
  -H "X-API-Key: correct-key-here" \
  -F "file=@cv.pdf"
```

### Issue: "File too large" (413 Payload Too Large)

**Cause**: PDF exceeds 10MB limit

**Solution**:
- Compress PDF using online tools or `ghostscript`:
```bash
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=compressed.pdf input.pdf
```

### Issue: "Low text extraction quality" (400 Bad Request)

**Cause**: Scanned PDF with poor OCR quality

**Solution**:
- Provide a digital PDF instead of scanned document
- Improve scan quality (300 DPI minimum)
- Use OCR preprocessing tools before uploading

### Issue: "Service unavailable" (503)

**Cause**: Claude API rate limited or unavailable

**Solution**:
- Wait for `Retry-After` header duration
- Check Anthropic API status: https://status.anthropic.com/
- Verify ANTHROPIC_API_KEY is valid:
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "test"}]
  }'
```

### Issue: Slow response times (>30s)

**Possible causes and solutions**:

1. **Large CV files**: Compress PDFs or reduce page count
2. **Cold start**: First request after deployment is slower
3. **Low resources**: Increase memory/CPU allocation
4. **High concurrency**: Reduce concurrent requests or scale horizontally

**Debug**:
```bash
# Check processing duration in logs
tail -f logs/api.log | jq 'select(.processing_duration_ms > 30000)'

# Monitor resource usage
docker stats cv-analyzer

# Check Claude API latency in logs
grep "claude_api_duration_ms" logs/api.log
```

### Issue: Tests failing with "VCR cassette not found"

**Solution**:
```bash
# Re-record VCR cassettes
pytest -m integration --record-mode=rewrite

# Or delete cassettes and re-run
rm -rf tests/integration/cassettes/*
pytest -m integration
```

---

## Next Steps

After successfully running the API:

1. **Review API Documentation**: Explore `/docs` for complete endpoint reference
2. **Integrate with HR Systems**: Use client examples to integrate with your recruitment workflow
3. **Customize Analysis**: Modify agent prompts in `src/services/agent/cv_analyzer_agent.py`
4. **Monitor Performance**: Set up logging aggregation and alerting
5. **Scale Deployment**: Configure load balancing for high-volume usage

## Support

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Documentation**: See `/specs/001-cv-cybersecurity-analyzer-api/` for complete design docs
- **API Reference**: http://localhost:8000/docs (when running)

---

**Last Updated**: 2025-10-27
**API Version**: 1.0.0
