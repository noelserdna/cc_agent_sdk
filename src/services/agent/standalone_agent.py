"""Servicio standalone del Agent SDK.

Puede usarse sin FastAPI para integraciones directas.
Este módulo proporciona una interfaz simplificada para analizar CVs
usando el Agent SDK directamente, sin dependencias de FastAPI.
"""

from pathlib import Path

import structlog
from claude_agent_sdk import query, ClaudeAgentOptions

from src.core.config import Settings
from src.models.response import CVAnalysisResponse

logger = structlog.get_logger(__name__)


async def analyze_cv_with_agent(
    pdf_path: str | Path,
    language: str = "es",
    role_target: str | None = None,
    config: Settings | None = None,
) -> str:
    """Analiza un CV usando Agent SDK con Skills.

    Este es un servicio standalone que puede usarse sin FastAPI
    para integraciones directas con el Agent SDK.

    Args:
        pdf_path: Ruta al archivo PDF del CV
        language: Idioma del análisis ('es' o 'en')
        role_target: Rol objetivo opcional para análisis contextualizado
        config: Configuración opcional (usa default si no se proporciona)

    Returns:
        Texto de respuesta del análisis (formato JSON según skill)

    Raises:
        RuntimeError: Si la consulta al Agent SDK falla

    Example:
        >>> result = await analyze_cv_with_agent("cv.pdf", language="es")
        >>> print(result)
        {...JSON con el análisis...}
    """
    if config is None:
        config = Settings()

    logger.info(
        "standalone_agent_starting",
        pdf_path=str(pdf_path),
        language=language,
        role_target=role_target,
    )

    # Configure Agent SDK options
    options = ClaudeAgentOptions(
        cwd=config.agent_cwd,
        setting_sources=config.agent_setting_sources,
        allowed_tools=config.agent_allowed_tools,
        model=config.claude_model,
        max_tokens=config.claude_max_tokens,
    )

    # Build guided prompt for the 2-step flow
    if language == "es":
        prompt = f"""Analiza este CV de ciberseguridad usando el siguiente flujo:

1. Usa la skill 'pdf' para extraer el contenido del archivo: {pdf_path}
2. Usa la skill 'cybersecurity-cv-analyzer' para analizar el contenido extraído

Idioma del análisis: {language}
{f"Puesto objetivo: {role_target}" if role_target else ""}

Retorna el análisis completo en formato JSON estructurado según el esquema de la skill."""
    else:
        prompt = f"""Analyze this cybersecurity CV using the following flow:

1. Use the 'pdf' skill to extract the content from file: {pdf_path}
2. Use the 'cybersecurity-cv-analyzer' skill to analyze the extracted content

Analysis language: {language}
{f"Target role: {role_target}" if role_target else ""}

Return the complete analysis in structured JSON format according to the skill schema."""

    # Execute Agent SDK query
    logger.info("executing_standalone_query", model=config.claude_model)

    try:
        response_text = ""
        async for message in query(prompt=prompt, options=options):
            response_text += message

        logger.info(
            "standalone_query_complete",
            response_length=len(response_text),
        )

        return response_text

    except Exception as e:
        logger.error(
            "standalone_agent_error",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise RuntimeError(f"Agent SDK query failed: {e}") from e
