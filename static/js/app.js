// ========================================
// 1. Configuración
// ========================================

const CONFIG = {
    API_KEY: 'test-key-local-12345678901234567890',  // ✅ Configurado desde .env
    API_BASE_URL: window.location.origin,
    MAX_FILE_SIZE: 10 * 1024 * 1024,  // 10MB
    ALLOWED_EXTENSIONS: ['.pdf'],
    TIMEOUT_MS: 95000  // 95 segundos (API tiene 90s + margen)
};

// ========================================
// 2. Estado de la Aplicación
// ========================================

const appState = {
    currentView: 'upload',
    selectedFile: null,
    analysisResult: null,
    charts: {
        radar: null,
        gauge: null
    }
};

// ========================================
// 3. Referencias DOM
// ========================================

const DOM = {
    // Vistas
    views: {
        upload: document.getElementById('upload-view'),
        loading: document.getElementById('loading-view'),
        results: document.getElementById('results-view')
    },

    // Upload view
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    fileName: document.getElementById('file-name'),
    roleTarget: document.getElementById('role-target'),
    language: document.getElementById('language'),
    analyzeBtn: document.getElementById('analyze-btn'),
    errorMessage: document.getElementById('error-message'),

    // Results view
    resultsContent: document.getElementById('results-content'),
    resetBtn: document.getElementById('reset-btn'),

    // Score elements
    totalScore: document.getElementById('total-score'),
    percentile: document.getElementById('percentile'),
    candidateName: document.getElementById('candidate-name'),
    detectedRole: document.getElementById('detected-role'),
    seniorityLevel: document.getElementById('seniority-level'),
    yearsExperience: document.getElementById('years-experience'),

    // Chart canvases
    radarChart: document.getElementById('radar-chart'),
    scoreGauge: document.getElementById('score-gauge'),

    // Content containers
    strengthsGrid: document.getElementById('strengths-grid'),
    improvementsList: document.getElementById('improvements-list'),
    redflagsList: document.getElementById('redflags-list'),

    // Recommendations tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    recommendationsCertifications: document.getElementById('recommendations-certifications'),
    recommendationsTraining: document.getElementById('recommendations-training'),
    recommendationsExperience: document.getElementById('recommendations-experience'),
    recommendationsNextRoles: document.getElementById('recommendations-next-roles'),

    // Interview questions
    accordionHeaders: document.querySelectorAll('.accordion-header'),
    interviewTechnical: document.getElementById('interview-technical'),
    interviewScenario: document.getElementById('interview-scenario'),
    interviewVerification: document.getElementById('interview-verification'),

    // Metadata
    analysisTimestamp: document.getElementById('analysis-timestamp'),
    processingDuration: document.getElementById('processing-duration'),
    parsingConfidence: document.getElementById('parsing-confidence'),
    cvLanguage: document.getElementById('cv-language')
};

// ========================================
// 4. Inicialización
// ========================================

document.addEventListener('DOMContentLoaded', init);

function init() {
    console.log('CV Analyzer App initialized');
    setupUploadHandlers();
    setupEventListeners();
}

// ========================================
// 5. Manejo de Upload
// ========================================

function setupUploadHandlers() {
    // File input change (el click ya lo maneja el label for="file-input")
    DOM.fileInput.addEventListener('change', handleFileSelect);

    // Drag & drop
    DOM.dropZone.addEventListener('dragover', handleDragOver);
    DOM.dropZone.addEventListener('dragleave', handleDragLeave);
    DOM.dropZone.addEventListener('drop', handleDrop);

    // Prevenir comportamiento por defecto del navegador
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        DOM.dropZone.addEventListener(eventName, preventDefaults);
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDragOver(e) {
    DOM.dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    DOM.dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    DOM.dropZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Validar archivo
    const validation = validateFile(file);
    if (!validation.valid) {
        showError(validation.error);
        appState.selectedFile = null;
        DOM.analyzeBtn.disabled = true;
        DOM.fileName.textContent = '';
        return;
    }

    // Archivo válido
    appState.selectedFile = file;
    DOM.fileName.textContent = `Archivo seleccionado: ${file.name}`;
    DOM.analyzeBtn.disabled = false;
    hideError();
}

// ========================================
// 6. Validación de Archivos
// ========================================

function validateFile(file) {
    // Verificar que existe
    if (!file) {
        return { valid: false, error: 'No se ha seleccionado ningún archivo' };
    }

    // Verificar extensión
    const fileName = file.name.toLowerCase();
    const hasValidExtension = CONFIG.ALLOWED_EXTENSIONS.some(ext => fileName.endsWith(ext));
    if (!hasValidExtension) {
        return { valid: false, error: 'Solo se permiten archivos PDF' };
    }

    // Verificar tamaño
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
        return { valid: false, error: `El archivo es muy grande (${sizeMB}MB). Máximo permitido: 10MB` };
    }

    // Verificar que no esté vacío
    if (file.size === 0) {
        return { valid: false, error: 'El archivo está vacío' };
    }

    return { valid: true };
}

// ========================================
// 7. Event Listeners
// ========================================

function setupEventListeners() {
    // Botón analizar
    DOM.analyzeBtn.addEventListener('click', handleAnalyze);

    // Botón reset
    DOM.resetBtn.addEventListener('click', handleReset);

    // Tabs de recomendaciones
    DOM.tabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetTab = e.currentTarget.dataset.tab;
            switchTab(targetTab);
        });
    });

    // Accordion de preguntas
    DOM.accordionHeaders.forEach(header => {
        header.addEventListener('click', (e) => {
            toggleAccordion(e.currentTarget);
        });
    });
}

function switchTab(tabName) {
    // Desactivar todos los tabs
    DOM.tabBtns.forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

    // Activar el tab seleccionado
    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    const activePane = document.getElementById(`tab-${tabName}`);

    if (activeBtn && activePane) {
        activeBtn.classList.add('active');
        activePane.classList.add('active');
    }
}

function toggleAccordion(header) {
    const targetId = header.dataset.target;
    const content = document.getElementById(targetId);

    // Toggle active class
    header.classList.toggle('active');
    content.classList.toggle('active');
}

// ========================================
// 8. Análisis de CV (API Call)
// ========================================

async function handleAnalyze() {
    if (!appState.selectedFile) {
        showError('Por favor selecciona un archivo PDF');
        return;
    }

    try {
        // Cambiar a vista loading
        showView('loading');

        // Preparar datos
        const roleTarget = DOM.roleTarget.value.trim();
        const language = DOM.language.value;

        // Llamar a la API
        const result = await analyzeCV(appState.selectedFile, roleTarget, language);

        // Guardar resultado y mostrar
        appState.analysisResult = result;
        renderResults(result);
        showView('results');

    } catch (error) {
        console.error('Error al analizar CV:', error);
        showView('upload');
        showError(error.message || 'Error al analizar el CV. Por favor intenta de nuevo.');
    }
}

async function analyzeCV(file, roleTarget, language) {
    // Crear FormData
    const formData = new FormData();
    formData.append('file', file);
    if (roleTarget) {
        formData.append('role_target', roleTarget);
    }
    formData.append('language', language);

    // Configurar timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT_MS);

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/v1/analyze-cv`, {
            method: 'POST',
            headers: {
                'X-API-Key': CONFIG.API_KEY
            },
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        // Manejar errores HTTP
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
        }

        return await response.json();

    } catch (error) {
        clearTimeout(timeoutId);

        if (error.name === 'AbortError') {
            throw new Error('El análisis está tomando más tiempo del esperado. Por favor intenta de nuevo.');
        }

        throw error;
    }
}

// ========================================
// 9. Navegación entre Vistas
// ========================================

function showView(viewName) {
    // Ocultar todas las vistas
    Object.values(DOM.views).forEach(view => {
        view.classList.remove('active');
    });

    // Mostrar vista solicitada
    if (DOM.views[viewName]) {
        DOM.views[viewName].classList.add('active');
        appState.currentView = viewName;
    }
}

// ========================================
// 10. Renderizado de Resultados
// ========================================

function renderResults(data) {
    console.log('Rendering results:', data);

    // Renderizar header
    renderHeader(data);

    // Renderizar fortalezas
    renderStrengths(data.strengths);

    // Renderizar áreas de mejora
    renderImprovements(data.improvement_areas);

    // Renderizar red flags
    renderRedFlags(data.red_flags);

    // Renderizar recomendaciones
    renderRecommendations(data.recommendations);

    // Renderizar preguntas de entrevista
    renderInterviewQuestions(data.interview_suggestions);

    // Renderizar metadata
    renderMetadata(data.analysis_metadata);

    // Inicializar gráficos (después de que el DOM esté actualizado)
    setTimeout(() => {
        initCharts(data);
    }, 100);
}

function renderHeader(data) {
    const summary = data.candidate_summary;

    // Score total
    DOM.totalScore.textContent = summary.total_score.toFixed(1);

    // Percentil
    DOM.percentile.textContent = summary.percentile;

    // Información del candidato
    DOM.candidateName.textContent = summary.name || 'No detectado';
    DOM.detectedRole.textContent = summary.detected_role || 'No detectado';
    DOM.seniorityLevel.textContent = summary.seniority_level || 'No detectado';

    // Años de experiencia
    const exp = summary.years_experience;
    if (exp) {
        DOM.yearsExperience.textContent = `${exp.total_it || 0} años en IT, ${exp.cybersecurity || 0} en ciberseguridad`;
    } else {
        DOM.yearsExperience.textContent = 'No detectado';
    }
}

function renderStrengths(strengths) {
    if (!strengths || strengths.length === 0) {
        DOM.strengthsGrid.innerHTML = '<p>No se detectaron fortalezas específicas.</p>';
        return;
    }

    const strengthsHTML = strengths.map(strength => `
        <div class="strength-card">
            <h3>${escapeHtml(strength.area)}</h3>
            <div class="strength-score">${strength.score.toFixed(1)}/10</div>
            <p class="strength-description">${escapeHtml(strength.description)}</p>
            <span class="market-value">${escapeHtml(strength.market_value)}</span>
        </div>
    `).join('');

    DOM.strengthsGrid.innerHTML = strengthsHTML;
}

function renderImprovements(improvements) {
    if (!improvements || improvements.length === 0) {
        DOM.improvementsList.innerHTML = '<p class="no-redflags">No se detectaron áreas críticas de mejora.</p>';
        return;
    }

    const improvementsHTML = improvements.map(improvement => `
        <div class="improvement-item">
            <div class="improvement-header">
                <span class="improvement-area">${escapeHtml(improvement.area)}</span>
                <span class="improvement-score">${improvement.current_score.toFixed(1)}/10</span>
            </div>
            <p class="improvement-gap">${escapeHtml(improvement.gap_description)}</p>
            ${improvement.recommendations && improvement.recommendations.length > 0 ? `
                <div class="improvement-recommendations">
                    <strong>Recomendaciones:</strong>
                    <ul>
                        ${improvement.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            ${improvement.priority ? `
                <span class="priority-badge priority-${improvement.priority.toLowerCase()}">${improvement.priority}</span>
            ` : ''}
        </div>
    `).join('');

    DOM.improvementsList.innerHTML = improvementsHTML;
}

function renderRedFlags(redFlags) {
    if (!redFlags || redFlags.length === 0) {
        DOM.redflagsList.innerHTML = '<p class="no-redflags">✓ No se detectaron red flags</p>';
        return;
    }

    const redFlagsHTML = redFlags.map(flag => `
        <div class="redflag-item">
            <div class="redflag-header">
                <span class="redflag-type">${escapeHtml(flag.type.replace(/_/g, ' '))}</span>
                <span class="severity-badge severity-${flag.severity.toLowerCase()}">${flag.severity}</span>
            </div>
            <p class="redflag-description">${escapeHtml(flag.description)}</p>
            ${flag.impact ? `<p class="redflag-impact">Impacto: ${escapeHtml(flag.impact)}</p>` : ''}
        </div>
    `).join('');

    DOM.redflagsList.innerHTML = redFlagsHTML;
}

function renderRecommendations(recommendations) {
    if (!recommendations) {
        return;
    }

    // Certificaciones
    const certifications = recommendations.certifications || [];
    DOM.recommendationsCertifications.innerHTML = certifications.length > 0
        ? certifications.map(cert => `<li>${escapeHtml(cert)}</li>`).join('')
        : '<li>No hay recomendaciones específicas de certificaciones</li>';

    // Training
    const training = recommendations.training || [];
    DOM.recommendationsTraining.innerHTML = training.length > 0
        ? training.map(t => `<li>${escapeHtml(t)}</li>`).join('')
        : '<li>No hay recomendaciones específicas de training</li>';

    // Áreas de experiencia
    const experience = recommendations.experience_areas || [];
    DOM.recommendationsExperience.innerHTML = experience.length > 0
        ? experience.map(exp => `<li>${escapeHtml(exp)}</li>`).join('')
        : '<li>No hay recomendaciones específicas de experiencia</li>';

    // Próximos roles
    const nextRoles = recommendations.next_role_suggestions || [];
    DOM.recommendationsNextRoles.innerHTML = nextRoles.length > 0
        ? nextRoles.map(role => `<li>${escapeHtml(role)}</li>`).join('')
        : '<li>No hay sugerencias de próximos roles</li>';
}

function renderInterviewQuestions(suggestions) {
    if (!suggestions) {
        return;
    }

    // Preguntas técnicas
    const technical = suggestions.technical_questions || [];
    DOM.interviewTechnical.innerHTML = technical.length > 0
        ? technical.map(q => `<li>${escapeHtml(q)}</li>`).join('')
        : '<li>No hay preguntas técnicas sugeridas</li>';

    // Preguntas de escenarios
    const scenario = suggestions.scenario_questions || [];
    DOM.interviewScenario.innerHTML = scenario.length > 0
        ? scenario.map(q => `<li>${escapeHtml(q)}</li>`).join('')
        : '<li>No hay preguntas de escenarios sugeridas</li>';

    // Preguntas de verificación
    const verification = suggestions.verification_questions || [];
    DOM.interviewVerification.innerHTML = verification.length > 0
        ? verification.map(q => `<li>${escapeHtml(q)}</li>`).join('')
        : '<li>No hay preguntas de verificación sugeridas</li>';
}

function renderMetadata(metadata) {
    if (!metadata) {
        return;
    }

    // Timestamp
    if (metadata.timestamp) {
        const date = new Date(metadata.timestamp);
        DOM.analysisTimestamp.textContent = date.toLocaleString();
    }

    // Duración de procesamiento
    if (metadata.processing_duration_ms) {
        const seconds = (metadata.processing_duration_ms / 1000).toFixed(2);
        DOM.processingDuration.textContent = `${seconds} segundos`;
    }

    // Confianza del parsing
    if (metadata.parsing_confidence !== undefined) {
        const percentage = (metadata.parsing_confidence * 100).toFixed(1);
        DOM.parsingConfidence.textContent = `${percentage}%`;
    }

    // Idioma del CV
    if (metadata.cv_language) {
        DOM.cvLanguage.textContent = metadata.cv_language === 'es' ? 'Español' : 'Inglés';
    }
}

// ========================================
// 11. Gráficos con Chart.js
// ========================================

function initCharts(data) {
    // Destruir gráficos anteriores si existen
    if (appState.charts.radar) {
        appState.charts.radar.destroy();
    }
    if (appState.charts.gauge) {
        appState.charts.gauge.destroy();
    }

    // Crear nuevos gráficos
    createRadarChart(data.detailed_scores);
    createGaugeChart(data.candidate_summary.total_score);
}

function createRadarChart(detailedScores) {
    if (!detailedScores) {
        console.warn('No hay scores detallados para el gráfico radar');
        return;
    }

    const ctx = DOM.radarChart.getContext('2d');

    // Extraer labels y valores
    const labels = Object.keys(detailedScores).map(formatLabel);
    const scores = Object.keys(detailedScores).map(key => detailedScores[key].score);

    appState.charts.radar = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Evaluación',
                data: scores,
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(59, 130, 246, 1)',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    min: 0,
                    max: 10,
                    beginAtZero: true,
                    ticks: {
                        stepSize: 2,
                        font: {
                            size: 11
                        }
                    },
                    pointLabels: {
                        font: {
                            size: 11,
                            weight: 'bold'
                        },
                        color: '#374151'
                    },
                    grid: {
                        color: '#e5e7eb'
                    },
                    angleLines: {
                        color: '#d1d5db'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Score: ${context.parsed.r.toFixed(1)}/10`;
                        }
                    }
                }
            }
        }
    });
}

function createGaugeChart(score) {
    const ctx = DOM.scoreGauge.getContext('2d');

    // Calcular porcentaje
    const percentage = (score / 10) * 100;

    // Determinar color según score
    let color;
    if (score >= 8) {
        color = '#10b981'; // Verde (success)
    } else if (score >= 6) {
        color = '#3b82f6'; // Azul (primary)
    } else if (score >= 4) {
        color = '#f59e0b'; // Amarillo (warning)
    } else {
        color = '#ef4444'; // Rojo (danger)
    }

    appState.charts.gauge = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [percentage, 100 - percentage],
                backgroundColor: [color, '#e5e7eb'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '75%',
            rotation: -90,
            circumference: 180,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    });
}

// ========================================
// 12. Helpers y Utilidades
// ========================================

function formatLabel(key) {
    // Convertir snake_case a Title Case
    return key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function escapeHtml(text) {
    if (typeof text !== 'string') {
        return text;
    }
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function showError(message) {
    DOM.errorMessage.textContent = message;
    DOM.errorMessage.style.display = 'block';
}

function hideError() {
    DOM.errorMessage.textContent = '';
    DOM.errorMessage.style.display = 'none';
}

function handleReset() {
    // Resetear estado
    appState.selectedFile = null;
    appState.analysisResult = null;

    // Limpiar inputs
    DOM.fileInput.value = '';
    DOM.fileName.textContent = '';
    DOM.roleTarget.value = '';
    DOM.language.value = 'es';
    DOM.analyzeBtn.disabled = true;

    // Destruir gráficos
    if (appState.charts.radar) {
        appState.charts.radar.destroy();
        appState.charts.radar = null;
    }
    if (appState.charts.gauge) {
        appState.charts.gauge.destroy();
        appState.charts.gauge = null;
    }

    // Volver a vista upload
    hideError();
    showView('upload');
}

// ========================================
// 13. Manejo de Errores Global
// ========================================

window.addEventListener('error', (event) => {
    console.error('Error global:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Promesa rechazada:', event.reason);
});

// ========================================
// Fin del archivo
// ========================================

console.log('App.js cargado correctamente');
