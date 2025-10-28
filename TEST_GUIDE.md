# 🧪 Guía de Pruebas - CV Cybersecurity Analyzer API

Esta guía te ayudará a probar el sistema end-to-end para verificar que la implementación del parsing real del agente funciona correctamente.

---

## 📋 Requisitos Previos

### 1. API Key de Anthropic

Necesitas una API key válida de Claude:

1. Ve a [https://console.anthropic.com/](https://console.anthropic.com/)
2. Crea una cuenta o inicia sesión
3. Navega a **API Keys**
4. Genera una nueva API key (empieza con `sk-ant-...`)

### 2. Configurar Variables de Entorno

Edita el archivo `.env` en la raíz del proyecto y configura:

```env
# Claude Agent SDK (CRÍTICO)
ANTHROPIC_API_KEY=sk-ant-tu-key-real-aqui

# Authentication (para pruebas locales)
API_KEYS=test-key-local-12345678

# Resto de configuración (opcional, usa defaults)
CLAUDE_MODEL=claude-sonnet-4-5-20250929
CLAUDE_MAX_TOKENS=8192
LOG_LEVEL=INFO
```

**Nota**: Las API keys de `API_KEYS` son para autenticar al cliente que llama a tu API. Para pruebas locales puedes usar cualquier string de 16+ caracteres.

---

## 🚀 Opción 1: Prueba Directa con Script Python

### Ejecutar el Script de Prueba

```bash
python test_api_local.py
```

### ¿Qué hace este script?

1. ✅ Carga el CV de prueba desde `tests/fixtures/sample_cvs/test_cybersecurity_cv.txt`
2. ✅ Calcula el parsing confidence del texto
3. ✅ Verifica que la API key de Anthropic esté configurada
4. ✅ Inicializa el agente CVAnalyzerAgent
5. ✅ Llama a `analyze_cv()` con el texto del CV
6. ✅ El agente envía el CV a Claude API con el prompt JSON estructurado
7. ✅ Claude retorna un JSON con los 24 parámetros evaluados
8. ✅ El sistema parsea el JSON y calcula scores ponderados
9. ✅ Muestra un resumen completo del análisis

### Salida Esperada

```
================================================================================
🧪 PRUEBA END-TO-END: CV Cybersecurity Analyzer API
================================================================================

✅ CV cargado: 5847 caracteres
📄 Extracto: JUAN CARLOS PÉREZ GARCÍA
Analista de Seguridad Senior | Pentester Certificado...

✅ Parsing confidence calculado: 0.85
✅ API key detectada: sk-ant-api03-abc12...
✅ Modelo configurado: claude-sonnet-4-5-20250929

🤖 Inicializando agente Claude...
✅ Agente inicializado

🔍 Analizando CV (esto puede tardar 20-30 segundos)...
   - Enviando CV al agente Claude
   - Solicitando análisis de 24 parámetros
   - Calculando scores ponderados

================================================================================
✅ ANÁLISIS COMPLETADO
================================================================================

📊 RESUMEN DEL CANDIDATO
--------------------------------------------------------------------------------
  Nombre:              Juan Carlos Pérez García
  Rol detectado:       Security Analyst Senior / Pentester
  Nivel de seniority:  Senior
  Score total:         8.45/10.0
  Percentil:           84%
  Años en IT:          8.0
  Años en seguridad:   5.0

💪 TOP 5 FORTALEZAS
--------------------------------------------------------------------------------
  1. Offensive Skills (9.2/10)
     Amplia experiencia en pentesting con OSCP y más de 50 pruebas de penetr...
     Valor de mercado: high

  2. Certifications (9.0/10)
     OSCP, CEH, AWS Security Specialty - portfolio sólido de certificaciones...
     Valor de mercado: high

  3. Cloud Security (8.5/10)
     Experiencia práctica en AWS con hardening de infraestructura y Guardd...
     Valor de mercado: high

  ... (continúa)
```

---

## 🌐 Opción 2: Prueba con FastAPI Server + HTTP Client

### 1. Iniciar el Servidor

```bash
# En una terminal
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Llamar al Endpoint con curl

```bash
curl -X POST http://localhost:8000/v1/analyze-cv \
  -H "X-API-Key: test-key-local-12345678" \
  -F "file=@tests/fixtures/sample_cvs/test_cybersecurity_cv.txt" \
  -F "language=es" \
  -F "role_target=Senior Security Analyst" \
  | jq '.'
```

**Nota para Windows (PowerShell)**:

```powershell
# Necesitas curl.exe (no el alias de Invoke-WebRequest)
curl.exe -X POST http://localhost:8000/v1/analyze-cv `
  -H "X-API-Key: test-key-local-12345678" `
  -F "file=@tests/fixtures/sample_cvs/test_cybersecurity_cv.txt" `
  -F "language=es" `
  | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### 3. Verificar el Health Endpoint

```bash
curl http://localhost:8000/v1/health | jq '.'
```

Salida esperada:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agent_sdk_version": "0.71.0",
  "uptime_seconds": 42,
  "environment": "development"
}
```

---

## 🐍 Opción 3: Prueba con Cliente Python

Crea un archivo `test_client.py`:

```python
import httpx
import asyncio
from pathlib import Path


async def test_analyze_cv():
    """Test the API endpoint with a real HTTP request."""

    api_url = "http://localhost:8000"
    api_key = "test-key-local-12345678"

    # Prepare file
    cv_path = Path("tests/fixtures/sample_cvs/test_cybersecurity_cv.txt")

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Open file
        with cv_path.open("rb") as f:
            files = {"file": (cv_path.name, f, "text/plain")}
            data = {
                "language": "es",
                "role_target": "Senior Security Analyst"
            }
            headers = {"X-API-Key": api_key}

            print("Sending request to API...")
            response = await client.post(
                f"{api_url}/v1/analyze-cv",
                headers=headers,
                files=files,
                data=data
            )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print("\n✅ ANÁLISIS COMPLETO")
            print(f"Nombre: {result['candidate_summary']['name']}")
            print(f"Rol: {result['candidate_summary']['detected_role']}")
            print(f"Score Total: {result['candidate_summary']['total_score']}/10")

            print("\nTop 3 Fortalezas:")
            for i, strength in enumerate(result['strengths'][:3], 1):
                print(f"  {i}. {strength['area']} ({strength['score']}/10)")

        else:
            print(f"Error: {response.text}")


if __name__ == "__main__":
    asyncio.run(test_analyze_cv())
```

Ejecutar:

```bash
python test_client.py
```

---

## ✅ Checklist de Validación

Después de ejecutar las pruebas, verifica que:

- [ ] El sistema parsea correctamente el nombre del candidato
- [ ] El rol detectado es coherente ("Security Analyst", "Pentester", etc.)
- [ ] El score total está entre 0.0 y 10.0
- [ ] Los 24 parámetros tienen scores válidos (0.0-10.0)
- [ ] Cada parámetro tiene justificación (mínimo 20 caracteres)
- [ ] Cada parámetro tiene evidencia (lista con citas del CV)
- [ ] Se generan exactamente 5 strengths
- [ ] El score ponderado se calcula correctamente
- [ ] Los red flags se detectan cuando existen
- [ ] Las recomendaciones son relevantes al perfil
- [ ] Las preguntas de entrevista son técnicas y específicas

---

## 🐛 Troubleshooting

### Error: "Failed to parse Claude response as JSON"

**Causa**: Claude no retornó JSON válido (poco común con el prompt actual)

**Solución**:
1. Verifica que el prompt en `src/services/agent/cv_analyzer_agent.py` esté correcto
2. Revisa los logs para ver el texto que retornó Claude
3. Intenta con `temperature=0.0` para más consistencia

### Error: "Invalid API key" (401)

**Causa**: La API key en el header `X-API-Key` no coincide con `API_KEYS` en `.env`

**Solución**:
- Verifica que `.env` tenga: `API_KEYS=test-key-local-12345678`
- El header debe ser: `-H "X-API-Key: test-key-local-12345678"`

### Error: "Claude API call failed" (503)

**Causa**: Problema con la API key de Anthropic o rate limiting

**Solución**:
1. Verifica que `ANTHROPIC_API_KEY` en `.env` sea válida
2. Revisa tu cuota en https://console.anthropic.com/
3. Espera unos minutos si alcanzaste el rate limit

### Error: "Parsing confidence too low"

**Causa**: El texto del CV tiene muy poco contenido

**Solución**:
- Usa un CV más completo (mínimo 500 caracteres)
- Ajusta el threshold en `analyze_cv()` si es necesario

---

## 📊 Métricas de Rendimiento Esperadas

Con el CV de ejemplo proporcionado:

| Métrica | Valor Esperado |
|---------|----------------|
| Parsing Confidence | 0.80 - 0.95 |
| Processing Time | 15-30 segundos |
| Input Tokens | ~3000-4000 |
| Output Tokens | ~2000-3000 |
| Total Score | 7.0 - 9.0 (para el CV de ejemplo) |
| API Cost | ~$0.15-0.30 por análisis |

---

## 📝 Notas Finales

- **Primera ejecución**: Puede tardar un poco más mientras Claude "aprende" el formato
- **Rate Limits**: Ten en cuenta los límites de la API de Anthropic
- **Costos**: Cada análisis consume tokens (~5000-7000 total)
- **Idioma**: El sistema soporta `language="es"` o `language="en"`
- **Cache**: Claude API tiene cache automático de 5 minutos para prompts idénticos

---

## 🎯 Próximos Pasos

Una vez que la prueba funcione:

1. ✅ Probar con CVs reales en PDF
2. ✅ Validar la extracción de PDF con el skill de Claude Code
3. ✅ Ajustar los prompts si es necesario para mejorar precisión
4. ✅ Implementar tests automatizados con VCR cassettes
5. ✅ Configurar deployment con Docker

---

**¿Preguntas o problemas?**

- Revisa los logs en la consola del servidor
- Verifica los archivos `.env` y `pyproject.toml`
- Consulta la documentación de Claude API: https://docs.anthropic.com/
