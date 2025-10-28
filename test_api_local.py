#!/usr/bin/env python3
"""
Script de prueba local para el endpoint de análisis de CV.

Este script simula el flujo completo:
1. Carga el CV de texto de ejemplo
2. Simula la extracción de PDF
3. Llama al agente Claude para análisis
4. Muestra el resultado JSON

NOTA: Requiere ANTHROPIC_API_KEY configurado en .env
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config import settings
from src.services.agent.cv_analyzer_agent import CVAnalyzerAgent
from src.services.pdf_extractor import calculate_parsing_confidence


async def test_cv_analysis():
    """Test the CV analysis flow end-to-end."""

    print("=" * 80)
    print("🧪 PRUEBA END-TO-END: CV Cybersecurity Analyzer API")
    print("=" * 80)
    print()

    # Step 1: Load sample CV
    cv_path = Path("tests/fixtures/sample_cvs/test_cybersecurity_cv.txt")

    if not cv_path.exists():
        print(f"❌ ERROR: CV de prueba no encontrado en {cv_path}")
        return

    cv_text = cv_path.read_text(encoding="utf-8")
    print(f"✅ CV cargado: {len(cv_text)} caracteres")
    print(f"📄 Extracto: {cv_text[:150]}...")
    print()

    # Step 2: Calculate parsing confidence
    parsing_confidence = calculate_parsing_confidence(cv_text, page_count=1)
    print(f"✅ Parsing confidence calculado: {parsing_confidence:.2f}")
    print()

    # Step 3: Check API key configuration
    if not settings.anthropic_api_key or settings.anthropic_api_key.startswith("sk-ant-your-key"):
        print("⚠️  WARNING: ANTHROPIC_API_KEY no configurada o usa valor por defecto")
        print("   Por favor configura tu API key en el archivo .env")
        print()
        print("   Para obtener una API key:")
        print("   1. Ve a https://console.anthropic.com/")
        print("   2. Crea una cuenta o inicia sesión")
        print("   3. Ve a API Keys y genera una nueva key")
        print("   4. Añade en .env: ANTHROPIC_API_KEY=sk-ant-tu-key-aqui")
        print()
        print("❌ No se puede continuar sin API key válida")
        return

    print(f"✅ API key detectada: {settings.anthropic_api_key[:20]}...")
    print(f"✅ Modelo configurado: {settings.claude_model}")
    print()

    # Step 4: Initialize agent
    print("🤖 Inicializando agente Claude...")
    agent = CVAnalyzerAgent(settings)
    print("✅ Agente inicializado")
    print()

    # Step 5: Analyze CV
    print("🔍 Analizando CV (esto puede tardar 20-30 segundos)...")
    print("   - Enviando CV al agente Claude")
    print("   - Solicitando análisis de 24 parámetros")
    print("   - Calculando scores ponderados")
    print()

    try:
        result = await agent.analyze_cv(
            cv_text=cv_text,
            parsing_confidence=parsing_confidence,
            role_target="Senior Security Analyst",  # Opcional
            language="es"
        )

        print("=" * 80)
        print("✅ ANÁLISIS COMPLETADO")
        print("=" * 80)
        print()

        # Display results
        print("📊 RESUMEN DEL CANDIDATO")
        print("-" * 80)
        print(f"  Nombre:              {result.candidate_summary.name}")
        print(f"  Rol detectado:       {result.candidate_summary.detected_role}")
        print(f"  Nivel de seniority:  {result.candidate_summary.seniority_level}")
        print(f"  Score total:         {result.candidate_summary.total_score:.2f}/10.0")
        print(f"  Percentil:           {result.candidate_summary.percentile}%")
        print(f"  Años en IT:          {result.candidate_summary.years_experience.total_it}")
        print(f"  Años en seguridad:   {result.candidate_summary.years_experience.cybersecurity}")
        print()

        print("💪 TOP 5 FORTALEZAS")
        print("-" * 80)
        for i, strength in enumerate(result.strengths, 1):
            print(f"  {i}. {strength.area} ({strength.score:.1f}/10)")
            print(f"     {strength.description[:80]}...")
            print(f"     Valor de mercado: {strength.market_value}")
            print()

        print("📈 PUNTUACIONES DETALLADAS (24 PARÁMETROS)")
        print("-" * 80)
        scores_dict = result.detailed_scores.model_dump()

        # Show top 10 parameters by score
        param_list = [(name, data["score"], data["justification"][:60])
                      for name, data in scores_dict.items()]
        param_list.sort(key=lambda x: x[1], reverse=True)

        for name, score, justification in param_list[:10]:
            param_display = name.replace("_", " ").title()
            print(f"  {param_display:25} {score:.1f}/10  - {justification}...")

        print(f"\n  ... y {len(param_list) - 10} parámetros más")
        print()

        print("⚠️  RED FLAGS DETECTADAS")
        print("-" * 80)
        if result.red_flags:
            for flag in result.red_flags:
                print(f"  [{flag.severity.upper()}] {flag.type}")
                print(f"  {flag.description}")
                print(f"  Impacto: {flag.impact}")
                print()
        else:
            print("  ✅ No se detectaron red flags significativas")
            print()

        print("📚 ÁREAS DE MEJORA")
        print("-" * 80)
        if result.improvement_areas:
            for area in result.improvement_areas[:3]:  # Show top 3
                print(f"  [{area.priority.upper()}] {area.area} (Score actual: {area.current_score:.1f})")
                print(f"  {area.gap_description}")
                print(f"  Recomendaciones: {', '.join(area.recommendations[:2])}")
                print()
        else:
            print("  ✅ Perfil muy completo, sin áreas críticas de mejora")
            print()

        print("🎯 RECOMENDACIONES DE DESARROLLO")
        print("-" * 80)
        if result.recommendations.certifications:
            print(f"  Certificaciones: {', '.join(result.recommendations.certifications[:3])}")
        if result.recommendations.training:
            print(f"  Formación: {', '.join(result.recommendations.training[:2])}")
        if result.recommendations.next_role_suggestions:
            print(f"  Próximos roles: {', '.join(result.recommendations.next_role_suggestions[:2])}")
        print()

        print("💬 PREGUNTAS DE ENTREVISTA SUGERIDAS")
        print("-" * 80)
        print("  Técnicas:")
        for q in result.interview_suggestions.technical_questions[:2]:
            print(f"    - {q}")

        if result.interview_suggestions.scenario_questions:
            print("\n  Escenarios:")
            for q in result.interview_suggestions.scenario_questions[:2]:
                print(f"    - {q}")
        print()

        print("📋 METADATA DEL ANÁLISIS")
        print("-" * 80)
        print(f"  Timestamp:            {result.analysis_metadata.timestamp}")
        print(f"  Parsing confidence:   {result.analysis_metadata.parsing_confidence:.2f}")
        print(f"  Versión del análisis: {result.analysis_metadata.analysis_version}")
        print(f"  Duración:             {result.analysis_metadata.processing_duration_ms}ms")
        print()

        print("=" * 80)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print()
        print("💾 Para guardar el resultado completo en JSON:")
        print(f"   result_json = result.model_dump_json(indent=2)")
        print()

    except ValueError as e:
        print(f"❌ ERROR DE VALIDACIÓN: {e}")
        print()

    except RuntimeError as e:
        print(f"❌ ERROR DE RUNTIME: {e}")
        print()
        print("   Posibles causas:")
        print("   - API key de Anthropic inválida o expirada")
        print("   - Problemas de conectividad con la API de Claude")
        print("   - Límites de rate exceeded")
        print()

    except Exception as e:
        print(f"❌ ERROR INESPERADO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print()


if __name__ == "__main__":
    print()
    print("Iniciando prueba del CV Cybersecurity Analyzer API...")
    print()

    # Run async test
    asyncio.run(test_cv_analysis())

    print("Prueba finalizada.")
    print()
