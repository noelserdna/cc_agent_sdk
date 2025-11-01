# CV Cybersecurity Analyzer API

API automatizada para análisis de CVs de ciberseguridad utilizando Claude Agent SDK.

## Características

- **Análisis técnico de 24 parámetros** en diferentes dominios de ciberseguridad
- **Identificación de fortalezas** (top 5 ventajas del candidato)
- **Detección de red flags** (gaps, inconsistencias, preocupaciones)
- **Recomendaciones de desarrollo profesional** (certificaciones, formación, próximos roles)
- **Sugerencias de preguntas de entrevista** (técnicas, escenarios, verificación)
- **Análisis autónomo** usando Claude Agent SDK con Skills
- **Procesamiento de PDF** con extracción enriquecida de contenido

## Arquitectura

```
┌─────────────────────────────────────────────┐
│          FastAPI REST API                   │
│     (Endpoint: POST /v1/analyze-cv)         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│      CVAnalyzerAgent (Agent SDK)            │
│  - Flujo autónomo en 4 fases                │
│  - Skills: pdf, cybersecurity-cv-analyzer   │
│  - Modelo: claude-haiku-4-5-20251001        │
└─────────────────────────────────────────────┘
```

### Flujo de Análisis Autónomo

El agente sigue un ciclo de 4 fases:
1. **Gather Context**: Extrae y parsea información del CV
2. **Take Action**: Puntúa en 24 parámetros de ciberseguridad
3. **Verify Work**: Verifica confianza y valida esquema
4. **Iterate**: Refina puntuación si es necesario

## Instalación

### Requisitos Previos

- Python 3.11+
- Claude Agent SDK instalado
- Skill `cybersecurity-cv-analyzer` en `~/.claude/skills/`
- API Key de Anthropic (Claude)

### Setup

```bash
# Clonar repositorio
git clone <repository-url>
cd cc_agent_sdk

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### Configuración (.env)

```bash
# API Configuration
ANTHROPIC_API_KEY=your_api_key_here
VALID_API_KEYS=test-api-key-123,production-key-456

# Agent SDK Configuration
CLAUDE_MODEL=claude-haiku-4-5-20251001
CLAUDE_MAX_TOKENS=8192
AGENT_SETTING_SOURCES=["user","project"]
AGENT_ALLOWED_TOOLS=["Skill"]

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
ANALYSIS_TIMEOUT_SECONDS=120
```

## Uso

### Iniciar el servidor

```bash
# Desarrollo con hot-reload
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Producción
cd src
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Health Check

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agent_sdk_version": "1.0.0",
  "uptime_seconds": 3600,
  "environment": "production"
}
```

#### Analizar CV

```bash
curl -X POST http://localhost:8000/v1/analyze-cv \
  -H "X-API-Key: test-api-key-123" \
  -F "file=@cv.pdf" \
  -F "language=es"
```

Parámetros:
- `file`: Archivo PDF del CV (requerido, max 5MB)
- `language`: Idioma del análisis - `es` o `en` (opcional, default: `es`)
- `role_target`: Rol objetivo para contextualizar análisis (opcional)

Respuesta:
```json
{
  "overall_score": 7.5,
  "candidate_summary": {
    "name": "Juan Pérez",
    "main_specialization": "Offensive Security",
    "years_experience": {"min": 5, "max": 7},
    "current_role": "Penetration Tester Senior"
  },
  "detailed_scores": {
    "offensive_security_fundamentals": {
      "score": 8.0,
      "weight": 2.0,
      "justification": "Experiencia demostrada..."
    },
    // ... 23 parámetros más
  },
  "strengths": [
    {
      "title": "Expertise en pentesting",
      "description": "Amplia experiencia...",
      "impact": "high"
    }
    // ... 4 más
  ],
  "red_flags": [],
  "recommendations": {
    "certifications": ["OSCP", "OSWE"],
    "training_courses": ["Advanced Web Exploitation"],
    "experience_areas": ["Cloud Penetration Testing"],
    "next_roles": ["Lead Security Consultant"]
  },
  "interview_suggestions": {
    "technical_questions": ["¿Cómo identificas...?"],
    "scenario_questions": ["Describe un escenario..."],
    "verification_questions": ["¿Puedes explicar...?"]
  },
  "analysis_metadata": {
    "timestamp": "2025-11-01T10:00:00Z",
    "parsing_confidence": 0.95,
    "cv_language": "es",
    "model_used": "claude-haiku-4-5-20251001",
    "processing_duration_ms": 15000
  }
}
```

## Tests

```bash
# Todos los tests
python -m pytest

# Solo tests unitarios
python -m pytest tests/unit/

# Solo tests de integración
python -m pytest tests/integration/

# Con coverage
python -m pytest --cov=src --cov-report=html
```

## Linting

```bash
# Verificar código
cd src && python -m ruff check .

# Corregir automáticamente
cd src && python -m ruff check . --fix
```

## Estructura del Proyecto

```
cc_agent_sdk/
├── src/
│   ├── api/              # Endpoints FastAPI
│   ├── core/             # Configuración, logging, retry
│   ├── models/           # Modelos Pydantic
│   └── services/
│       └── agent/        # CVAnalyzerAgent (Agent SDK)
├── tests/
│   ├── unit/             # Tests unitarios
│   └── integration/      # Tests de integración
├── docs/                 # Documentación adicional
├── static/               # Frontend web (opcional)
└── specs/                # Especificaciones de features
```

## Documentación Adicional

- [PRD - Product Requirements](docs/PRD-CV-Cybersecurity-Analyzer.md)
- [Plan de Migración Agent SDK](docs/PLAN-agent-sdk-skills-migration.md)
- [Guía de Tests](TEST_GUIDE.md)
- [Auditoría de Seguridad](SECURITY_AUDIT.md)

## Tecnologías

- **Python 3.11+**: Lenguaje principal
- **FastAPI**: Framework web
- **Claude Agent SDK**: Análisis autónomo con IA
- **Pydantic**: Validación de datos
- **Structlog**: Logging estructurado JSON
- **Tenacity**: Retry logic con exponential backoff
- **Uvicorn**: Servidor ASGI

## Licencia

Propietario - Todos los derechos reservados

## Contribuciones

Este es un proyecto privado. Para contribuir, contacta al propietario del repositorio.

## Soporte

Para reportar bugs o solicitar features, abre un issue en el repositorio.
