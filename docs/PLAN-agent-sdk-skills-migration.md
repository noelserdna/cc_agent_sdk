# Plan de Migración a Agent SDK con Skills

**Fecha:** 2025-11-01
**Objetivo:** Refactorizar el proyecto para usar el Claude Agent SDK con Skills, eliminando código custom y usando un enfoque modular basado en Skills.

## Contexto

El proyecto actualmente usa `AsyncAnthropic` directamente para llamar a la API de Claude, con código custom para extracción de PDF (pdfplumber) y prompts monolíticos para análisis de CVs.

La migración a Skills permitirá:
- Código más limpio y modular
- Skills reutilizables entre proyectos
- Mantenimiento simplificado (cambios en Skills, no en código)
- Separación de concerns clara

## Arquitectura Final

```
┌─────────────────────────────────────────────┐
│          FastAPI REST API                   │
│     (Endpoint: POST /v1/analyze-cv)         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│      CVAnalyzerAgent (Agent SDK)            │
│  - setting_sources: ["user", "project"]     │
│  - allowed_tools: ["Skill"]                 │
│  - Flujo guiado en 2 steps                  │
└─────────────────┬───────────────────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
┌──────────────┐    ┌────────────────────────┐
│  Skill: pdf  │    │ Skill: cybersecurity-  │
│  (extracción)│    │ cv-analyzer (análisis) │
└──────────────┘    └────────────────────────┘
```

### Componentes

1. **API REST FastAPI** (se mantiene)
   - Endpoint `/v1/analyze-cv`
   - Interfaz HTTP tradicional
   - Internamente usa Agent SDK

2. **Servicio Agent SDK** (nuevo)
   - Implementación standalone: `standalone_agent.py`
   - Puede usarse sin FastAPI
   - Para integraciones directas

3. **Skills utilizadas**
   - `pdf`: Extracción de contenido PDF (reemplaza pdfplumber)
   - `cybersecurity-cv-analyzer`: Análisis especializado de CVs (existe en `~/.claude/skills/`)

4. **Flujo guiado**
   - Step 1: Invocar skill `pdf` para extracción
   - Step 2: Invocar skill `cybersecurity-cv-analyzer` para análisis
   - No totalmente autónomo, secuencia controlada

## Cambios Detallados

### 1. Actualizar `src/core/config.py`

**Añadir nuevos parámetros:**

```python
# Agent SDK Configuration
agent_setting_sources: list[str] = Field(
    default=["user", "project"],
    description="Sources for loading Agent SDK settings and skills"
)
agent_allowed_tools: list[str] = Field(
    default=["Skill"],
    description="Tools allowed for the Agent SDK"
)
agent_cwd: str = Field(
    default=".",
    description="Working directory for Agent SDK"
)
```

### 2. Refactorizar `src/services/agent/cv_analyzer_agent.py`

**Cambios principales:**

- **Remover:** Import de `AsyncAnthropic`
- **Añadir:** Import de `query` y `ClaudeAgentOptions` del SDK
- **Reemplazar:** Llamada directa a API por uso del Agent SDK
- **Implementar:** Flujo guiado en 2 pasos

**Código objetivo:**

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async def analyze_cv(self, pdf_path: str, language: str = "es") -> CVAnalysisResponse:
    """
    Analiza un CV usando Agent SDK con Skills.

    Flujo:
    1. Skill 'pdf' extrae contenido del PDF
    2. Skill 'cybersecurity-cv-analyzer' analiza el contenido
    """

    options = ClaudeAgentOptions(
        cwd=self.config.agent_cwd,
        setting_sources=self.config.agent_setting_sources,
        allowed_tools=self.config.agent_allowed_tools,
        model=self.config.claude_model,
        max_tokens=self.config.claude_max_tokens
    )

    # Prompt guiado para el flujo de 2 steps
    prompt = f"""
    Analiza este CV de ciberseguridad usando el siguiente flujo:

    1. Usa la skill 'pdf' para extraer el contenido del archivo: {pdf_path}
    2. Usa la skill 'cybersecurity-cv-analyzer' para analizar el contenido extraído

    Idioma del análisis: {language}

    Retorna el análisis completo en formato JSON estructurado.
    """

    response_text = ""
    async for message in query(prompt=prompt, options=options):
        response_text += message

    # Parse y validar respuesta JSON
    analysis = self._parse_response(response_text)
    return analysis
```

### 3. Eliminar `src/services/pdf_extractor.py`

**Acción:** Borrar el archivo completo

**Razón:** La skill `pdf` reemplaza toda la funcionalidad de pdfplumber

**Archivos afectados:**
- Remover import en `src/api/analyze.py`
- Remover import en `cv_analyzer_agent.py`
- Actualizar tests que usen `invoke_pdf_skill()`

### 4. Actualizar `src/api/analyze.py`

**Cambios:**

```python
# ANTES
from src.services.pdf_extractor import invoke_pdf_skill

@router.post("/v1/analyze-cv")
async def analyze_cv(file: UploadFile, language: str = "es"):
    # Guardar PDF temporalmente
    pdf_path = save_temp_file(file)

    # Extraer contenido con pdfplumber
    pdf_content = await invoke_pdf_skill(pdf_path)

    # Analizar con agente
    result = await agent.analyze_cv(pdf_content, language)

    return result

# DESPUÉS
@router.post("/v1/analyze-cv")
async def analyze_cv(file: UploadFile, language: str = "es"):
    # Guardar PDF temporalmente
    pdf_path = save_temp_file(file)

    # El agente internamente usa la skill 'pdf' para extracción
    result = await agent.analyze_cv(pdf_path, language)

    return result
```

### 5. Crear `src/services/agent/standalone_agent.py`

**Propósito:** Servicio standalone del Agent SDK sin dependencias de FastAPI

```python
"""
Servicio standalone del Agent SDK.
Puede usarse sin FastAPI para integraciones directas.
"""

from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions
from src.models.response import CVAnalysisResponse
from src.core.config import Settings

async def analyze_cv_with_agent(
    pdf_path: str | Path,
    language: str = "es",
    config: Settings | None = None
) -> CVAnalysisResponse:
    """
    Analiza un CV usando Agent SDK con Skills.

    Args:
        pdf_path: Ruta al archivo PDF del CV
        language: Idioma del análisis ('es' o 'en')
        config: Configuración opcional (usa default si no se proporciona)

    Returns:
        CVAnalysisResponse con el análisis completo

    Example:
        >>> result = await analyze_cv_with_agent("cv.pdf", language="es")
        >>> print(result.overall_score)
        7.5
    """
    if config is None:
        config = Settings()

    options = ClaudeAgentOptions(
        cwd=config.agent_cwd,
        setting_sources=config.agent_setting_sources,
        allowed_tools=config.agent_allowed_tools,
        model=config.claude_model,
        max_tokens=config.claude_max_tokens
    )

    prompt = f"""
    Analiza este CV de ciberseguridad usando el siguiente flujo:

    1. Usa la skill 'pdf' para extraer el contenido del archivo: {pdf_path}
    2. Usa la skill 'cybersecurity-cv-analyzer' para analizar el contenido extraído

    Idioma del análisis: {language}
    """

    response_text = ""
    async for message in query(prompt=prompt, options=options):
        response_text += message

    # Parse y validar respuesta
    # TODO: Implementar parsing y validación

    return response_text
```

### 6. Actualizar dependencias

**requirements.txt / pyproject.toml:**

```toml
# Añadir
claude-agent-sdk = "^1.0.0"  # Verificar versión actual

# Mantener
anthropic = "^0.40.0"
pydantic = "^2.0.0"
fastapi = "^0.115.0"
uvicorn = "^0.32.0"

# Remover (ahora en skill)
# pdfplumber = "^0.11.0"  # Ya no es necesario aquí
```

**Nota:** `pdfplumber` ahora es dependencia de la skill `pdf`, no del proyecto principal.

### 7. Actualizar tests

**tests/unit/test_cv_analyzer_agent.py:**

```python
# ANTES: Mock pdfplumber
@patch('src.services.pdf_extractor.pdfplumber')
async def test_analyze_cv(mock_pdfplumber):
    mock_pdfplumber.open.return_value = ...
    result = await agent.analyze_cv(pdf_content, "es")
    assert result.overall_score > 0

# DESPUÉS: Mock Agent SDK query
@patch('src.services.agent.cv_analyzer_agent.query')
async def test_analyze_cv(mock_query):
    mock_query.return_value = AsyncMock()
    result = await agent.analyze_cv("cv.pdf", "es")

    # Verificar que se invocó con las skills correctas
    call_args = mock_query.call_args
    assert "skill 'pdf'" in call_args.kwargs['prompt'].lower()
    assert "cybersecurity-cv-analyzer" in call_args.kwargs['prompt'].lower()
    assert result.overall_score > 0
```

**Nuevos tests:**

- `test_standalone_agent.py`: Tests para el servicio standalone
- `test_agent_skills_integration.py`: Tests de integración end-to-end

### 8. Documentación

**Actualizar/crear:**

- `README.md`: Explicar nueva arquitectura con Skills
- `docs/ARCHITECTURE.md`: Diagrama de componentes actualizado
- `docs/SKILLS.md`: Cómo funcionan las Skills en el proyecto
- `docs/STANDALONE_USAGE.md`: Cómo usar el agente sin FastAPI

## Orden de Ejecución

```
1. ✓ Crear este documento de plan
2. □ Actualizar src/core/config.py (agent_setting_sources, agent_allowed_tools)
3. □ Refactorizar src/services/agent/cv_analyzer_agent.py
   - Importar claude_agent_sdk
   - Implementar flujo guiado con Skills
   - Remover AsyncAnthropic directo
4. □ Eliminar src/services/pdf_extractor.py
5. □ Actualizar src/api/analyze.py (remover pdf_extractor)
6. □ Crear src/services/agent/standalone_agent.py
7. □ Actualizar requirements.txt / pyproject.toml
8. □ Actualizar tests
   - test_cv_analyzer_agent.py
   - Crear test_standalone_agent.py
   - Crear test_agent_skills_integration.py
9. □ Ejecutar tests: pytest tests/ -v
10. □ Validar API con curl/Postman
11. □ Actualizar documentación (README, ARCHITECTURE, SKILLS)
12. □ Commit: "refactor: Migrate to Agent SDK with Skills architecture"
```

## Beneficios de la Migración

### ✅ Modularidad
- Skills reutilizables entre proyectos
- Separación clara de concerns (extracción vs análisis)
- Cambios en Skills no requieren redeployar el código

### ✅ Mantenimiento
- Menos código custom a mantener
- Skills se actualizan independientemente
- Bugs y mejoras centralizados en Skills

### ✅ Flexibilidad
- Dos formas de uso: API REST o standalone
- Fácil añadir nuevas Skills sin cambiar código
- Configuración centralizada en Settings

### ✅ Código Limpio
- Elimina ~200 líneas de código de pdfplumber
- Prompts y lógica de análisis en Skills, no en código
- Arquitectura más clara y comprensible

## Impacto y Consideraciones

### ⚠️ Breaking Changes Mínimos
- La API REST mantiene la misma interfaz HTTP
- Response JSON mantiene la misma estructura
- Clientes externos no se ven afectados

### ⚠️ Requisitos Previos
- Skill `cybersecurity-cv-analyzer` debe existir en `~/.claude/skills/`
- Skill `pdf` debe estar disponible (viene con Claude Code)
- Claude Agent SDK debe estar instalado

### ⚠️ Cambios Internos Significativos
- El flujo de procesamiento cambia completamente
- Tests necesitan adaptarse al nuevo enfoque
- Debugging puede ser diferente (logs del Agent SDK)

## Validación Post-Migración

### Tests Funcionales
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# End-to-end test con API
curl -X POST http://localhost:8000/v1/analyze-cv \
  -H "X-API-Key: test-key" \
  -F "file=@sample_cv.pdf" \
  -F "language=es"
```

### Verificación de Skills
```python
# Verificar que las skills están disponibles
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    setting_sources=["user", "project"],
    allowed_tools=["Skill"]
)

async for msg in query("What Skills are available?", options=options):
    print(msg)

# Debe mostrar:
# - pdf
# - cybersecurity-cv-analyzer
```

### Métricas de Calidad
- ✓ Reducción de líneas de código: ~20%
- ✓ Cobertura de tests mantenida: >80%
- ✓ Tiempo de respuesta API: similar o mejor
- ✓ Calidad de análisis: igual o superior

## Referencias

- [Agent Skills in the SDK](https://docs.anthropic.com/en/api/agent-sdk/skills)
- [Claude Agent SDK Overview](https://docs.anthropic.com/en/api/agent-sdk/overview)
- [Agent Skills Best Practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices)

---

**Estado:** ⏳ Pendiente de ejecución
**Próximo paso:** Actualizar `src/core/config.py` con parámetros del Agent SDK
