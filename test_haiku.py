"""
Test script to evaluate Claude Haiku performance for CV analysis.
"""
import os
import asyncio
from pathlib import Path

# Override model to use Haiku
os.environ["CLAUDE_MODEL"] = "claude-3-5-haiku-20241022"

from src.services.pdf_extractor import PDFExtractor
from src.services.agent.cv_analyzer_agent import CVAnalyzerAgent
from src.core.config import Settings

print("=" * 80)
print("🧪 PRUEBA CON CLAUDE HAIKU: CV Cybersecurity Analyzer API")
print("=" * 80)
print()

async def main():
    # Load sample CV
    cv_path = Path("tests/fixtures/sample_cvs/test_cybersecurity_cv.txt")

    if not cv_path.exists():
        print(f"❌ Error: CV file not found at {cv_path}")
        return

    with open(cv_path, "r", encoding="utf-8") as f:
        cv_text = f.read()

    print(f"✅ CV cargado: {len(cv_text)} caracteres")
    print(f"📄 Extracto: {cv_text[:150]}...")
    print()

    # Calculate parsing confidence
    extractor = PDFExtractor()
    confidence = extractor.calculate_confidence(cv_text)
    print(f"✅ Parsing confidence calculado: {confidence:.2f}")
    print()

    # Initialize agent with Haiku
    settings = Settings()
    print(f"✅ Modelo configurado: {settings.claude_model}")
    print(f"✅ Max tokens: {settings.claude_max_tokens}")
    print()

    agent = CVAnalyzerAgent(settings)
    print("✅ Agente Haiku inicializado")
    print()

    print("🔍 Analizando CV con Claude Haiku...")
    print("   - Este modelo es más rápido que Sonnet")
    print("   - Esperamos <60 segundos de procesamiento")
    print()

    import time
    start_time = time.time()

    try:
        result = await agent.analyze_cv(
            cv_text=cv_text,
            parsing_confidence=confidence,
            role_target="Senior Security Analyst",
            language="es"
        )

        end_time = time.time()
        duration = end_time - start_time

        print("=" * 80)
        print("✅ ANÁLISIS COMPLETADO CON HAIKU")
        print("=" * 80)
        print()
        print(f"⏱️  TIEMPO DE PROCESAMIENTO: {duration:.1f} segundos")
        print()
        print("📊 RESUMEN DEL CANDIDATO")
        print("-" * 80)
        print(f"  Nombre:              {result.candidate_summary.name}")
        print(f"  Rol detectado:       {result.candidate_summary.detected_role}")
        print(f"  Nivel de seniority:  {result.candidate_summary.seniority_level}")
        print(f"  Score total:         {result.candidate_summary.total_score}/10.0")
        print(f"  Percentil:           {result.candidate_summary.percentile}%")
        print()

        print("💪 TOP 5 FORTALEZAS")
        print("-" * 80)
        for i, strength in enumerate(result.strengths[:5], 1):
            print(f"  {i}. {strength.area} ({strength.score}/10)")
            print(f"     {strength.description[:100]}...")
            print(f"     Valor de mercado: {strength.market_value}")
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
            print("  Ninguna red flag detectada")
            print()

        print("=" * 80)
        print("✅ COMPARACIÓN DE PERFORMANCE")
        print("=" * 80)
        print(f"  Sonnet 4.5:  ~123 segundos")
        print(f"  Haiku 3.5:   {duration:.1f} segundos")
        if duration < 123:
            improvement = ((123 - duration) / 123) * 100
            print(f"  Mejora:      {improvement:.1f}% más rápido ⚡")
        print()

        if duration < 30:
            print("✅ ¡SLA DE 30 SEGUNDOS CUMPLIDO!")
        else:
            print(f"⚠️  Aún por encima del SLA de 30s (faltan {duration-30:.1f}s)")
        print()

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
