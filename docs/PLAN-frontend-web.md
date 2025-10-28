# Plan: Frontend Web para Análisis de CVs de Ciberseguridad

**Fecha**: 2025-10-28
**Proyecto**: cc_agent_sdk
**Objetivo**: Crear una interfaz web simple para subir CVs y visualizar resultados del análisis

---

## 📋 Resumen Ejecutivo

Se desarrollará un frontend web en HTML/CSS/JavaScript vanilla que permita:
1. Subir CVs en formato PDF (drag & drop)
2. Mostrar estado de "Procesando..." mientras se analiza
3. Visualizar resultados en un dashboard avanzado con gráficos interactivos

El frontend se servirá desde el mismo servidor FastAPI existente en el puerto 8000.

---

## 🎯 Requisitos Funcionales

### RF-01: Upload de CVs
- Área de drag & drop para archivos PDF
- Validación client-side: solo PDF, máximo 10MB
- Campo opcional "Rol objetivo" (3-100 caracteres)
- Selector de idioma: Español (default) o Inglés
- Botón "Analizar CV"

### RF-02: Estado de Procesamiento
- Spinner animado mientras se procesa
- Mensaje "Analizando CV..."
- Manejo de timeout (máximo 30 segundos)

### RF-03: Dashboard de Resultados
- **Score Total**: Gauge circular visual (0-10)
- **Percentil**: Indicador de posición vs mercado
- **Información del Candidato**: Nombre, rol detectado, seniority, años de experiencia
- **Gráfico Radar**: Visualización de los 24 parámetros de ciberseguridad
- **5 Fortalezas**: Cards con área, descripción, score y market value
- **Áreas de Mejora**: Lista priorizada con gaps y recomendaciones
- **Red Flags**: Alertas con tipo, severidad, descripción e impacto
- **Recomendaciones**: Tabs organizados por certificaciones, training, experiencia
- **Preguntas de Entrevista**: Secciones colapsables (técnicas, escenarios, verificación)
- **Botón**: "Analizar otro CV" para resetear

### RF-04: Manejo de Errores
- 400: Mostrar mensaje de error específico del servidor
- 401: "Error de autenticación"
- 413: "Archivo muy grande, máximo 10MB"
- 500: "Error interno del servidor"
- 503: "Servicio no disponible, intenta de nuevo"
- Timeout: "El análisis está tomando más tiempo del esperado"

---

## 🏗️ Arquitectura Técnica

### Estructura de Archivos

```
cc_agent_sdk/
├── static/                    # NUEVO - Archivos estáticos del frontend
│   ├── index.html            # SPA principal
│   ├── css/
│   │   └── styles.css        # Estilos
│   └── js/
│       └── app.js            # Lógica de la aplicación
│
├── src/
│   ├── main.py               # MODIFICAR - Agregar StaticFiles
│   └── ...                   # Resto del backend sin cambios
```

### Stack Tecnológico

- **HTML5**: Estructura semántica
- **CSS3**: Grid, Flexbox, Variables CSS, Animaciones
- **JavaScript ES6+**: Fetch API, async/await, Modules (opcional)
- **Chart.js 4.x**: Gráficos (radar, doughnut, gauge)
- **No frameworks**: Vanilla JavaScript para simplicidad
- **No build tools**: Todo servido directamente sin compilación

### API Integration

**Endpoint**: `POST /v1/analyze-cv`

**Request**:
```javascript
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('role_target', roleTarget || '');
formData.append('language', language || 'es');

fetch('/v1/analyze-cv', {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY  // Hardcodeada
  },
  body: formData
})
```

**Response**: Ver `src/models/response.py` - `CVAnalysisResponse`

---

## 🎨 Diseño UI/UX

### Wireframe Conceptual

```
┌─────────────────────────────────────────────────────┐
│  CV CYBERSECURITY ANALYZER                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────┐    │
│  │                                           │    │
│  │      📄 Arrastra tu CV aquí              │    │
│  │         o haz clic para seleccionar      │    │
│  │                                           │    │
│  └───────────────────────────────────────────┘    │
│                                                     │
│  Rol objetivo (opcional): [________________]       │
│  Idioma: [ Español ▼ ]                             │
│                                                     │
│            [ Analizar CV ]                         │
│                                                     │
└─────────────────────────────────────────────────────┘

        ↓ (Después de upload)

┌─────────────────────────────────────────────────────┐
│  CV CYBERSECURITY ANALYZER                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│              ⏳ Analizando CV...                   │
│            [Spinner animado]                        │
│                                                     │
└─────────────────────────────────────────────────────┘

        ↓ (Resultados)

┌─────────────────────────────────────────────────────┐
│  CV CYBERSECURITY ANALYZER                          │
├─────────────────────────────────────────────────────┤
│  ┌──────────┬──────────┬─────────────────────────┐ │
│  │ Score    │ Percentil│ Rol: Cloud Security     │ │
│  │  [8.2]   │  85%     │ Seniority: Senior       │ │
│  └──────────┴──────────┴─────────────────────────┘ │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │   [Gráfico Radar - 24 Parámetros]          │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ⭐ FORTALEZAS                                      │
│  ┌────┬────┬────┬────┬────┐                       │
│  │Card│Card│Card│Card│Card│                       │
│  └────┴────┴────┴────┴────┘                       │
│                                                     │
│  📈 ÁREAS DE MEJORA                                 │
│  • Forensics (4.0) → Recomendaciones...            │
│                                                     │
│  ⚠️  RED FLAGS                                      │
│  • Employment gap (medium)...                      │
│                                                     │
│  💡 RECOMENDACIONES                                 │
│  [Tabs: Certificaciones | Training | Experiencia] │
│                                                     │
│  ❓ PREGUNTAS DE ENTREVISTA                         │
│  [Collapsibles: Técnicas | Escenarios | Verify]   │
│                                                     │
│            [ Analizar otro CV ]                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Paleta de Colores (Sugerida)

```css
:root {
  --primary: #3b82f6;      /* Azul principal */
  --secondary: #8b5cf6;    /* Púrpura */
  --success: #10b981;      /* Verde */
  --warning: #f59e0b;      /* Amarillo */
  --danger: #ef4444;       /* Rojo */
  --dark: #1f2937;         /* Gris oscuro */
  --light: #f9fafb;        /* Gris claro */
  --border: #e5e7eb;       /* Bordes */
}
```

---

## 📝 Especificación de Componentes

### 1. index.html

**Estructura**:
```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CV Cybersecurity Analyzer</title>
  <link rel="stylesheet" href="/static/css/styles.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
  <!-- Vista 1: Upload -->
  <section id="upload-view" class="view active">
    <div class="container">
      <h1>CV Cybersecurity Analyzer</h1>
      <div id="drop-zone">
        <input type="file" id="file-input" accept=".pdf">
        <label for="file-input">
          <p>📄 Arrastra tu CV aquí o haz clic para seleccionar</p>
        </label>
      </div>
      <div class="form-group">
        <label>Rol objetivo (opcional):</label>
        <input type="text" id="role-target" maxlength="100">
      </div>
      <div class="form-group">
        <label>Idioma:</label>
        <select id="language">
          <option value="es">Español</option>
          <option value="en">English</option>
        </select>
      </div>
      <button id="analyze-btn" disabled>Analizar CV</button>
      <p id="error-message" class="error"></p>
    </div>
  </section>

  <!-- Vista 2: Loading -->
  <section id="loading-view" class="view">
    <div class="container">
      <div class="spinner"></div>
      <p>Analizando CV...</p>
      <p class="hint">Esto puede tomar hasta 30 segundos</p>
    </div>
  </section>

  <!-- Vista 3: Results -->
  <section id="results-view" class="view">
    <div class="container">
      <h1>Resultados del Análisis</h1>
      <div id="results-content"></div>
      <button id="reset-btn">Analizar otro CV</button>
    </div>
  </section>

  <script src="/static/js/app.js"></script>
</body>
</html>
```

### 2. styles.css

**Características**:
- Reset CSS básico
- Variables CSS para colores y spacing
- Layout responsive con media queries
- Estilos para drag & drop (hover, active)
- Animaciones CSS para spinner y transiciones
- Grid/Flexbox para dashboard
- Cards con sombras y hover effects
- Estilos para gráficos Chart.js

**Secciones principales**:
```css
/* 1. Variables y Reset */
/* 2. Layout general */
/* 3. Vista Upload */
/* 4. Vista Loading */
/* 5. Vista Results - Dashboard */
/* 6. Componentes reutilizables */
/* 7. Responsive */
```

### 3. app.js

**Estructura del código**:

```javascript
// Configuración
const API_KEY = 'TU_API_KEY_AQUI'; // ⚠️ HARDCODED
const API_BASE_URL = window.location.origin;

// Estado de la aplicación
let currentView = 'upload';
let selectedFile = null;
let analysisResult = null;

// Referencias DOM
const views = {
  upload: document.getElementById('upload-view'),
  loading: document.getElementById('loading-view'),
  results: document.getElementById('results-view')
};

// Inicialización
document.addEventListener('DOMContentLoaded', init);

function init() {
  setupUploadHandlers();
  setupEventListeners();
}

// Manejo de Upload
function setupUploadHandlers() {
  // Drag & drop
  // File input change
  // Validación de archivos
}

// Llamada a API
async function analyzeCV(file, roleTarget, language) {
  const formData = new FormData();
  formData.append('file', file);
  if (roleTarget) formData.append('role_target', roleTarget);
  formData.append('language', language);

  const response = await fetch(`${API_BASE_URL}/v1/analyze-cv`, {
    method: 'POST',
    headers: { 'X-API-Key': API_KEY },
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error analizando CV');
  }

  return await response.json();
}

// Navegación entre vistas
function showView(viewName) {
  Object.values(views).forEach(v => v.classList.remove('active'));
  views[viewName].classList.add('active');
  currentView = viewName;
}

// Renderizado de resultados
function renderResults(data) {
  const container = document.getElementById('results-content');

  container.innerHTML = `
    ${renderHeader(data)}
    ${renderRadarChart(data)}
    ${renderStrengths(data)}
    ${renderImprovements(data)}
    ${renderRedFlags(data)}
    ${renderRecommendations(data)}
    ${renderInterviewQuestions(data)}
  `;

  // Inicializar gráficos Chart.js después del render
  initCharts(data);
}

// Gráficos con Chart.js
function initCharts(data) {
  createRadarChart(data.detailed_scores);
  createGaugeChart(data.candidate_summary.total_score);
}

function createRadarChart(scores) {
  const ctx = document.getElementById('radar-chart').getContext('2d');

  // Extraer los 24 parámetros
  const labels = Object.keys(scores);
  const values = labels.map(key => scores[key].score);

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels.map(formatLabel),
      datasets: [{
        label: 'Scores',
        data: values,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        pointBackgroundColor: 'rgba(59, 130, 246, 1)'
      }]
    },
    options: {
      scales: {
        r: {
          min: 0,
          max: 10,
          ticks: { stepSize: 2 }
        }
      }
    }
  });
}

// Helpers de renderizado
function renderHeader(data) { /* ... */ }
function renderStrengths(data) { /* ... */ }
function renderImprovements(data) { /* ... */ }
// etc.

// Manejo de errores
function showError(message) {
  const errorEl = document.getElementById('error-message');
  errorEl.textContent = message;
  errorEl.style.display = 'block';
}
```

---

## 🔧 Modificaciones al Backend

### src/main.py

**Cambios necesarios**:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # NUEVO
from fastapi.middleware.cors import CORSMiddleware  # NUEVO (si es necesario)

app = FastAPI(title="CV Cybersecurity Analyzer API", version="1.0.0")

# CORS (solo si frontend y backend están en dominios diferentes)
# En este caso no es necesario porque se sirve desde el mismo origen
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Montar archivos estáticos - NUEVO
app.mount("/static", StaticFiles(directory="static"), name="static")

# IMPORTANTE: Esto debe ir DESPUÉS de montar /static pero ANTES de las rutas API
# para que /static tenga prioridad

# Incluir routers existentes
from api import analyze, health
app.include_router(health.router, tags=["Health"])
app.include_router(analyze.router, prefix="/v1", tags=["Analysis"])

# Root endpoint - MODIFICAR para servir el frontend
from fastapi.responses import FileResponse

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Resto del código sin cambios
```

**Nota de seguridad sobre API Key**:
- ⚠️ La API key estará hardcodeada en el JavaScript del frontend
- Esto significa que cualquiera que acceda al código fuente del navegador podrá verla
- **Solo es apropiado para**:
  - Desarrollo local
  - Uso personal interno
  - Demos y prototipos
- **NO usar en producción pública**
- Para producción, considerar:
  - Backend-for-Frontend (BFF) que maneje la autenticación
  - OAuth/JWT para usuarios
  - Variables de entorno en servidor

---

## ✅ Criterios de Aceptación

### CA-01: Upload funcional
- ✅ Drag & drop funciona correctamente
- ✅ Validación client-side rechaza archivos no-PDF
- ✅ Validación client-side rechaza archivos >10MB
- ✅ Botón "Analizar" se habilita solo con archivo válido

### CA-02: Procesamiento visible
- ✅ Vista cambia a "loading" al iniciar análisis
- ✅ Spinner se muestra mientras espera respuesta
- ✅ Mensaje indica que puede tomar hasta 30s

### CA-03: Resultados completos
- ✅ Se muestran todos los componentes del análisis
- ✅ Gráfico radar renderiza correctamente con 24 parámetros
- ✅ Gauge de score total es claro y visual
- ✅ 5 fortalezas se muestran en cards
- ✅ Áreas de mejora son legibles y priorizadas
- ✅ Red flags destacan según severidad
- ✅ Recomendaciones organizadas en tabs
- ✅ Preguntas de entrevista son colapsables

### CA-04: Manejo de errores
- ✅ Errores de API se muestran claramente al usuario
- ✅ Timeout se maneja gracefully
- ✅ Usuario puede reintentar después de error

### CA-05: UX
- ✅ Transiciones entre vistas son suaves
- ✅ Diseño es responsive (mobile, tablet, desktop)
- ✅ Botón "Analizar otro CV" resetea correctamente

### CA-06: Integración
- ✅ Frontend accesible en `http://localhost:8000/`
- ✅ API REST sigue funcionando en `/v1/analyze-cv`
- ✅ No rompe funcionalidad existente del backend

---

## 🧪 Plan de Pruebas

### Pruebas Manuales

1. **Test Upload Happy Path**:
   - Subir CV válido → Debe procesar y mostrar resultados

2. **Test Validación Cliente**:
   - Intentar subir archivo .txt → Debe rechazar
   - Intentar subir PDF >10MB → Debe rechazar

3. **Test Campos Opcionales**:
   - Subir sin "role_target" → Debe funcionar
   - Subir con "role_target" → Debe incluirse en análisis
   - Cambiar idioma a EN → Resultados en inglés

4. **Test Manejo de Errores**:
   - API key inválida (modificar temporalmente) → Error 401
   - Servidor apagado → Error de conexión
   - PDF corrupto → Error 400

5. **Test Reset**:
   - Ver resultados → Click "Analizar otro CV" → Volver a vista upload

6. **Test Responsive**:
   - Abrir en mobile → Layout se adapta
   - Abrir en tablet → Layout se adapta
   - Redimensionar ventana → Sin breaks

### Pruebas de Integración

```python
# tests/integration/test_frontend_integration.py

import pytest
from fastapi.testclient import TestClient

def test_static_files_served(client: TestClient):
    """Verifica que archivos estáticos se sirven correctamente"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_css_accessible(client: TestClient):
    """Verifica que CSS es accesible"""
    response = client.get("/static/css/styles.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]

def test_js_accessible(client: TestClient):
    """Verifica que JavaScript es accesible"""
    response = client.get("/static/js/app.js")
    assert response.status_code == 200
```

---

## 📦 Entregables

1. ✅ `docs/PLAN-frontend-web.md` - Este documento
2. ✅ `static/index.html` - Frontend SPA
3. ✅ `static/css/styles.css` - Estilos
4. ✅ `static/js/app.js` - Lógica de aplicación
5. ✅ `src/main.py` - Modificado para servir estáticos
6. ✅ Tests de integración actualizados

---

## 🚀 Deployment

### Local Development
```bash
# 1. Asegurarse de tener .env configurado con API_KEY válida
# 2. Instalar dependencias (si no están)
pip install -r requirements.txt

# 3. Ejecutar servidor
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 4. Abrir navegador
# http://localhost:8000/
```

### Docker
```bash
# Rebuild con nuevos archivos estáticos
docker-compose build

# Levantar servicio
docker-compose up -d

# Verificar
curl http://localhost:8000/
```

### Producción
- ⚠️ **NO USAR** API key hardcodeada en producción
- Implementar autenticación de usuarios (OAuth, JWT)
- Usar HTTPS
- Considerar CDN para archivos estáticos
- Minificar CSS/JS
- Implementar rate limiting

---

## 📚 Referencias

- **FastAPI StaticFiles**: https://fastapi.tiangolo.com/tutorial/static-files/
- **Chart.js Docs**: https://www.chartjs.org/docs/latest/
- **MDN Web Docs - Drag & Drop**: https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API
- **Fetch API**: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

---

## 📝 Notas de Implementación

### Priorización
1. **ALTA**: Upload, API call, mostrar resultados básicos (texto)
2. **MEDIA**: Gráfico radar, gauge, styling avanzado
3. **BAJA**: Animaciones, easter eggs, dark mode

### Limitaciones Conocidas
- API key visible en código fuente (solo para dev/interno)
- Sin autenticación de usuarios
- Sin persistencia de resultados
- Sin histórico de análisis
- Sin comparación entre CVs

### Posibles Mejoras Futuras
- Autenticación de usuarios
- Guardar resultados en base de datos
- Exportar resultados a PDF
- Comparar múltiples CVs lado a lado
- Dark mode toggle
- Internacionalización completa (i18n)
- Progressive Web App (PWA)
- Análisis batch de múltiples CVs

---

**Fin del Plan**
