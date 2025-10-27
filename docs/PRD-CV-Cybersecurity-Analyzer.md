# PRD: Agente de Análisis de CVs de Ciberseguridad con Claude Agent SDK

## 📋 Executive Summary

**Feature Name**: CV Cybersecurity Analyzer Agent API

**Type**: Backend API + Autonomous Agent System

**Owner**: Andre

**Status**: Planning Phase

**Brief Description**:
Sistema de análisis automatizado de CVs de profesionales de ciberseguridad basado en Claude Agent SDK. El agente procesa CVs en formato PDF, extrae información estructurada y genera análisis completos con scoring basado en 24 parámetros de evaluación específicos del sector. Expone funcionalidad vía API REST para integración con sistemas de recursos humanos.

---

## 🎯 Motivation

### Problem Statement

El proceso manual de evaluación de CVs de ciberseguridad consume 30-45 minutos por candidato y carece de consistencia entre evaluadores. Los perfiles técnicos requieren evaluación especializada de certificaciones (OSCP, CISSP, CEH), skills técnicas (pentesting, cloud security, forensics) y experiencia específica del sector que los recruiters generales no pueden valorar adecuadamente.

### Objective

Automatizar la evaluación de CVs de ciberseguridad mediante un agente autónomo que:
1. Extrae información de PDFs automáticamente
2. Analiza perfiles según 24 dimensiones técnicas especializadas
3. Genera scoring objetivo y recomendaciones personalizadas
4. Reduce tiempo de screening de 45 min a <5 min
5. Mejora consistencia entre evaluaciones al 90%+

### Business Value

- **Eficiencia**: Reducción 85% en tiempo de screening inicial
- **Calidad**: Evaluación objetiva basada en criterios técnicos estandarizados
- **Escalabilidad**: Procesar volumen alto de candidatos sin degradación
- **ROI**: 10x retorno en primer año por reducción de tiempo y mejora en quality-of-hire

---

## 📐 Functional Requirements

### User Stories

**US-1: Analizar CV Individual**
```gherkin
Como reclutador técnico
Quiero subir un CV en PDF y recibir análisis completo
Para evaluar objetivamente al candidato sin revisión manual
```

**US-2: Obtener Scoring Detallado**
```gherkin
Como hiring manager
Quiero ver scoring por 24 parámetros técnicos
Para identificar fortalezas y gaps específicos del candidato
```

**US-3: Generar Recomendaciones**
```gherkin
Como talent acquisition
Quiero recibir recomendaciones de certificaciones y desarrollo
Para orientar conversaciones con candidatos
```

**US-4: Identificar Red Flags**
```gherkin
Como responsable de contratación
Quiero detectar automáticamente inconsistencias en CVs
Para realizar preguntas de clarificación en entrevistas
```

### Core Functionality

#### 1. PDF Processing
- Recibir PDFs vía API multipart/form-data
- Extraer texto usando skill de PDF existente
- Manejar diferentes formatos y layouts
- OCR para PDFs escaneados (si disponible en skill)

#### 2. CV Analysis
- Parsing automático usando skill cybersecurity-cv-analyzer
- Extracción de:
  - Certificaciones (regex patterns predefinidos)
  - Años de experiencia (total, por área, por rol)
  - Skills técnicas y herramientas
  - Formación académica
  - Idiomas y soft skills

#### 3. Scoring System
Evaluación en 24 parámetros agrupados:

**Competencias Core (1-12)**:
- Certificaciones, Experiencia, Habilidades Ofensivas/Defensivas
- Gobernanza, Cloud Security, Herramientas, Programming
- Arquitectura, Formación, Soft Skills, Idiomas

**Competencias Especializadas (13-24)**:
- DevSecOps, Forensics, Criptografía, OT/ICS
- Mobile/IoT, Threat Intelligence, Contribuciones
- Publicaciones, Gestión, Crisis, Transformación, Especialidades Nicho

Cada parámetro: puntuación 0-10 con justificación

#### 4. Report Generation
Salida JSON estructurada con:
- Metadata del análisis
- Resumen ejecutivo del candidato
- Scores detallados por parámetro
- Top 5 fortalezas identificadas
- Áreas de mejora prioritarias
- Red flags detectados
- Recomendaciones de desarrollo
- Sugerencias para entrevista técnica
- Comparación vs mercado (percentiles)

### API Endpoints

#### `POST /analyze-cv`

**Request**:
```http
POST /analyze-cv
Content-Type: multipart/form-data

cv_file: [PDF binary]
role_target: "Cloud Security Engineer" (optional)
language: "es" | "en" (optional, default: "es")
```

**Response** (200 OK):
```json
{
  "analysis_metadata": {
    "timestamp": "2025-10-27T10:30:00Z",
    "cv_language": "es",
    "parsing_confidence": 0.95,
    "analysis_version": "1.0"
  },
  "candidate_summary": {
    "name": "John Doe",
    "total_score": 7.5,
    "percentile": 78,
    "detected_role": "Senior Security Engineer",
    "seniority_level": "Senior",
    "years_experience": {
      "total_it": 10,
      "cybersecurity": 6,
      "current_role": 2
    }
  },
  "detailed_scores": {
    "certifications": { "score": 8.0, "details": {...} },
    "offensive_skills": { "score": 7.5, "details": {...} },
    // ... 24 parámetros
  },
  "strengths": [
    {
      "area": "Cloud Security",
      "description": "Strong AWS expertise",
      "score": 8.5,
      "market_value": "high"
    }
  ],
  "improvement_areas": [...],
  "red_flags": [...],
  "recommendations": {...},
  "interview_suggestions": {...}
}
```

**Error Responses**:
- `400 Bad Request`: PDF corrupto, formato no soportado
- `413 Payload Too Large`: PDF >10MB
- `500 Internal Server Error`: Error procesamiento agente

#### `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agent_sdk_version": "X.X.X",
  "uptime_seconds": 3600
}
```

---

## 🔧 Technical Requirements

### Technology Stack

**Backend Framework**: Node.js + TypeScript
- Runtime: Node.js ≥18.x
- Language: TypeScript 5.x
- Framework: Express.js 4.x

**Agent Framework**: Claude Agent SDK
- Package: `@anthropic-ai/claude-agent-sdk`
- Model: `claude-sonnet-4-5` (configurable)
- Skills: PDF extraction + Cybersecurity CV Analyzer

**Dependencies**:
```json
{
  "@anthropic-ai/claude-agent-sdk": "^latest",
  "express": "^4.18.0",
  "multer": "^1.4.5-lts.1",
  "zod": "^3.22.0",
  "dotenv": "^16.0.0"
}
```

### Architecture

```
┌─────────────┐
│   Client    │
│  (HR Tool)  │
└──────┬──────┘
       │ HTTP POST /analyze-cv
       │ (multipart/form-data)
       ▼
┌──────────────────────────────┐
│   Express API Server         │
│   - Multer file upload       │
│   - Input validation         │
│   - Error handling           │
└──────┬───────────────────────┘
       │ Invoke agent
       ▼
┌──────────────────────────────┐
│   Claude Agent SDK           │
│   query("Analiza este CV")  │
└──────┬───────────────────────┘
       │
       ├─────────► Skill: PDF Extraction
       │           - Extract text from PDF
       │           - Handle OCR if needed
       │
       └─────────► Skill: Cybersecurity CV Analyzer
                   - Parse CV structure
                   - Score 24 parameters
                   - Generate recommendations
                   - Detect red flags

       ▼
┌──────────────────────────────┐
│   JSON Response              │
│   - Complete analysis        │
│   - Scoring breakdown        │
│   - Recommendations          │
└──────────────────────────────┘
```

### System Components

#### 1. API Server (`src/server.ts`)
- Express application setup
- Multer middleware for file uploads
- Route handlers
- Error middleware
- Health check endpoint

#### 2. Agent Orchestrator (`src/agent.ts`)
- Claude Agent SDK initialization
- Skills integration (PDF + CV Analyzer)
- Permission mode configuration
- Hooks for logging
- Response streaming handling

#### 3. Type Definitions (`src/types.ts`)
- TypeScript interfaces for API contracts
- CV analysis output types
- Request/response validation schemas (Zod)

#### 4. Skills Directory (`skills/`)
- `cybersecurity-cv-analyzer/` - Unzipped skill
- `pdf/` - PDF extraction skill (si está disponible)

### Configuration

**Environment Variables**:
```bash
ANTHROPIC_API_KEY=sk-ant-...          # Required
PORT=3000                              # Optional, default 3000
MAX_FILE_SIZE_MB=10                    # Optional, default 10
AGENT_MODEL=claude-sonnet-4-5          # Optional
PERMISSION_MODE=bypassPermissions      # Optional, default 'default'
LOG_LEVEL=info                         # Optional, debug|info|warn|error
```

### Data Flow

1. **Request Reception**: Client uploads PDF via POST
2. **File Validation**: Check size, format, readability
3. **Agent Invocation**: `query()` with prompt + PDF path
4. **PDF Extraction**: Agent uses PDF skill to extract text
5. **CV Analysis**: Agent uses cybersecurity-cv-analyzer skill
6. **Response Construction**: Format JSON output
7. **Cleanup**: Delete temporary uploaded file
8. **Response**: Return analysis to client

### Performance Requirements

- **Response Time**: <30 seconds for typical CV (2-4 pages)
- **Throughput**: 10 concurrent requests without degradation
- **File Size**: Support PDFs up to 10MB
- **Availability**: 99% uptime during business hours

### Security Requirements

1. **Input Validation**:
   - Verify uploaded file is valid PDF
   - Sanitize extracted text
   - Limit file size to prevent DoS

2. **API Security**:
   - API key authentication (header: `X-API-Key`)
   - Rate limiting: 100 requests/hour per client
   - CORS configuration for allowed origins

3. **Data Privacy**:
   - Delete uploaded PDFs after processing
   - No persistent storage of candidate data
   - Anonymize logs (no PII in log files)

4. **Claude Agent SDK Security**:
   - Permission mode: `bypassPermissions` (controlled environment)
   - No access to filesystem outside temp directory
   - No network tools beyond skill requirements

---

## ✅ Acceptance Criteria

### AC-1: Successful CV Analysis

```gherkin
Given un CV válido en PDF de un profesional de ciberseguridad
When envío POST /analyze-cv con el archivo
Then recibo respuesta 200 OK
And la respuesta contiene:
  - analysis_metadata con timestamp y confidence
  - candidate_summary con nombre y scores
  - detailed_scores con 24 parámetros evaluados
  - strengths array con al menos 3 fortalezas
  - improvement_areas con recomendaciones
  - interview_suggestions con preguntas técnicas
And el tiempo de respuesta es menor a 30 segundos
```

### AC-2: PDF Extraction Correcta

```gherkin
Given un CV en formato PDF (digitalizado o escaneado)
When el agente procesa el archivo
Then el texto extraído contiene:
  - Nombre del candidato
  - Certificaciones listadas
  - Experiencia laboral
  - Skills técnicas mencionadas
And la confidence de parsing es >= 0.8
```

### AC-3: Scoring de 24 Parámetros

```gherkin
Given un CV analizado exitosamente
When reviso los detailed_scores
Then cada parámetro tiene:
  - score numérico entre 0 y 10
  - details object con justificación
  - evidencia extraída del CV
And la suma ponderada genera total_score correcto
```

### AC-4: Detección de Red Flags

```gherkin
Given un CV con inconsistencias temporales
When el agente analiza el documento
Then el campo red_flags contiene:
  - type: "employment_gap" o "certification_mismatch"
  - severity: "low" | "medium" | "high"
  - description explicativa
  - impact en la evaluación
```

### AC-5: Manejo de Errores

```gherkin
Given un archivo corrupto o formato no-PDF
When envío POST /analyze-cv
Then recibo respuesta 400 Bad Request
And el body contiene:
  - error code específico
  - mensaje descriptivo
  - no crash del servidor
```

### AC-6: Health Check Operativo

```gherkin
Given el servidor está ejecutándose
When envío GET /health
Then recibo respuesta 200 OK en <500ms
And el body indica status "healthy"
```

---

## ⚠️ Risk Assessment

### Technical Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **Claude API Rate Limits** | High | Medium | Implementar queue system, retry logic con exponential backoff |
| **PDF Parsing Failures** | Medium | High | Múltiples estrategias (pdf-parse, fallback a OCR), validación de confidence |
| **Skill Dependencies** | High | Low | Verificar skills incluyen todos los recursos necesarios, tests de integración |
| **Token Context Limits** | Medium | Medium | Prompt optimization, compaction de CV largo antes de análisis |
| **Performance Degradation** | Medium | Medium | Load testing, caching de respuestas para CVs idénticos |

### Business Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| **Sesgo en Evaluación** | High | Low | Auditoría regular de scores, feedback de usuarios, criterios objetivos documentados |
| **Datos Sensibles GDPR** | High | Medium | No almacenar CVs, anonimizar logs, compliance review |
| **Adopción Baja** | Medium | Medium | User training, demo con casos reales, integración con ATS existente |

### Mitigation Actions

1. **Pre-Launch**:
   - Validar skills funcionan correctamente con 10+ CVs reales
   - Load testing con 50 concurrent requests
   - Security audit de manejo de archivos

2. **Launch**:
   - Deploy con rate limiting conservador
   - Monitoring detallado (error rates, latency, API usage)
   - Feedback loop con primeros usuarios

3. **Post-Launch**:
   - Recolectar métricas de accuracy (user feedback)
   - Calibrar scoring basado en casos reales
   - Documentar edge cases encontrados

---

## 📊 Success Metrics

### KPIs (Key Performance Indicators)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Screening Time Reduction** | 85% (45min → 5min) | Promedio tiempo antes/después |
| **Analysis Accuracy** | >80% | User validation: correct/incorrect |
| **API Response Time** | <30s p95 | Server logs, APM monitoring |
| **System Uptime** | 99% | Health check pings |
| **User Satisfaction** | NPS >50 | Post-usage survey |

### Technical Metrics

| Metric | Target | Monitoring |
|--------|--------|-----------|
| **API Error Rate** | <5% | CloudWatch/Datadog |
| **PDF Parsing Success** | >90% | Agent hooks logging |
| **Avg Confidence Score** | >0.85 | Response metadata tracking |
| **Claude API Costs** | <$0.50/CV | API usage billing |
| **Concurrent Capacity** | 10 requests | Load testing |

### Alerting Thresholds

- Error rate >10% in 5min window → Page on-call
- Response time >60s p95 → Warning alert
- API costs >$1/CV → Budget alert
- Health check fails 3x → Critical alert

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1)

**Tasks**:
- [ ] Setup TypeScript project structure
- [ ] Install Claude Agent SDK + dependencies
- [ ] Extract skills to `skills/` directory
- [ ] Create basic Express server skeleton
- [ ] Configure environment variables

**Deliverable**: Runnable "Hello World" API

### Phase 2: Agent Integration (Week 2)

**Tasks**:
- [ ] Implement agent orchestrator (`src/agent.ts`)
- [ ] Integrate PDF skill for text extraction
- [ ] Integrate cybersecurity-cv-analyzer skill
- [ ] Test end-to-end workflow with `Adria_Perez_CV.pdf`
- [ ] Validate JSON output schema

**Deliverable**: Working agent that analyzes test CV

### Phase 3: API Development (Week 2)

**Tasks**:
- [ ] Implement `POST /analyze-cv` endpoint
- [ ] Add Multer file upload handling
- [ ] Input validation with Zod
- [ ] Error handling middleware
- [ ] Implement `GET /health` endpoint

**Deliverable**: Functional API server

### Phase 4: Testing & Refinement (Week 3)

**Tasks**:
- [ ] Unit tests for key functions
- [ ] Integration tests with sample CVs
- [ ] Load testing (10 concurrent)
- [ ] Security review (file handling)
- [ ] Documentation (README, API examples)

**Deliverable**: Production-ready application

### Phase 5: Deployment (Week 3)

**Tasks**:
- [ ] Deploy to staging environment
- [ ] Monitoring setup (logs, metrics)
- [ ] Demo with 5 real CVs
- [ ] Collect initial feedback
- [ ] Production deployment

**Deliverable**: Live API in production

### Timeline Summary

- **Total Duration**: 3 weeks
- **Resources**: 1 developer (full-time)
- **Critical Path**: Agent integration → API development → Testing

---

## 📚 Out of Scope

The following are explicitly **NOT** included in this PRD:

❌ **Endpoint de comparación de múltiples CVs** - Solo análisis individual
❌ **Frontend/UI** - API only, consumida por sistemas externos
❌ **Almacenamiento persistente** - No base de datos de candidatos
❌ **Autenticación compleja** - Solo API key básica
❌ **Webhooks** - No notificaciones asíncronas
❌ **Batch processing** - Procesar 1 CV por request
❌ **Export a PDF/HTML** - Solo respuesta JSON
❌ **Integración directa con ATS** - Cliente hace integración
❌ **Machine Learning personalizado** - Usa criterios predefinidos en skills

---

## 📖 References

### Related Documents

- `prompt_skill_ciber_cv.md` - Spec completa de skill cybersecurity-cv-analyzer
- `.claude/skills/claude-agent-sdk-expert/` - Documentación técnica del SDK
- `.claude/skills/prd-spec-kit/` - Framework de especificación usado

### External Resources

- [Claude Agent SDK Documentation](https://docs.anthropic.com/agent-sdk)
- [Spec-Kit Framework](https://github.com/github/spec-kit)
- [Express.js Documentation](https://expressjs.com/)

---

## 🔄 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-27 | Andre | Initial PRD creation |

---

**Fin del PRD**
