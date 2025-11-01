"""Claude Agent SDK integration for autonomous CV analysis.

This module implements the CVAnalyzerAgent which performs CV analysis
using the four-phase agent feedback loop:
1. Gather Context: Extract and parse CV information
2. Take Action: Score across 24 cybersecurity parameters
3. Verify Work: Check confidence scores and validate schema
4. Iterate: Refine scoring if needed
"""

import json
import re
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog
from anthropic import AsyncAnthropic

from src.core.config import Settings
from src.models.candidate import CandidateSummary, YearsExperience
from src.models.improvement import ImprovementArea
from src.models.metadata import AnalysisMetadata
from src.models.recommendations import InterviewSuggestions, Recommendations
from src.models.redflag import RedFlag
from src.models.response import CVAnalysisResponse
from src.models.scores import CybersecurityParameter, DetailedScores
from src.models.strength import Strength

logger = structlog.get_logger(__name__)


class CVAnalyzerAgent:
    """Autonomous agent for CV analysis using Claude Agent SDK."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the CV analyzer agent.

        Args:
            settings: Application settings containing API keys and configuration
        """
        self.settings = settings

        # Configure HTTP timeout for Claude API calls
        # - connect: 10s to establish connection
        # - read: 60s to wait for response (model generation time)
        # - write: 10s to send request
        # - pool: 10s to acquire connection from pool
        timeout = httpx.Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=10.0,
        )

        self.client = AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=timeout,
        )
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens

        logger.info(
            "cv_analyzer_agent_initialized",
            model=self.model,
            max_tokens=self.max_tokens,
            timeout_read=60,
        )

    async def analyze_cv(
        self,
        cv_text: str,
        parsing_confidence: float,
        role_target: str | None = None,
        language: str = "es",
        tables: list[list[list[str]]] | None = None,
        urls: list[str] | None = None,
    ) -> CVAnalysisResponse:
        """Analyze a CV using the four-phase agent loop.

        Phase 1: Gather Context - Parse CV, extract metadata
        Phase 2: Take Action - Score across 24 parameters
        Phase 3: Verify Work - Validate schema
        Phase 4: Iterate - Refine scoring if needed

        Args:
            cv_text: Extracted text from the CV PDF
            parsing_confidence: Confidence score from PDF extraction (0.0-1.0)
            role_target: Optional target role for contextualized analysis
            language: Output language (es or en)
            tables: Optional list of extracted tables from PDF
            urls: Optional list of URLs extracted from PDF

        Returns:
            CVAnalysisResponse with complete analysis

        Raises:
            RuntimeError: If Claude API call fails after retries
        """
        start_time = datetime.now(timezone.utc)

        logger.info(
            "starting_cv_analysis",
            text_length=len(cv_text),
            parsing_confidence=parsing_confidence,
            role_target=role_target,
            language=language,
        )

        # Phase 1: Gather Context - Log parsing confidence for observability
        # Note: No longer blocking on low confidence - agent will determine sufficiency
        logger.info(
            "parsing_confidence_metadata",
            parsing_confidence=parsing_confidence,
            note="Agent will determine content sufficiency",
        )

        # Build the analysis prompt
        system_prompt = self._build_system_prompt(language)
        user_prompt = self._build_user_prompt(cv_text, role_target, language, tables, urls)

        # Phase 2: Take Action - Call Claude API for analysis
        logger.info("calling_claude_api", model=self.model)

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.3,  # Lower temperature for consistent analysis
            )

            analysis_text = response.content[0].text
            logger.info(
                "claude_api_response_received",
                response_length=len(analysis_text),
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )

        except Exception as e:
            logger.error("claude_api_error", error=str(e), error_type=type(e).__name__)
            raise RuntimeError(f"Claude API call failed: {e}") from e

        # Phase 3: Verify Work - Parse and validate the response
        # TODO: Implement structured output parsing
        # For now, we'll create a placeholder response
        analysis_result = self._parse_analysis_response(
            analysis_text, cv_text, parsing_confidence
        )

        # Phase 4: Iterate - Check if refinement is needed
        # (For MVP, we accept the first analysis)

        # Calculate processing duration
        end_time = datetime.now(timezone.utc)
        processing_duration_ms = int((end_time - start_time).total_seconds() * 1000)

        logger.info(
            "cv_analysis_complete",
            processing_duration_ms=processing_duration_ms,
            total_score=analysis_result.candidate_summary.total_score,
            detected_role=analysis_result.candidate_summary.detected_role,
        )

        return analysis_result

    def _build_system_prompt(self, language: str) -> str:
        """Build the system prompt for the Claude agent.

        Args:
            language: Output language (es or en)

        Returns:
            System prompt string
        """
        if language == "es":
            return """Eres un experto reclutador técnico especializado en ciberseguridad.
Analiza CVs de profesionales de ciberseguridad evaluando 24 parámetros específicos: certificaciones, habilidades ofensivas/defensivas, gobernanza, cloud security, herramientas, programación, arquitectura, educación, soft skills, idiomas, DevSecOps, forense digital, criptografía, OT/ICS, mobile/IoT, threat intelligence, contribuciones open source, publicaciones, gestión de equipos, gestión de crisis, transformación digital, especialidades de nicho, y experiencia.

Proporciona puntuaciones de 0.0 a 10.0 para cada parámetro con justificaciones detalladas basadas en evidencia concreta del CV."""
        else:
            return """You are an expert technical recruiter specialized in cybersecurity.
Analyze CVs of cybersecurity professionals evaluating 24 specific parameters: certifications, offensive/defensive skills, governance, cloud security, tools, programming, architecture, education, soft skills, languages, DevSecOps, digital forensics, cryptography, OT/ICS, mobile/IoT, threat intelligence, open source contributions, publications, team management, crisis management, digital transformation, niche specialties, and experience.

Provide scores from 0.0 to 10.0 for each parameter with detailed justifications based on concrete CV evidence."""

    def _build_user_prompt(
        self,
        cv_text: str,
        role_target: str | None,
        language: str,
        tables: list[list[list[str]]] | None = None,
        urls: list[str] | None = None,
    ) -> str:
        """Build the user prompt for CV analysis.

        Args:
            cv_text: Extracted CV text
            role_target: Optional target role
            language: Output language
            tables: Optional list of extracted tables
            urls: Optional list of extracted URLs

        Returns:
            User prompt string
        """
        if language == "es":
            base_prompt = f"""Analiza el siguiente CV de un profesional de ciberseguridad:

{cv_text}

"""
            # Add enriched content if available
            if tables:
                base_prompt += f"\n\nTABLAS ESTRUCTURADAS EXTRAÍDAS ({len(tables)} encontradas):\n"
                for i, table in enumerate(tables[:3], 1):  # Max 3 tables
                    base_prompt += f"Tabla {i}: {table}\n"
                if len(tables) > 3:
                    base_prompt += f"... y {len(tables) - 3} tabla(s) más.\n"

            if urls:
                base_prompt += f"\n\nENLACES EXTERNOS ENCONTRADOS ({len(urls)}):\n"
                base_prompt += "\n".join(urls[:10])  # Max 10 URLs
                if len(urls) > 10:
                    base_prompt += f"\n... y {len(urls) - 10} URL(s) más."
                base_prompt += "\n"

            if role_target:
                base_prompt += f"\nContexto: El candidato está siendo evaluado para el puesto de {role_target}.\n\n"

            base_prompt += """Responde ÚNICAMENTE con un objeto JSON válido (sin markdown, sin ```json).

Estructura JSON requerida:
{
  "candidate": {"name": "str", "detected_role": "str", "seniority_level": "Junior|Mid|Senior|Lead|Executive", "years_experience": {"total_it": num, "cybersecurity": num, "current_role": num}},
  "parameters": {
    "certifications": {"score": 0-10, "justification": "1-2 frases concisas"},
    "offensive_skills": {"score": 0-10, "justification": "1-2 frases concisas"},
    "defensive_skills": {"score": 0-10, "justification": "1-2 frases concisas"},
    "governance": {"score": 0-10, "justification": "1-2 frases concisas"},
    "cloud_security": {"score": 0-10, "justification": "1-2 frases concisas"},
    "tools": {"score": 0-10, "justification": "1-2 frases concisas"},
    "programming": {"score": 0-10, "justification": "1-2 frases concisas"},
    "architecture": {"score": 0-10, "justification": "1-2 frases concisas"},
    "education": {"score": 0-10, "justification": "1-2 frases concisas"},
    "soft_skills": {"score": 0-10, "justification": "1-2 frases concisas"},
    "languages": {"score": 0-10, "justification": "1-2 frases concisas"},
    "devsecops": {"score": 0-10, "justification": "1-2 frases concisas"},
    "forensics": {"score": 0-10, "justification": "1-2 frases concisas"},
    "cryptography": {"score": 0-10, "justification": "1-2 frases concisas"},
    "ot_ics": {"score": 0-10, "justification": "1-2 frases concisas"},
    "mobile_iot": {"score": 0-10, "justification": "1-2 frases concisas"},
    "threat_intel": {"score": 0-10, "justification": "1-2 frases concisas"},
    "contributions": {"score": 0-10, "justification": "1-2 frases concisas"},
    "publications": {"score": 0-10, "justification": "1-2 frases concisas"},
    "management": {"score": 0-10, "justification": "1-2 frases concisas"},
    "crisis": {"score": 0-10, "justification": "1-2 frases concisas"},
    "transformation": {"score": 0-10, "justification": "1-2 frases concisas"},
    "niche_specialties": {"score": 0-10, "justification": "1-2 frases concisas"},
    "experience": {"score": 0-10, "justification": "1-2 frases concisas"}
  },
  "strengths": [{"area": "str", "description": "texto breve", "score": 7-10, "market_value": "high|medium|low"}],
  "improvement_areas": [{"area": "str", "current_score": 0-10, "gap_description": "texto breve", "recommendations": ["acción"], "priority": "high|medium|low"}],
  "red_flags": [{"type": "employment_gap|certification_mismatch|skill_inconsistency|frequent_job_changes|missing_fundamentals|unclear_progression", "severity": "low|medium|high", "description": "texto breve", "impact": "texto breve"}],
  "recommendations": {"certifications": ["str"], "training": ["str"], "experience_areas": ["str"], "next_role_suggestions": ["str"]},
  "interview_questions": {"technical": ["pregunta"], "scenario": ["pregunta"], "verification": ["pregunta"]}
}

IMPORTANTE: Mantén las justificaciones breves y concisas (máximo 2 frases cada una). Sé específico y objetivo."""

        else:
            base_prompt = f"""Analyze the following cybersecurity professional's CV:

{cv_text}

"""
            # Add enriched content if available
            if tables:
                base_prompt += f"\n\nEXTRACTED STRUCTURED TABLES ({len(tables)} found):\n"
                for i, table in enumerate(tables[:3], 1):  # Max 3 tables
                    base_prompt += f"Table {i}: {table}\n"
                if len(tables) > 3:
                    base_prompt += f"... and {len(tables) - 3} more table(s).\n"

            if urls:
                base_prompt += f"\n\nEXTERNAL LINKS FOUND ({len(urls)}):\n"
                base_prompt += "\n".join(urls[:10])  # Max 10 URLs
                if len(urls) > 10:
                    base_prompt += f"\n... and {len(urls) - 10} more URL(s)."
                base_prompt += "\n"

            if role_target:
                base_prompt += f"\nContext: The candidate is being evaluated for the position of {role_target}.\n\n"

            base_prompt += """Respond ONLY with a valid JSON object (no markdown, no ```json).

Required JSON structure:
{
  "candidate": {"name": "str", "detected_role": "str", "seniority_level": "Junior|Mid|Senior|Lead|Executive", "years_experience": {"total_it": num, "cybersecurity": num, "current_role": num}},
  "parameters": {
    "certifications": {"score": 0-10, "justification": "1-2 concise sentences"},
    "offensive_skills": {"score": 0-10, "justification": "1-2 concise sentences"},
    "defensive_skills": {"score": 0-10, "justification": "1-2 concise sentences"},
    "governance": {"score": 0-10, "justification": "1-2 concise sentences"},
    "cloud_security": {"score": 0-10, "justification": "1-2 concise sentences"},
    "tools": {"score": 0-10, "justification": "1-2 concise sentences"},
    "programming": {"score": 0-10, "justification": "1-2 concise sentences"},
    "architecture": {"score": 0-10, "justification": "1-2 concise sentences"},
    "education": {"score": 0-10, "justification": "1-2 concise sentences"},
    "soft_skills": {"score": 0-10, "justification": "1-2 concise sentences"},
    "languages": {"score": 0-10, "justification": "1-2 concise sentences"},
    "devsecops": {"score": 0-10, "justification": "1-2 concise sentences"},
    "forensics": {"score": 0-10, "justification": "1-2 concise sentences"},
    "cryptography": {"score": 0-10, "justification": "1-2 concise sentences"},
    "ot_ics": {"score": 0-10, "justification": "1-2 concise sentences"},
    "mobile_iot": {"score": 0-10, "justification": "1-2 concise sentences"},
    "threat_intel": {"score": 0-10, "justification": "1-2 concise sentences"},
    "contributions": {"score": 0-10, "justification": "1-2 concise sentences"},
    "publications": {"score": 0-10, "justification": "1-2 concise sentences"},
    "management": {"score": 0-10, "justification": "1-2 concise sentences"},
    "crisis": {"score": 0-10, "justification": "1-2 concise sentences"},
    "transformation": {"score": 0-10, "justification": "1-2 concise sentences"},
    "niche_specialties": {"score": 0-10, "justification": "1-2 concise sentences"},
    "experience": {"score": 0-10, "justification": "1-2 concise sentences"}
  },
  "strengths": [{"area": "str", "description": "brief text", "score": 7-10, "market_value": "high|medium|low"}],
  "improvement_areas": [{"area": "str", "current_score": 0-10, "gap_description": "brief text", "recommendations": ["action"], "priority": "high|medium|low"}],
  "red_flags": [{"type": "employment_gap|certification_mismatch|skill_inconsistency|frequent_job_changes|missing_fundamentals|unclear_progression", "severity": "low|medium|high", "description": "brief text", "impact": "brief text"}],
  "recommendations": {"certifications": ["str"], "training": ["str"], "experience_areas": ["str"], "next_role_suggestions": ["str"]},
  "interview_questions": {"technical": ["question"], "scenario": ["question"], "verification": ["question"]}
}

IMPORTANT: Keep justifications brief and concise (maximum 2 sentences each). Be specific and objective."""

        return base_prompt

    def _parse_analysis_response(
        self, analysis_text: str, cv_text: str, parsing_confidence: float
    ) -> CVAnalysisResponse:
        """Parse the Claude API response into structured format.

        Args:
            analysis_text: Raw text response from Claude (should be JSON)
            cv_text: Original CV text
            parsing_confidence: Confidence score from PDF extraction

        Returns:
            Structured CVAnalysisResponse

        Raises:
            ValueError: If JSON parsing fails or required fields are missing
        """
        logger.info("parsing_claude_response", response_length=len(analysis_text))

        # Clean the response - remove markdown code blocks if present
        cleaned_text = analysis_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
        elif cleaned_text.startswith("```"):
            cleaned_text = re.sub(r"^```\s*", "", cleaned_text)
            cleaned_text = re.sub(r"\s*```$", "", cleaned_text)

        # Parse JSON
        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error("json_parse_error", error=str(e), text_preview=cleaned_text[:500])
            raise ValueError(f"Failed to parse Claude response as JSON: {e}") from e

        # Extract candidate data
        candidate_data = data.get("candidate", {})
        years_exp = candidate_data.get("years_experience", {})

        # Create candidate summary
        candidate_summary = CandidateSummary(
            name=candidate_data.get("name", "Unknown"),
            total_score=0.0,  # Will be calculated below
            percentile=0,  # Will be calculated below
            detected_role=candidate_data.get("detected_role", "Unknown"),
            seniority_level=candidate_data.get("seniority_level", "Mid"),
            years_experience=YearsExperience(
                total_it=float(years_exp.get("total_it", 0.0)),
                cybersecurity=float(years_exp.get("cybersecurity", 0.0)),
                current_role=float(years_exp.get("current_role", 0.0)),
            ),
        )

        # Parse the 24 parameters
        detailed_scores = self._parse_parameters(data.get("parameters", {}))

        # Calculate weighted total score
        total_score = self._calculate_weighted_score(detailed_scores)
        candidate_summary.total_score = total_score

        # Calculate percentile (simplified - in production would use market benchmarks)
        candidate_summary.percentile = min(100, max(0, int(total_score * 10)))

        # Parse strengths (ensure exactly 5)
        strengths_data = data.get("strengths", [])
        strengths = self._parse_strengths(strengths_data, detailed_scores)

        # Parse improvement areas
        improvement_areas_data = data.get("improvement_areas", [])
        improvement_areas = [
            ImprovementArea(
                area=item.get("area", "Unknown"),
                current_score=float(item.get("current_score", 0.0)),
                gap_description=item.get("gap_description", ""),
                recommendations=item.get("recommendations", []),
                priority=item.get("priority", "medium"),
            )
            for item in improvement_areas_data
        ]

        # Parse red flags
        red_flags_data = data.get("red_flags", [])
        red_flags = [
            RedFlag(
                type=item.get("type", "skill_inconsistency"),
                severity=item.get("severity", "medium"),
                description=item.get("description", ""),
                impact=item.get("impact", ""),
            )
            for item in red_flags_data
        ]

        # Parse recommendations
        recommendations_data = data.get("recommendations", {})
        recommendations = Recommendations(
            certifications=recommendations_data.get("certifications", []),
            training=recommendations_data.get("training", []),
            experience_areas=recommendations_data.get("experience_areas", []),
            next_role_suggestions=recommendations_data.get("next_role_suggestions", []),
        )

        # Parse interview questions
        interview_data = data.get("interview_questions", {})
        interview_suggestions = InterviewSuggestions(
            technical_questions=interview_data.get("technical", []),
            scenario_questions=interview_data.get("scenario", []),
            verification_questions=interview_data.get("verification", []),
        )

        # Create metadata
        metadata = AnalysisMetadata(
            timestamp=datetime.now(timezone.utc),
            parsing_confidence=parsing_confidence,
            cv_language="es",  # TODO: detect from CV text
            analysis_version="1.0.0",
            processing_duration_ms=0,  # Will be updated by caller
        )

        logger.info(
            "parse_complete",
            total_score=total_score,
            strengths_count=len(strengths),
            improvement_areas_count=len(improvement_areas),
            red_flags_count=len(red_flags),
        )

        return CVAnalysisResponse(
            analysis_metadata=metadata,
            candidate_summary=candidate_summary,
            detailed_scores=detailed_scores,
            strengths=strengths,
            improvement_areas=improvement_areas,
            red_flags=red_flags,
            recommendations=recommendations,
            interview_suggestions=interview_suggestions,
        )

    def _parse_parameters(self, parameters_data: dict[str, Any]) -> DetailedScores:
        """Parse the 24 cybersecurity parameters from JSON data.

        Args:
            parameters_data: Dictionary containing parameter scores from Claude

        Returns:
            DetailedScores with all 24 parameters

        Raises:
            ValueError: If required parameters are missing
        """
        # Parameter weights as defined in data-model.md
        weights = {
            "certifications": 1.2,
            "offensive_skills": 1.1,
            "defensive_skills": 1.1,
            "governance": 1.0,
            "cloud_security": 1.1,
            "tools": 1.0,
            "programming": 1.0,
            "architecture": 1.0,
            "education": 0.9,
            "soft_skills": 1.0,
            "languages": 0.8,
            "devsecops": 1.0,
            "forensics": 1.0,
            "cryptography": 1.0,
            "ot_ics": 1.0,
            "mobile_iot": 1.0,
            "threat_intel": 1.0,
            "contributions": 0.9,
            "publications": 0.9,
            "management": 1.0,
            "crisis": 1.1,
            "transformation": 1.0,
            "niche_specialties": 1.0,
            "experience": 1.2,
        }

        scores_dict: dict[str, CybersecurityParameter] = {}

        for param_name, weight in weights.items():
            param_data = parameters_data.get(param_name, {})

            scores_dict[param_name] = CybersecurityParameter(
                score=float(param_data.get("score", 0.0)),
                justification=param_data.get("justification", "No data provided"),
                evidence=param_data.get("evidence", []),
                weight=weight,
            )

        return DetailedScores(**scores_dict)

    def _calculate_weighted_score(self, detailed_scores: DetailedScores) -> float:
        """Calculate the weighted total score from all 24 parameters.

        Args:
            detailed_scores: DetailedScores object with all parameters

        Returns:
            Weighted average score (0.0-10.0)
        """
        total_weighted = 0.0
        total_weight = 0.0

        # Get all parameter scores as dictionary
        scores_dict = detailed_scores.model_dump()

        for param_name, param_data in scores_dict.items():
            score = param_data["score"]
            weight = param_data["weight"]
            total_weighted += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        weighted_avg = total_weighted / total_weight
        return round(weighted_avg, 2)

    def _parse_strengths(
        self, strengths_data: list[dict[str, Any]], detailed_scores: DetailedScores
    ) -> list[Strength]:
        """Parse strengths, ensuring exactly 5 are returned.

        Args:
            strengths_data: List of strength dictionaries from Claude
            detailed_scores: Detailed scores to fall back on if needed

        Returns:
            List of exactly 5 Strength objects
        """
        strengths: list[Strength] = []

        # Parse provided strengths, filtering out scores < 7.0
        for item in strengths_data:
            score = float(item.get("score", 0.0))
            # Only include strengths with score >= 7.0 (Strength model requirement)
            if score >= 7.0:
                strengths.append(
                    Strength(
                        area=item.get("area", "Unknown"),
                        description=item.get("description", ""),
                        score=score,
                        market_value=item.get("market_value", "medium"),
                    )
                )

        # If we have exactly 5, return them
        if len(strengths) == 5:
            return strengths

        # If we have more than 5, take top 5 by score
        if len(strengths) > 5:
            strengths.sort(key=lambda x: x.score, reverse=True)
            return strengths[:5]

        # If we have fewer than 5, generate from top-scoring parameters
        scores_dict = detailed_scores.model_dump()
        param_scores = [
            (name, data["score"], data["justification"])
            for name, data in scores_dict.items()
        ]
        param_scores.sort(key=lambda x: x[1], reverse=True)

        # Add strengths from top parameters until we have 5
        existing_areas = {s.area.lower() for s in strengths}

        for param_name, score, justification in param_scores:
            if len(strengths) >= 5:
                break

            # Format parameter name nicely
            area_name = param_name.replace("_", " ").title()

            if area_name.lower() not in existing_areas and score >= 7.0:
                strengths.append(
                    Strength(
                        area=area_name,
                        description=justification[:100] + "..." if len(justification) > 100 else justification,
                        score=score,
                        market_value="medium",
                    )
                )
                existing_areas.add(area_name.lower())

        # If still not enough, pad with lower-scoring parameters
        for param_name, score, justification in param_scores:
            if len(strengths) >= 5:
                break

            area_name = param_name.replace("_", " ").title()
            if area_name.lower() not in existing_areas:
                strengths.append(
                    Strength(
                        area=area_name,
                        description=justification[:100] + "..." if len(justification) > 100 else justification,
                        score=score,
                        market_value="low",
                    )
                )

        return strengths[:5]
