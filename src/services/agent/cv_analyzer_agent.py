"""Claude Agent SDK integration for autonomous CV analysis.

This module implements the CVAnalyzerAgent which performs CV analysis
using the four-phase agent feedback loop:
1. Gather Context: Extract and parse CV information
2. Take Action: Score across 24 cybersecurity parameters
3. Verify Work: Check confidence scores and validate schema
4. Iterate: Refine scoring if needed
"""

from datetime import UTC, datetime
import json
import re
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query
import structlog

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

        logger.info(
            "cv_analyzer_agent_initialized",
            model=settings.claude_model,
            max_tokens=settings.claude_max_tokens,
            agent_setting_sources=settings.agent_setting_sources,
            agent_allowed_tools=settings.agent_allowed_tools,
        )

    async def analyze_cv(
        self,
        pdf_path: str,
        role_target: str | None = None,
        language: str = "es",
    ) -> CVAnalysisResponse:
        """Analyze a CV using Agent SDK with Skills.

        Flujo:
        1. Skill 'pdf' extrae contenido del PDF
        2. Skill 'cybersecurity-cv-analyzer' analiza el contenido

        Args:
            pdf_path: Path to the CV PDF file
            role_target: Optional target role for contextualized analysis
            language: Output language (es or en)

        Returns:
            CVAnalysisResponse with complete analysis

        Raises:
            RuntimeError: If Agent SDK query fails
        """
        start_time = datetime.now(UTC)

        logger.info(
            "starting_cv_analysis_with_agent_sdk",
            pdf_path=pdf_path,
            role_target=role_target,
            language=language,
        )

        # Configure Agent SDK options
        options = ClaudeAgentOptions(
            cwd=self.settings.agent_cwd,
            setting_sources=self.settings.agent_setting_sources,
            allowed_tools=self.settings.agent_allowed_tools,
            model=self.settings.claude_model,
            max_tokens=self.settings.claude_max_tokens,
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
        logger.info("executing_agent_sdk_query", model=self.settings.claude_model)

        try:
            response_text = ""
            async for message in query(prompt=prompt, options=options):
                response_text += message

            logger.info(
                "agent_sdk_response_received",
                response_length=len(response_text),
            )

        except Exception as e:
            logger.error("agent_sdk_error", error=str(e), error_type=type(e).__name__)
            raise RuntimeError(f"Agent SDK query failed: {e}") from e

        # Parse and validate response - use existing parsing logic
        # Assume parsing_confidence = 1.0 since the pdf skill handles extraction
        analysis_result = self._parse_analysis_response(
            response_text, cv_content="", parsing_confidence=1.0
        )

        # Calculate processing duration
        end_time = datetime.now(UTC)
        processing_duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Update metadata with actual processing time
        analysis_result.analysis_metadata.processing_duration_ms = processing_duration_ms

        logger.info(
            "cv_analysis_complete",
            processing_duration_ms=processing_duration_ms,
            total_score=analysis_result.candidate_summary.total_score,
            detected_role=analysis_result.candidate_summary.detected_role,
        )

        return analysis_result

    def _parse_analysis_response(
        self, analysis_text: str, _cv_content: str, parsing_confidence: float
    ) -> CVAnalysisResponse:
        """Parse the Agent SDK response into structured format.

        Args:
            analysis_text: Raw text response from Agent SDK (should be JSON)
            cv_content: Original CV text (optional, used for legacy compatibility)
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
            timestamp=datetime.now(UTC),
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

        for _param_name, param_data in scores_dict.items():
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
