# Plan: Migración a Skill de PDF con Extracción Enriquecida

**Fecha:** 2025-11-01
**Versión:** 1.0
**Estado:** Planificación

---

## Resumen Ejecutivo

Migrar el código actual de procesamiento PDF desde `pypdf` básico hacia una implementación enriquecida usando las capacidades completas de la **skill de PDF**, extrayendo texto, tablas, metadata, imágenes, y URLs, delegando la validación de calidad al agente de Claude en lugar de usar un threshold rígido.

### Motivación

**Situación Actual:**
- El código comenta sobre usar "Claude Code pdf skill" pero implementa manualmente con `pypdf`
- Solo extrae texto plano, sin aprovechar tablas estructuradas ni metadata
- Validación rígida con `parsing_confidence >= 0.6` que puede rechazar CVs válidos
- Dependencia `pypdf` no está en `requirements.txt` (problema de configuración)

**Objetivo:**
- Usar capacidades completas de la skill de PDF (texto + tablas + imágenes + URLs)
- Delegar la validación de calidad al agente de Claude
- Implementación gradual y reversible por fases

---

## Contexto Técnico

### Archivos Afectados

**Código Principal:**
- `src/services/pdf_extractor.py` - Lógica de extracción
- `src/api/analyze.py` - Endpoint que valida parsing_confidence
- `src/services/agent/cv_analyzer_agent.py` - Agente que recibe el contenido

**Nuevos Archivos:**
- `src/models/pdf_content.py` - Modelo de datos enriquecido

**Dependencias:**
- `requirements.txt` o `pyproject.toml` - Añadir pdfplumber

**Tests:**
- `tests/unit/test_pdf_extractor.py` - Actualizar tests

### Capacidades de la Skill de PDF

Según `.claude/skills/pdf/SKILL.md` y `reference.md`:
- **pypdf:** Merge, split, metadata, rotación
- **pdfplumber:** Extracción de texto con layout + tablas estructuradas
- **pdfimages (CLI):** Extracción de imágenes embebidas
- **pypdfium2:** Renderizado a imágenes (no necesario para MVP)
- **reportlab:** Creación de PDFs (no necesario, solo lectura)

---

## Fases de Implementación

### **Fase 1: Modernizar Extracción de Texto con pdfplumber**

**Objetivo:** Mejorar la extracción de texto y añadir soporte para tablas estructuradas.

**Archivos a modificar:**
- `src/services/pdf_extractor.py`
- `requirements.txt` o `pyproject.toml`

**Cambios Detallados:**

1. **Reemplazar `pypdf.PdfReader` por `pdfplumber.open()`** en la función `invoke_pdf_skill()`:
   ```python
   # ANTES
   from pypdf import PdfReader
   reader = PdfReader(str(file_path))
   text = ""
   for page in reader.pages:
       text += page.extract_text() + "\n"

   # DESPUÉS
   import pdfplumber
   with pdfplumber.open(str(file_path)) as pdf:
       text = ""
       for page in pdf.pages:
           text += page.extract_text() + "\n"
   ```

2. **Añadir extracción de tablas:**
   ```python
   tables = []
   with pdfplumber.open(str(file_path)) as pdf:
       for page in pdf.pages:
           page_tables = page.extract_tables()
           tables.extend(page_tables)
   ```

3. **Extraer metadata real del PDF:**
   ```python
   with pdfplumber.open(str(file_path)) as pdf:
       page_count = len(pdf.pages)
       metadata = pdf.metadata  # autor, título, fecha creación
   ```

4. **Actualizar `PDFExtractionResult`** para incluir tablas y metadata:
   ```python
   @dataclass
   class PDFExtractionResult:
       text: str
       parsing_confidence: float
       page_count: int  # ✅ Ahora con valor real
       char_count: int
       cv_language: str
       tables: list[list[list[str]]] = field(default_factory=list)  # NEW
       metadata: dict[str, Any] = field(default_factory=dict)  # NEW
   ```

5. **Añadir dependencia:**
   ```toml
   # pyproject.toml o requirements.txt
   pdfplumber>=0.10.0
   pypdf>=3.17.0  # Mantener para compatibilidad
   ```

**Resultado Esperado:**
- Extracción de texto más precisa con layout preservado
- Tablas estructuradas disponibles para el agente
- Metadata real (número de páginas correcto, autor, título)

---

### **Fase 2: Extracción de Imágenes y URLs**

**Objetivo:** Enriquecer el contenido extraído con elementos visuales y enlaces externos.

**Archivos a modificar:**
- `src/services/pdf_extractor.py`
- `src/models/pdf_content.py` (nuevo archivo)

**Cambios Detallados:**

1. **Crear modelo de datos enriquecido** en `src/models/pdf_content.py`:
   ```python
   from dataclasses import dataclass, field
   from typing import Any

   @dataclass
   class ImageInfo:
       page_number: int
       image_index: int
       format: str  # jpg, png, etc.
       size_bytes: int
       extracted_path: str | None = None

   @dataclass
   class EnrichedPDFContent:
       text: str
       tables: list[list[list[str]]] = field(default_factory=list)
       images: list[ImageInfo] = field(default_factory=list)
       urls: list[str] = field(default_factory=list)
       metadata: dict[str, Any] = field(default_factory=dict)
       page_count: int = 1
       char_count: int = 0
       cv_language: str = "en"
       parsing_confidence: float = 0.0
   ```

2. **Extraer imágenes usando comando CLI `pdfimages`** (de poppler-utils):
   ```python
   import subprocess
   import tempfile
   from pathlib import Path

   def extract_images(pdf_path: Path) -> list[ImageInfo]:
       with tempfile.TemporaryDirectory() as temp_dir:
           # Extraer imágenes
           subprocess.run([
               "pdfimages",
               "-list",  # Primero listar
               str(pdf_path)
           ], capture_output=True)

           # Parsear output para obtener info
           # Retornar lista de ImageInfo
   ```

3. **Extraer URLs del texto:**
   ```python
   import re

   def extract_urls(text: str) -> list[str]:
       url_pattern = r'https?://[^\s]+|www\.[^\s]+'
       urls = re.findall(url_pattern, text)
       return list(set(urls))  # Eliminar duplicados
   ```

4. **Detectar logos corporativos** (imágenes en primera página):
   ```python
   # Las imágenes en la primera página suelen ser logos
   # Útil para identificar empresa actual del candidato
   first_page_images = [img for img in images if img.page_number == 1]
   ```

**Resultado Esperado:**
- Lista de imágenes embebidas con metadata
- URLs extraídas (LinkedIn, GitHub, portfolio, certificaciones online)
- Información visual disponible para el agente

---

### **Fase 3: Delegar Validación al Agente de Claude**

**Objetivo:** Eliminar validación rígida basada en threshold y dejar que el agente determine si el contenido es suficiente.

**Archivos a modificar:**
- `src/api/analyze.py`
- `src/services/agent/cv_analyzer_agent.py`

**Cambios Detallados:**

**En `src/api/analyze.py` (líneas 280-296):**

```python
# ELIMINAR este bloque:
if parsing_confidence < MIN_PARSING_CONFIDENCE:
    logger.warning(...)
    raise HTTPException(...)

# REEMPLAZAR con solo logging:
if parsing_confidence < MIN_PARSING_CONFIDENCE:
    logger.warning(
        "low_parsing_confidence_detected",
        request_id=request_id,
        parsing_confidence=parsing_confidence,
        threshold=MIN_PARSING_CONFIDENCE,
        action="proceeding_with_agent_validation"
    )
    # ✅ No lanzar excepción, dejar que el agente decida
```

**En `src/services/agent/cv_analyzer_agent.py`:**

1. **Eliminar validación rígida en `analyze_cv()` (líneas 108-112):**
   ```python
   # ELIMINAR:
   if parsing_confidence < 0.6:
       raise ValueError(...)

   # REEMPLAZAR con logging informativo:
   logger.info(
       "parsing_confidence_metadata",
       parsing_confidence=parsing_confidence,
       note="Agent will determine content sufficiency"
   )
   ```

2. **Actualizar `_build_user_prompt()` para incluir información enriquecida:**
   ```python
   def _build_user_prompt(
       self,
       cv_text: str,
       enriched_content: EnrichedPDFContent,  # NEW parameter
       role_target: str | None,
       language: str
   ) -> str:
       # Añadir información de tablas
       if enriched_content.tables:
           prompt += f"\n\nTABLAS ESTRUCTURADAS ({len(enriched_content.tables)} encontradas):\n"
           for i, table in enumerate(enriched_content.tables[:3]):  # Max 3
               prompt += f"Tabla {i+1}: {table}\n"

       # Añadir URLs encontradas
       if enriched_content.urls:
           prompt += f"\n\nENLACES EXTERNOS ({len(enriched_content.urls)}):\n"
           prompt += "\n".join(enriched_content.urls[:10])  # Max 10

       # Añadir info de imágenes
       if enriched_content.images:
           prompt += f"\n\nIMAGENES EMBEBIDAS: {len(enriched_content.images)} encontradas"
           first_page_imgs = [img for img in enriched_content.images if img.page_number == 1]
           if first_page_imgs:
               prompt += f" ({len(first_page_imgs)} en primera página - posibles logos)"
   ```

3. **El agente validará contenido internamente:**
   ```python
   # El prompt incluirá:
   """
   IMPORTANTE: Si el texto extraído es insuficiente o de muy baja calidad:
   1. Analiza si hay tablas estructuradas que compensen
   2. Revisa si las URLs proporcionan contexto adicional
   3. Si definitivamente no hay información suficiente, responde con:
      {"error": "insufficient_content", "reason": "descripción del problema"}
   """
   ```

**Resultado Esperado:**
- No se rechazan PDFs prematuramente por threshold arbitrario
- El agente de Claude decide basándose en TODO el contenido disponible
- Mejor experiencia de usuario (menos falsos negativos)

---

### **Fase 4: Mantener Lógica de Confianza y Lenguaje (Opcional)**

**Objetivo:** Preservar métricas útiles para logging y debugging sin que bloqueen el flujo.

**Archivos a modificar:**
- `src/services/pdf_extractor.py`

**Decisiones de Diseño:**

1. **MANTENER** `calculate_parsing_confidence()`:
   - Útil para métricas de observabilidad
   - Loggear como metadata, no como gate de validación
   - Puede ayudar al agente a calibrar su confianza

2. **MANTENER** `detect_language()`:
   - Pre-detección de idioma útil para el agente
   - Puede influir en el prompt inicial
   - Backup si el agente no detecta idioma claramente

3. **Actualizar comentarios** para reflejar el nuevo propósito:
   ```python
   def calculate_parsing_confidence(text: str, page_count: int = 1) -> float:
       """Calculate parsing confidence score for observability metrics.

       This score is used for logging and monitoring, NOT for rejecting CVs.
       The agent will make the final determination of content sufficiency.

       Args:
           text: Extracted text from PDF
           page_count: Number of pages in the PDF

       Returns:
           Confidence score between 0.0 and 1.0 (informational only)
       """
   ```

**Resultado Esperado:**
- Métricas útiles para debugging y monitoring
- No bloquean el procesamiento de CVs
- Información adicional para el agente

---

### **Fase 5: Testing y Validación**

**Objetivo:** Asegurar que los cambios no rompen funcionalidad existente y cubren casos edge.

**Archivos a modificar:**
- `tests/unit/test_pdf_extractor.py`

**Nuevos Tests a Añadir:**

1. **Test de extracción de tablas:**
   ```python
   async def test_extract_tables_from_pdf():
       # PDF con tabla de experiencia laboral
       result = await extract_text_from_pdf(pdf_with_tables)
       assert len(result.tables) > 0
       assert isinstance(result.tables[0], list)
   ```

2. **Test de extracción de URLs:**
   ```python
   async def test_extract_urls_from_cv():
       # CV con LinkedIn, GitHub
       result = await extract_text_from_pdf(pdf_with_urls)
       assert "linkedin.com" in str(result.urls)
       assert "github.com" in str(result.urls)
   ```

3. **Test de metadata real:**
   ```python
   async def test_pdf_metadata_extraction():
       result = await extract_text_from_pdf(multi_page_pdf)
       assert result.page_count == 3  # Real page count
       assert "title" in result.metadata or "author" in result.metadata
   ```

4. **Test de validación delegada al agente:**
   ```python
   async def test_low_confidence_still_processed():
       # PDF de baja calidad que antes era rechazado
       # Ahora debe llegar al agente
       result = await analyze_cv(low_quality_pdf)
       # El agente decide si es suficiente o no
   ```

5. **Test de casos edge:**
   ```python
   async def test_pdf_only_images():
       # PDF escaneado sin texto OCR
       result = await extract_text_from_pdf(scanned_pdf)
       assert result.images  # Debe tener imágenes
       # El agente debe pedir OCR o rechazar

   async def test_pdf_empty():
       # PDF vacío
       with pytest.raises(ValueError):
           await extract_text_from_pdf(empty_pdf)
   ```

**Resultado Esperado:**
- Cobertura de tests >= 80%
- Todos los casos edge manejados
- Regresión cero en funcionalidad existente

---

## Dependencias y Requisitos

### Nuevas Dependencias Python

```toml
# pyproject.toml o requirements.txt
pdfplumber>=0.10.0  # Extracción de texto + tablas
pypdf>=3.17.0       # Ya existe, mantener para compatibilidad
```

### Herramientas CLI Requeridas (Opcional - Fase 2)

- **pdfimages** (parte de poppler-utils):
  ```bash
  # Ubuntu/Debian
  sudo apt-get install poppler-utils

  # macOS
  brew install poppler

  # Windows
  # Descargar poppler-windows binaries
  # O usar Python pdfimages wrapper
  ```

**Nota:** Si `pdfimages` no está disponible, la Fase 2 puede omitirse o usar alternativa Python pura.

---

## Cambios en el Flujo de Datos

### ANTES (Implementación Actual)

```
┌─────────┐
│ PDF File│
└────┬────┘
     │
     ▼
┌─────────────────────┐
│ pypdf.PdfReader     │
│ - Extract text only │
└────┬────────────────┘
     │
     ▼
┌──────────────────────────┐
│ calculate_confidence()   │
│ Returns: 0.0 - 1.0       │
└────┬─────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ if confidence < 0.6:     │
│   ❌ REJECT (HTTP 400)   │
└────┬─────────────────────┘
     │ ✅ confidence >= 0.6
     ▼
┌──────────────────────────┐
│ CVAnalyzerAgent          │
│ - Receives text only     │
└────┬─────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Claude API Analysis      │
└──────────────────────────┘
```

### DESPUÉS (Implementación Propuesta)

```
┌─────────┐
│ PDF File│
└────┬────┘
     │
     ▼
┌──────────────────────────────────────┐
│ pdfplumber.open()                    │
│ - Extract text (with layout)         │
│ - Extract tables (page.extract_tables)│
│ - Extract metadata (pdf.metadata)    │
└────┬─────────────────────────────────┘
     │
     ├──────────────────────────┐
     │                          │
     ▼                          ▼
┌────────────────┐   ┌─────────────────┐
│ extract_urls() │   │ pdfimages (CLI) │
│ - Regex search │   │ - List images   │
└────┬───────────┘   └────┬────────────┘
     │                    │
     │                    │
     ▼                    ▼
┌────────────────────────────────────────┐
│ EnrichedPDFContent                     │
│ - text: str                            │
│ - tables: List[...]                    │
│ - urls: List[str]                      │
│ - images: List[ImageInfo]              │
│ - metadata: Dict                       │
│ - parsing_confidence: float (metadata) │
└────┬───────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ calculate_confidence()               │
│ ⚠️  Log as metadata only             │
│ ✅ NO rejection based on threshold   │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ CVAnalyzerAgent                      │
│ - Receives EnrichedPDFContent        │
│ - Agent validates content quality    │
│ - Uses tables, URLs, images context  │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ Claude API Analysis                  │
│ - If insufficient: returns error     │
│ - If sufficient: full analysis       │
└──────────────────────────────────────┘
```

**Diferencias Clave:**
1. ✅ Extracción enriquecida (tablas, URLs, imágenes)
2. ✅ No hay rechazo prematuro por threshold
3. ✅ El agente decide si el contenido es suficiente
4. ✅ Mejor contexto para análisis más preciso

---

## Compatibilidad con Skill de PDF

La implementación sigue los patrones documentados en la skill oficial:

### Referencia: `.claude/skills/pdf/SKILL.md`

**Extracción de Texto:**
```python
# Patrón recomendado por la skill
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
```

**Extracción de Tablas:**
```python
# Patrón recomendado por la skill
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            # Process table
```

### Referencia: `.claude/skills/pdf/reference.md`

**Extracción de Imágenes:**
```bash
# Comando CLI recomendado
pdfimages -list document.pdf
pdfimages -all document.pdf images/img
```

**Metadata:**
```python
# Usando pypdf como fallback
from pypdf import PdfReader
reader = PdfReader("document.pdf")
meta = reader.metadata
```

**Nuestra implementación ES una aplicación Python de estos patrones oficiales.**

---

## Plan de Rollback

Cada fase es independiente y reversible:

### Si falla Fase 1 (pdfplumber):
```python
# Revertir a pypdf original
# Commit: git revert <commit-hash>
# O simplemente cambiar imports
```

### Si falla Fase 2 (imágenes/URLs):
```python
# Comentar código de extracción
# Usar EnrichedPDFContent sin imágenes/URLs
# La funcionalidad básica sigue intacta
```

### Si falla Fase 3 (validación delegada):
```python
# Restaurar el threshold check
if parsing_confidence < MIN_PARSING_CONFIDENCE:
    raise HTTPException(...)
```

### Si falla Fase 5 (tests):
```python
# Los tests antiguos se mantienen
# Nuevos tests se marcan como @pytest.mark.skip
# Implementación puede seguir funcionando
```

**Ventaja:** Las fases son aditivas, no destructivas. Siempre podemos volver atrás.

---

## Métricas de Éxito

### Fase 1:
- ✅ Extracción de tablas funcional en al menos 80% de CVs de prueba
- ✅ Número de páginas real (no siempre 1)
- ✅ Metadata extraída (al menos 2 de: título, autor, fecha)

### Fase 2:
- ✅ URLs extraídas en CVs con LinkedIn/GitHub
- ✅ Imágenes listadas correctamente
- ✅ Logos de primera página identificados

### Fase 3:
- ✅ 0% de rechazos prematuros por threshold
- ✅ Agente determina validez en 100% de casos
- ✅ Tasa de falsos negativos < 5%

### Fase 5:
- ✅ Cobertura de tests >= 80%
- ✅ 0 regresiones en funcionalidad existente
- ✅ Todos los tests pasan en CI/CD

---

## Timeline Estimado

| Fase | Esfuerzo | Prioridad |
|------|----------|-----------|
| Fase 1: pdfplumber + tablas | 4-6 horas | Alta |
| Fase 2: Imágenes + URLs | 3-4 horas | Media |
| Fase 3: Validación delegada | 2-3 horas | Alta |
| Fase 4: Refactor confianza | 1-2 horas | Baja |
| Fase 5: Testing completo | 4-6 horas | Alta |
| **TOTAL** | **14-21 horas** | - |

**Recomendación:** Implementar en 2-3 sesiones de desarrollo:
1. Sesión 1: Fases 1 + 3 (core functionality)
2. Sesión 2: Fase 2 (enrichment)
3. Sesión 3: Fase 5 (testing + validación)

---

## Próximos Pasos al Confirmar

### Checklist de Implementación

- [ ] **Preparación:**
  - [ ] Crear rama: `git checkout -b feature/pdf-skill-migration`
  - [ ] Backup del código actual
  - [ ] Leer documentación de pdfplumber

- [ ] **Fase 1:**
  - [ ] Actualizar `requirements.txt` o `pyproject.toml`
  - [ ] Instalar: `pip install pdfplumber`
  - [ ] Refactorizar `invoke_pdf_skill()` para usar pdfplumber
  - [ ] Actualizar `PDFExtractionResult` con campos nuevos
  - [ ] Test manual con CV de prueba

- [ ] **Fase 2:**
  - [ ] Crear `src/models/pdf_content.py`
  - [ ] Implementar `extract_urls()`
  - [ ] Implementar `extract_images()` (o skip si no hay pdfimages)
  - [ ] Integrar en `extract_text_from_pdf()`
  - [ ] Test manual con CV con tablas y URLs

- [ ] **Fase 3:**
  - [ ] Eliminar threshold check en `analyze.py`
  - [ ] Actualizar `analyze_cv()` en agente
  - [ ] Actualizar `_build_user_prompt()` con contenido enriquecido
  - [ ] Test manual con CV de baja calidad

- [ ] **Fase 4:**
  - [ ] Actualizar comentarios de `calculate_parsing_confidence()`
  - [ ] Actualizar logging para reflejar nuevo propósito
  - [ ] Verificar que se sigue usando para métricas

- [ ] **Fase 5:**
  - [ ] Actualizar tests existentes
  - [ ] Añadir tests nuevos (tablas, URLs, imágenes)
  - [ ] Ejecutar: `pytest tests/unit/test_pdf_extractor.py -v`
  - [ ] Coverage report: `pytest --cov=src.services.pdf_extractor`

- [ ] **Validación Final:**
  - [ ] Test E2E con CV real
  - [ ] Verificar logs estructurados
  - [ ] Performance test (no debe ser más lento)
  - [ ] Code review
  - [ ] Merge a main

---

## Notas Finales

### Decisiones de Diseño Clave

1. **¿Por qué pdfplumber y no pypdf?**
   - pdfplumber tiene mejor extracción de tablas
   - Preserva layout de texto mejor
   - Es la herramienta recomendada en la skill de PDF para tablas

2. **¿Por qué delegar validación al agente?**
   - El threshold de 0.6 es arbitrario
   - Claude puede evaluar contexto mejor (tablas compensan texto pobre)
   - Reduce falsos negativos

3. **¿Por qué migración gradual?**
   - Reduce riesgo
   - Permite rollback fácil
   - Cada fase añade valor independientemente

### Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| pdfplumber más lento | Media | Medio | Benchmark, optimizar si necesario |
| pdfimages no disponible | Alta | Bajo | Fase 2 opcional, usar alternativa Python |
| Agente rechaza menos CVs válidos | Baja | Alto | Logging exhaustivo, tuning de prompts |
| Tests fallan | Media | Medio | Fase 5 completa, CI/CD robusto |

---

## Referencias

- Skill de PDF: `.claude/skills/pdf/SKILL.md`
- Referencia avanzada: `.claude/skills/pdf/reference.md`
- Documentación pdfplumber: https://github.com/jsvine/pdfplumber
- PRD Original: `docs/PRD-CV-Cybersecurity-Analyzer.md`

---

**Aprobado por:** _Pendiente_
**Fecha de aprobación:** _Pendiente_
**Estado de implementación:** Planificación
