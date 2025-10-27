# 📋 **PROMPT COMPLETO PARA CREAR SKILL DE ANÁLISIS DE CVs DE CIBERSEGURIDAD**

```markdown
# Crear Skill: cybersecurity-cv-analyzer

Quiero crear un skill llamado "cybersecurity-cv-analyzer" que permita analizar y evaluar CVs de profesionales de ciberseguridad de forma estructurada, objetiva y consistente.

## 🎯 OBJETIVO PRINCIPAL

Profesionalizar y estandarizar la evaluación de talento en ciberseguridad, reduciendo el tiempo de screening de 30-45 minutos a 5 minutos, mientras se mejora la consistencia y objetividad en las evaluaciones.

## 📝 CASOS DE USO CONCRETOS

El skill debe poder manejar estas situaciones típicas:

1. "Analiza este CV para un rol de Pentester Senior"
2. "Compara estos 3 CVs para la posición de Cloud Security Architect"
3. "Identifica los gaps de este candidato para un rol SOC L2"
4. "Dame un radar chart de las competencias de este profesional"
5. "¿Qué certificaciones le recomendarías a este candidato para mejorar su perfil?"
6. "Evalúa si este CV cumple con los requisitos mínimos para un CISO"
7. "Extrae todas las herramientas técnicas y años de experiencia de este CV"
8. "Genera preguntas de entrevista basadas en los gaps detectados"
9. "¿Cuál es el percentil de este candidato comparado con el mercado?"
10. "Detecta red flags o inconsistencias en este CV"

## 🔧 FUNCIONALIDAD ESPERADA

### Capacidades Core

#### Parsing y Extracción:
- Parsear CVs en formato PDF, DOCX, y texto plano
- Extraer automáticamente información estructurada
- Identificar certificaciones usando regex patterns
- Detectar herramientas y tecnologías mencionadas
- Calcular años de experiencia (total y por área)
- Extraer formación académica y cursos
- Identificar contribuciones a la comunidad

#### Evaluación y Scoring:
- Evaluar 24 parámetros principales de ciberseguridad
- Generar puntuaciones objetivas (0-10) por parámetro
- Aplicar ponderaciones según el rol objetivo
- Detectar rol predominante automáticamente
- Determinar nivel de seniority (Junior/Mid/Senior/Principal/Expert)
- Calcular score total y por categorías

#### Análisis y Comparación:
- Identificar fortalezas principales (top 5)
- Detectar áreas de mejora prioritarias
- Encontrar red flags y inconsistencias
- Comparar múltiples candidatos objetivamente
- Benchmark contra datos de mercado
- Análisis de fit para rol específico

#### Generación de Outputs:
- Reportes detallados en JSON/HTML/Markdown
- Visualizaciones (radar charts, skill matrices)
- Recomendaciones de desarrollo personalizadas
- Preguntas de entrevista específicas
- Estimación de rango salarial
- Export para ATS/HRIS

## 📊 PARÁMETROS DE EVALUACIÓN (24 DIMENSIONES)

### Competencias Técnicas Core (1-12)

1. **CERTIFICACIONES**
   - Entry-Level: CompTIA Security+, Network+, CySA+
   - Ofensivas: CEH, OSCP, OSWP, OSEP, OSWE, OSCE3, PNPT, eCPPT
   - Defensivas: GCIH, GNFA, GCIA, GCFA, CCD, BTL1/BTL2
   - Cloud: AWS Security, Azure Security Engineer, GCP Security
   - Governance: CISSP, CISM, CISA, CRISC, CGEIT
   - Especializadas: GIAC, ISO 27001, CCSP, SABSA

2. **AÑOS DE EXPERIENCIA**
   - Experiencia total en IT
   - Experiencia específica en ciberseguridad
   - Experiencia en el rol actual
   - Experiencia en sectores regulados
   - Experiencia internacional
   - Progresión de carrera

3. **HABILIDADES OFENSIVAS (RED TEAM)**
   - Penetration Testing (web, mobile, infra, APIs)
   - Exploitation (buffer overflows, privilege escalation)
   - Social Engineering (phishing, vishing, physical)
   - Red Team Operations (C2, persistence, evasión)
   - Vulnerability Research (0-days, exploit dev)
   - Wireless Security (WiFi, Bluetooth, SDR)

4. **HABILIDADES DEFENSIVAS (BLUE TEAM)**
   - SOC Operations (monitoring, análisis, escalación)
   - Incident Response (contención, erradicación, recuperación)
   - Threat Hunting (proactivo, hypothesis-driven)
   - Digital Forensics (memoria, disco, red, móvil)
   - Malware Analysis (estático, dinámico, reverse)
   - Detection Engineering (reglas SIEM, correlaciones)

5. **GOBERNANZA Y COMPLIANCE**
   - Frameworks: ISO 27001/27002, NIST CSF, CIS, MITRE ATT&CK
   - Regulaciones: GDPR, PCI-DSS, HIPAA, SOX, CCPA, NIS2
   - Risk Management (evaluación, matrices, KRI/KPI)
   - Políticas y Procedimientos
   - Auditoría (interna, externa, gap analysis)
   - Privacy (DPO, PIAs, data governance)

6. **CLOUD SECURITY**
   - AWS: IAM, VPC, GuardDuty, Security Hub, CloudTrail
   - Azure: AAD, Sentinel, Defender, Key Vault
   - GCP: Cloud IAM, Cloud Armor, Security Command
   - Multi-cloud (CASB, CSPM, CWPP)
   - Container Security (Docker, Kubernetes)
   - IaC Security (Terraform, CloudFormation)

7. **HERRAMIENTAS TÉCNICAS**
   - SIEM: Splunk, QRadar, ArcSight, Elastic, Sentinel
   - EDR/XDR: CrowdStrike, SentinelOne, Cortex
   - Vulnerability: Nessus, Qualys, Rapid7, Tenable
   - Network: Firewalls, IDS/IPS, Wireshark
   - SOAR: Phantom, Demisto, TheHive
   - PAM: CyberArk, BeyondTrust

8. **PROGRAMACIÓN Y SCRIPTING**
   - Scripting: Python, Bash, PowerShell, Ruby
   - Compilados: C/C++, Go, Rust, Java, C#
   - Web: JavaScript, PHP, SQL, APIs REST
   - Automation: Ansible, Puppet, Chef
   - Desarrollo de herramientas
   - Regex y parsing

9. **ARQUITECTURA Y DISEÑO SEGURO**
   - Security by Design (threat modeling, STRIDE)
   - Zero Trust Architecture
   - Secure SDLC/DevSecOps
   - Network Segmentation
   - Identity Management (SSO, MFA, federation)
   - Encryption (PKI, HSM, key management)

10. **FORMACIÓN ACADÉMICA**
    - Grado universitario relevante
    - Especialización en Ciberseguridad
    - Formación continua (cursos, bootcamps)
    - Certificaciones académicas
    - Research/publicaciones
    - Formación militar/policial (si aplica)

11. **SOFT SKILLS**
    - Liderazgo y gestión de equipos
    - Comunicación (técnica y ejecutiva)
    - Gestión de stakeholders
    - Resolución de problemas
    - Gestión de proyectos
    - Negociación y gestión de conflictos

12. **IDIOMAS**
    - Inglés técnico (lectura/escritura/conversación)
    - Certificaciones de idioma
    - Otros idiomas relevantes
    - Comunicación técnica
    - Redacción de documentación

### Competencias Especializadas (13-24)

13. **DEVSECOPS & CI/CD SECURITY**
    - Pipeline Security (Jenkins, GitLab CI)
    - SAST/DAST/SCA Tools
    - Container Security
    - Secrets Management
    - IaC Scanning

14. **FORENSICS & MALWARE ANALYSIS**
    - Memory/Disk/Network Forensics
    - Reverse Engineering
    - Malware Sandboxing
    - Mobile Forensics
    - Log Analysis

15. **CRIPTOGRAFÍA APLICADA**
    - PKI Management
    - Algoritmos y protocolos
    - Key Management
    - Crypto Libraries
    - Quantum-Safe awareness

16. **OT/ICS SECURITY**
    - Protocolos industriales
    - SCADA Systems
    - IEC 62443, NERC CIP
    - Safety Systems
    - Risk Assessment OT

17. **MOBILE & IOT SECURITY**
    - iOS/Android Security
    - Mobile Testing
    - IoT Protocols
    - Firmware Analysis
    - MDM/MAM

18. **THREAT INTELLIGENCE**
    - CTI Platforms
    - OSINT Tools
    - Threat Feeds
    - Attribution
    - Strategic Intelligence

19. **CONTRIBUCIONES A LA COMUNIDAD**
    - CVEs descubiertos
    - Open Source projects
    - Bug Bounties
    - Speaking/conferencias
    - Blogging/artículos
    - Mentoring

20. **PUBLICACIONES Y RESEARCH**
    - Papers académicos
    - Libros/whitepapers
    - PoCs publicados
    - Patentes
    - Contribución a standards

21. **GESTIÓN Y ESTRATEGIA**
    - Presupuesto gestionado
    - Tamaño de equipo
    - Program Development
    - Vendor Management
    - Board Reporting
    - Métricas y KPIs

22. **GESTIÓN DE CRISIS**
    - Incidentes mayores gestionados
    - Crisis Communication
    - Coordinación multi-equipo
    - Tabletop Exercises
    - Regulatory Reporting

23. **TRANSFORMACIÓN Y CAMBIO**
    - Digital Transformation Security
    - Culture Change
    - Process Improvement
    - Innovation/R&D
    - Change Management

24. **ESPECIALIDADES NICHO**
    - Sector-Specific (Fintech, Healthcare, etc.)
    - Emerging Tech (AI/ML, Quantum, 5G)
    - Compliance específico
    - Geografía/regulación local

## 🗂️ RECURSOS QUE NECESITARÁ EL SKILL

### Scripts (scripts/)

1. **parse_cv.py**
   - Extractor universal de CVs (PDF/DOCX/TXT)
   - OCR para PDFs escaneados
   - Limpieza y normalización de texto
   - Detección de idioma

2. **score_calculator.py**
   - Motor de scoring con algoritmos de puntuación
   - Ponderaciones dinámicas por rol
   - Normalización de puntuaciones
   - Cálculo de percentiles

3. **keyword_extractor.py**
   - Detección de certificaciones (regex patterns)
   - Identificación de herramientas y tecnologías
   - Extracción de skills técnicas
   - Análisis de contexto

4. **compare_candidates.py**
   - Comparación multi-candidato
   - Ranking por criterios
   - Análisis de complementariedad
   - Matriz de decisión

5. **generate_report.py**
   - Generador de reportes HTML/PDF
   - Creación de visualizaciones
   - Export a JSON/CSV
   - Templates personalizables

6. **interview_generator.py**
   - Generación de preguntas técnicas
   - Preguntas basadas en gaps
   - Casos prácticos personalizados
   - Guías de evaluación

### Referencias (references/)

1. **scoring_rubric.md**
   ```markdown
   # Criterios de Puntuación Detallados
   
   ## Certificaciones (0-10)
   0-2: Sin certificaciones relevantes
   3-4: Certificaciones entry-level (Security+)
   5-6: Certificaciones intermedias (CEH, CySA+)
   7-8: Certificaciones avanzadas (OSCP, CISSP)
   9-10: Múltiples certificaciones expert (OSCE3, SANS Expert)
   
   [... criterios para los 24 parámetros ...]
   ```

2. **certifications_db.md**
   - Catálogo completo de certificaciones
   - Valor/peso de cada certificación
   - Equivalencias y prerequisitos
   - Fecha de expiración/renovación

3. **tools_taxonomy.md**
   - Taxonomía completa de herramientas
   - Categorización por función
   - Nivel de expertise requerido
   - Alternativas y equivalencias

4. **role_profiles.md**
   - Perfiles ideales por rol
   - Requirements mínimos y deseables
   - Ponderaciones específicas
   - Career paths típicos

5. **red_flags.md**
   - Patrones problemáticos
   - Inconsistencias temporales
   - Señales de alerta
   - Cómo evaluar gaps

6. **interview_questions.md**
   - Banco de +500 preguntas
   - Organizadas por área y nivel
   - Respuestas esperadas
   - Criterios de evaluación

7. **market_data.md**
   - Benchmarks salariales por rol/región
   - Demanda de skills
   - Tendencias del mercado
   - Datos de competitividad

### Assets (assets/)

1. **templates/report_template.html**
   - Template HTML profesional
   - Responsive design
   - Gráficos interactivos
   - Branding personalizable

2. **templates/radar_chart.html**
   - Visualización de competencias
   - Chart.js/D3.js integration
   - Comparación múltiple
   - Export a imagen

3. **data/market_benchmarks.json**
   - Datos actualizados de mercado
   - Percentiles por skill
   - Rangos salariales
   - Índices de demanda

4. **data/keywords_dictionary.json**
   - Diccionario de keywords
   - Sinónimos y variaciones
   - Acrónimos y abreviaciones
   - Términos en múltiples idiomas

## 📤 OUTPUT ESPERADO

### Estructura JSON Principal

```json
{
  "analysis_metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "cv_language": "en",
    "parsing_confidence": 0.95,
    "analysis_version": "1.0"
  },
  
  "candidate_summary": {
    "name": "John Doe",
    "email": "john.doe@email.com",
    "location": "Madrid, Spain",
    "total_score": 7.5,
    "percentile": 78,
    "detected_role": "Senior Security Engineer",
    "detected_specialization": "Cloud Security",
    "seniority_level": "Senior",
    "years_experience": {
      "total_it": 10,
      "cybersecurity": 6,
      "current_role": 2,
      "management": 1
    }
  },
  
  "detailed_scores": {
    "certifications": {
      "score": 8.0,
      "details": {
        "total_certs": 5,
        "active_certs": ["OSCP", "AWS Security", "CISSP"],
        "expired_certs": ["CEH"],
        "in_progress": ["OSEP"]
      }
    },
    "offensive_skills": {
      "score": 7.5,
      "details": {
        "pentesting": 8,
        "exploit_dev": 6,
        "red_team": 7,
        "tools": ["Burp Suite", "Metasploit", "Cobalt Strike"]
      }
    },
    "defensive_skills": {
      "score": 6.0,
      "details": {
        "soc_operations": 5,
        "incident_response": 7,
        "threat_hunting": 6,
        "forensics": 5
      }
    },
    "cloud_security": {
      "score": 8.5,
      "details": {
        "aws": 9,
        "azure": 7,
        "gcp": 6,
        "multicloud": true,
        "certifications": ["AWS Security Specialty"]
      }
    },
    "programming": {
      "score": 7.0,
      "details": {
        "languages": ["Python", "Go", "Bash", "PowerShell"],
        "scripting": 8,
        "development": 6,
        "automation": 7
      }
    },
    // ... resto de los 24 parámetros con estructura similar
  },
  
  "strengths": [
    {
      "area": "Cloud Security",
      "description": "Strong AWS expertise with Security Specialty certification",
      "score": 8.5,
      "market_value": "high"
    },
    {
      "area": "Offensive Security",
      "description": "OSCP certified with 5+ years pentesting experience",
      "score": 8.0,
      "market_value": "high"
    },
    {
      "area": "Automation",
      "description": "Proficient in Python and infrastructure automation",
      "score": 7.5,
      "market_value": "medium-high"
    }
  ],
  
  "improvement_areas": [
    {
      "area": "Governance & Compliance",
      "current_score": 4.0,
      "impact": "high",
      "recommendation": "Consider CISA or ISO 27001 Lead Auditor",
      "time_to_improve": "6-12 months"
    },
    {
      "area": "Incident Response",
      "current_score": 5.0,
      "impact": "medium",
      "recommendation": "GCIH certification and hands-on IR training",
      "time_to_improve": "3-6 months"
    }
  ],
  
  "red_flags": [
    {
      "type": "employment_gap",
      "severity": "medium",
      "description": "Unexplained 6-month gap between positions (2019)",
      "impact": "Requires clarification during interview"
    },
    {
      "type": "certification_mismatch",
      "severity": "low",
      "description": "Claims CISSP but only 4 years experience",
      "impact": "Verify associate status"
    }
  ],
  
  "role_fit_analysis": {
    "requested_role": "Cloud Security Architect",
    "fit_percentage": 72,
    "fit_category": "Good fit with development areas",
    "strengths_for_role": [
      "Strong cloud security background",
      "Architecture experience",
      "Multi-cloud knowledge"
    ],
    "gaps_for_role": [
      "Limited enterprise architecture experience",
      "No formal architecture certification",
      "Governance experience below expected level"
    ],
    "missing_requirements": [
      {
        "requirement": "5+ years architecture experience",
        "candidate_has": "2 years",
        "criticality": "high"
      },
      {
        "requirement": "TOGAF or SABSA",
        "candidate_has": "none",
        "criticality": "medium"
      }
    ],
    "exceeds_requirements": [
      "Programming skills beyond expectations",
      "Hands-on security testing experience"
    ]
  },
  
  "recommendations": {
    "immediate_actions": [
      "Complete AWS Security Specialty certification",
      "Gain hands-on experience with Kubernetes security"
    ],
    "short_term": [
      {
        "action": "Obtain CISSP certification",
        "timeframe": "3-6 months",
        "impact": "High - validates senior-level knowledge"
      },
      {
        "action": "Lead a cloud migration project",
        "timeframe": "6 months",
        "impact": "High - demonstrates architecture skills"
      }
    ],
    "long_term": [
      {
        "action": "Develop governance expertise",
        "timeframe": "12-18 months",
        "impact": "Critical for architect roles"
      }
    ],
    "learning_path": [
      "AWS Security Specialty → CCSP → SABSA",
      "Focus areas: Governance, Enterprise Architecture, Risk Management"
    ]
  },
  
  "interview_suggestions": {
    "technical_questions": [
      {
        "question": "Design a secure multi-region AWS architecture for a fintech application",
        "purpose": "Assess cloud architecture and security design skills",
        "expected_topics": ["VPC design", "KMS", "Compliance", "DR"]
      },
      {
        "question": "How would you implement Zero Trust in a hybrid cloud environment?",
        "purpose": "Evaluate modern security architecture understanding",
        "expected_topics": ["Microsegmentation", "Identity", "Policy enforcement"]
      }
    ],
    "behavioral_questions": [
      {
        "question": "Describe a security incident you've managed",
        "purpose": "Assess incident response experience",
        "follow_ups": ["Lessons learned", "Process improvements"]
      }
    ],
    "practical_exercises": [
      {
        "exercise": "Review and identify vulnerabilities in terraform code",
        "duration": "30 minutes",
        "skills_tested": ["IaC security", "Cloud security", "Code review"]
      }
    ],
    "red_flag_clarifications": [
      "Can you explain the gap in employment during 2019?",
      "Verify CISSP associate status and sponsorship"
    ]
  },
  
  "market_comparison": {
    "overall_percentile": 75,
    "percentile_by_area": {
      "technical_skills": 80,
      "certifications": 85,
      "experience": 70,
      "leadership": 60
    },
    "salary_analysis": {
      "market_range": {
        "min": 120000,
        "p25": 135000,
        "median": 150000,
        "p75": 165000,
        "max": 180000
      },
      "estimated_range": {
        "min": 140000,
        "max": 160000,
        "confidence": 0.75
      },
      "factors": {
        "positive": ["Cloud expertise", "OSCP", "Programming skills"],
        "negative": ["Limited architecture experience", "No team leadership"]
      }
    },
    "demand_index": "high",
    "competition_level": "medium",
    "market_timing": "favorable"
  },
  
  "visualization_data": {
    "radar_chart": {
      "labels": ["Offensive", "Defensive", "Cloud", "Governance", "DevSecOps", 
                 "Programming", "Leadership", "Architecture"],
      "current_scores": [7.5, 6.0, 8.5, 4.0, 7.0, 7.0, 5.0, 6.5],
      "role_requirements": [6.0, 7.0, 9.0, 7.0, 8.0, 6.0, 7.0, 9.0],
      "market_average": [5.5, 6.0, 6.5, 5.0, 5.5, 5.0, 4.5, 5.0]
    },
    "skills_heatmap": {
      "technical": {
        "pentesting": 8,
        "cloud_security": 8.5,
        "devsecops": 7,
        "forensics": 5,
        "governance": 4
      }
    },
    "experience_timeline": [
      {"year": 2014, "role": "IT Support", "company": "TechCorp"},
      {"year": 2016, "role": "Junior Security Analyst", "company": "SecureIT"},
      {"year": 2019, "role": "Security Engineer", "company": "CloudFirst"},
      {"year": 2022, "role": "Senior Security Engineer", "company": "Current"}
    ]
  },
  
  "report_metadata": {
    "confidence_score": 0.92,
    "data_completeness": 0.88,
    "parsing_issues": [],
    "assumptions_made": [
      "Years of experience calculated from first IT role",
      "Certification dates estimated from context"
    ],
    "version": "1.0",
    "generated_at": "2024-01-15T10:35:00Z"
  }
}
```

### Formatos de Salida Adicionales

1. **HTML Report**: Informe visual profesional con gráficos
2. **PDF Executive Summary**: Resumen ejecutivo de 1 página
3. **CSV Export**: Para integración con ATS/Excel
4. **Markdown Report**: Para documentación/wiki
5. **API Response**: Para integración con sistemas

## 🎨 VISUALIZACIONES REQUERIDAS

1. **Radar Chart Multidimensional**
   - 24 dimensiones o agrupadas por categorías
   - Comparación candidato vs rol vs mercado
   - Interactivo con tooltips

2. **Skills Heatmap**
   - Matriz de competencias con código de colores
   - Agrupación por categorías
   - Identificación visual de gaps

3. **Experience Timeline**
   - Visualización cronológica de carrera
   - Identificación de gaps
   - Progresión de roles

4. **Comparison Matrix**
   - Tabla comparativa multi-candidato
   - Ordenable por criterios
   - Highlighting de mejores/peores

5. **Fit Score Gauge**
   - Indicador visual de fit percentage
   - Código de colores (rojo/amarillo/verde)
   - Breakdown por categorías

## ⚙️ CONFIGURACIÓN Y PERSONALIZACIÓN

### Parámetros Configurables

```yaml
config:
  scoring:
    weights:
      technical_skills: 0.4
      experience: 0.3
      certifications: 0.2
      soft_skills: 0.1
    
  role_profiles:
    - name: "SOC Analyst L1"
      required_skills: ["SIEM", "Network Security"]
      required_certs: ["Security+"]
      min_experience: 0
    
    - name: "Cloud Security Architect"
      required_skills: ["AWS", "Architecture", "DevSecOps"]
      required_certs: ["AWS Security", "CISSP"]
      min_experience: 5
  
  parsing:
    languages: ["en", "es", "fr"]
    date_formats: ["MM/YYYY", "MM-YYYY", "Month YYYY"]
    
  output:
    include_salary: true
    include_market_data: true
    anonymize: false
```

### Flags y Opciones

```bash
# Uso básico
analyze_cv --file cv.pdf --role "Security Analyst"

# Con comparación
analyze_cv --files cv1.pdf cv2.pdf cv3.pdf --compare

# Con configuración custom
analyze_cv --file cv.pdf --config custom_config.yaml

# Output específico
analyze_cv --file cv.pdf --output json --include-viz
```

## 🛡️ CONSIDERACIONES DE SEGURIDAD Y PRIVACIDAD

1. **Protección de Datos**
   - Cumplimiento GDPR/CCPA
   - Anonimización de datos sensibles
   - Eliminación segura post-análisis
   - Logs de auditoría

2. **Sesgo y Fairness**
   - Algoritmos libres de sesgo
   - Evaluación objetiva basada en skills
   - Sin discriminación por edad/género/origen
   - Auditoría regular de resultados

3. **Transparencia**
   - Explicación de scoring
   - Criterios visibles
   - Posibilidad de dispute
   - Documentación completa

4. **Seguridad Técnica**
   - Sanitización de inputs
   - Prevención de injection
   - Encriptación de datos
   - Access control

## 📚 DOCUMENTACIÓN ADICIONAL NECESARIA

1. **User Guide**
   - Instalación y setup
   - Casos de uso comunes
   - Troubleshooting
   - FAQ

2. **Technical Documentation**
   - Arquitectura del sistema
   - API reference
   - Algoritmos de scoring
   - Data models

3. **Maintenance Guide**
   - Actualización de keywords
   - Nuevas certificaciones
   - Calibración de scoring
   - Performance tuning

## 🎯 USUARIOS OBJETIVO

1. **Technical Recruiters**
   - Screening inicial rápido
   - Comparación objetiva
   - Preguntas técnicas guiadas

2. **Hiring Managers**
   - Evaluación profunda
   - Fit analysis
   - Team composition

3. **HR Teams**
   - Análisis de mercado
   - Benchmarking salarial
   - Reporting

4. **Cybersecurity Professionals**
   - Self-assessment
   - Career planning
   - Skill gap analysis

## 📈 MÉTRICAS DE ÉXITO

- **Reducción tiempo screening**: 85% (45min → 5min)
- **Consistencia entre evaluadores**: >90%
- **Accuracy en role matching**: >80%
- **Satisfacción usuarios**: NPS >50
- **ROI**: 10x en primer año
- **Reducción turnover**: 30% en primeros 12 meses

## 🔄 MANTENIMIENTO Y ACTUALIZACIÓN

### Frecuencia de Actualización

- **Keywords y herramientas**: Mensual
- **Certificaciones**: Trimestral
- **Market data**: Trimestral
- **Scoring algorithms**: Semestral
- **Role profiles**: Anual

### Proceso de Mejora Continua

1. Recolección de feedback
2. Análisis de accuracy
3. Calibración de scoring
4. A/B testing
5. Actualización de modelos

## 💡 EJEMPLOS DE USO REAL

### Ejemplo 1: Screening Masivo
```
Input: 50 CVs para rol SOC Analyst
Output: Top 10 candidatos rankeados con fit score
Tiempo: 5 minutos total
```

### Ejemplo 2: Comparación Finalistas
```
Input: 3 CVs finalistas para CISO
Output: Matriz comparativa detallada + recomendación
Tiempo: 2 minutos
```

### Ejemplo 3: Development Plan
```
Input: CV de empleado actual
Output: Plan de desarrollo personalizado + certificaciones
Tiempo: 1 minuto
```

---

## INSTRUCCIONES FINALES

Por favor, crea este skill siguiendo las mejores prácticas del skill-creator:

1. **SKILL.md conciso** (<500 líneas) con instrucciones esenciales
2. **Scripts modulares y testeados** en Python 3.8+
3. **Referencias organizadas** por categoría
4. **Assets profesionales** para reportes
5. **Ejemplos concretos** de uso
6. **Documentación clara** sin redundancia

El skill debe ser:
- ✅ Objetivo y libre de sesgos
- ✅ Fácil de usar (plug & play)
- ✅ Mantenible y actualizable
- ✅ Escalable (1-1000 CVs)
- ✅ Integratable con sistemas existentes

Genera el skill completo listo para empaquetar con package_skill.py
```

---

Este prompt completo en markdown proporciona toda la información necesaria para crear un skill profesional y completo de análisis de CVs de ciberseguridad. Incluye todos los detalles técnicos, funcionales y de implementación necesarios.