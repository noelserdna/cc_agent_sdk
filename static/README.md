# Frontend Web - CV Cybersecurity Analyzer

Interfaz web para analizar CVs de ciberseguridad con IA.

## 🚀 Acceso

Una vez que el servidor esté corriendo, accede a:

```
http://localhost:8000/
```

## ⚙️ Configuración de API Key

**IMPORTANTE**: Antes de usar el frontend, debes configurar una API key válida.

### Paso 1: Configurar API Key en el Backend

Asegúrate de que el archivo `.env` en la raíz del proyecto contenga:

```bash
API_KEYS=tu-api-key-aqui,otra-key-opcional
```

Las API keys deben tener mínimo 16 caracteres.

### Paso 2: Configurar API Key en el Frontend

Edita el archivo `static/js/app.js` y cambia la línea 6:

```javascript
const CONFIG = {
    API_KEY: 'tu-api-key-aqui',  // ⚠️ CAMBIAR ESTA LÍNEA
    // ...
};
```

Reemplaza `'tu-api-key-aqui'` con una de las API keys configuradas en tu `.env`.

**⚠️ Advertencia de Seguridad**:
- La API key estará visible en el código JavaScript del navegador
- Esto es apropiado SOLO para:
  - Desarrollo local
  - Uso personal/interno
  - Demos y prototipos
- **NO usar en producción pública**

## 📁 Estructura de Archivos

```
static/
├── README.md           # Este archivo
├── index.html          # Aplicación web (SPA)
├── css/
│   └── styles.css      # Estilos
└── js/
    └── app.js          # Lógica de la aplicación
```

## 🎯 Características

### 1. Upload de CVs
- Drag & drop de archivos PDF
- Validación: solo PDF, máximo 10MB
- Campo opcional "Rol objetivo"
- Selector de idioma (Español/Inglés)

### 2. Procesamiento
- Spinner mientras se analiza
- Timeout de 35 segundos
- Manejo de errores

### 3. Dashboard de Resultados
- **Score Total**: Gauge visual (0-10)
- **Percentil**: Posición vs mercado
- **Gráfico Radar**: 24 parámetros de ciberseguridad
- **5 Fortalezas**: Cards destacados
- **Áreas de Mejora**: Lista priorizada
- **Red Flags**: Alertas de severidad
- **Recomendaciones**: Certificaciones, training, experiencia
- **Preguntas de Entrevista**: Técnicas, escenarios, verificación
- **Metadata**: Info del análisis

## 🛠️ Desarrollo

### Modificar Estilos

Edita `static/css/styles.css`. Los cambios se verán al recargar la página (no requiere rebuild).

### Modificar Lógica

Edita `static/js/app.js`. Los cambios se verán al recargar la página.

### Variables CSS Disponibles

```css
:root {
    --primary: #3b82f6;
    --secondary: #8b5cf6;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    /* ... más variables */
}
```

## 🐛 Debugging

### Consola del Navegador

Abre las herramientas de desarrollo (F12) para ver:
- Logs de la aplicación
- Errores de JavaScript
- Requests de red a la API

### Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 401 Unauthorized | API key inválida | Verifica que la key en `app.js` coincida con `.env` |
| 404 Not Found | Servidor no corriendo | Inicia el servidor con `uvicorn` |
| CORS error | Configuración CORS | Ya está configurado en `main.py` |
| Timeout | Análisis toma >35s | Normal para CVs grandes, reintentar |

## 📊 Gráficos

Los gráficos usan **Chart.js 4.x** cargado desde CDN:

- **Radar Chart**: 24 parámetros de evaluación
- **Gauge Chart**: Score total (tipo doughnut con rotación)

Colores automáticos según score:
- Verde (≥8): Excelente
- Azul (6-7.9): Bueno
- Amarillo (4-5.9): Regular
- Rojo (<4): Bajo

## 🌐 Navegadores Soportados

- Chrome/Edge: ✅ Última versión
- Firefox: ✅ Última versión
- Safari: ✅ Última versión
- IE11: ❌ No soportado

## 📱 Responsive

El frontend es completamente responsive:
- Desktop: Grid con múltiples columnas
- Tablet: 2 columnas adaptativas
- Mobile: 1 columna vertical

## 🔒 Seguridad

### Limitaciones Actuales

- ❌ API key expuesta en JavaScript
- ❌ Sin autenticación de usuarios
- ❌ Sin rate limiting en frontend

### Para Producción

Si necesitas desplegar en producción pública:

1. **Implementar Backend-for-Frontend (BFF)**:
   - Crear endpoint `/api/analyze-cv-proxy` en backend
   - El frontend llama al proxy sin API key
   - El proxy agrega la API key desde variables de entorno

2. **Autenticación de Usuarios**:
   - Implementar OAuth/JWT
   - Login antes de acceder al frontend

3. **Rate Limiting**:
   - Limitar requests por usuario/IP

## 📝 Notas

- El análisis puede tomar hasta 30 segundos
- Los resultados NO se guardan (stateless)
- Cada análisis es independiente
- No hay histórico de CVs analizados

## 🚧 Mejoras Futuras

- [ ] Dark mode toggle
- [ ] Exportar resultados a PDF
- [ ] Guardar análisis en base de datos
- [ ] Comparar múltiples CVs
- [ ] Histórico de análisis
- [ ] Internacionalización completa (i18n)
- [ ] PWA (Progressive Web App)

## 📞 Soporte

Para issues o preguntas, revisa:
- `docs/PLAN-frontend-web.md` - Especificación completa
- `docs/PRD-CV-Cybersecurity-Analyzer.md` - PRD del proyecto
- API docs: `http://localhost:8000/docs`

---

**Versión**: 1.0.0
**Última actualización**: 2025-10-28
