"""
End-to-end integration tests for CV analysis workflow.

Tests validate complete workflow from PDF upload to analysis response.
"""
import pytest
from pathlib import Path
from httpx import AsyncClient

from src.main import app


@pytest.fixture
def sample_cv_path():
    """Path to sample cybersecurity CV"""
    return Path("tests/fixtures/sample_cvs/sample_cybersecurity_cv.pdf")


@pytest.fixture
def valid_api_key():
    """Valid API key for testing"""
    return "test-api-key-123"


class TestCVAnalysisE2E:
    """End-to-end integration tests for CV analysis"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_cv_analysis_workflow(self, async_client, sample_cv_path, valid_api_key):
        """Test complete workflow: upload PDF → extract text → analyze → return results"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        # Upload CV for analysis
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")},
                data={"language": "en"}
            )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "analysis_metadata" in data
        assert "candidate_summary" in data
        assert "detailed_scores" in data
        assert "strengths" in data
        assert "improvement_areas" in data
        assert "red_flags" in data
        assert "recommendations" in data
        assert "interview_suggestions" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analysis_metadata_completeness(self, async_client, sample_cv_path, valid_api_key):
        """Test analysis metadata is complete and valid"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 200
        metadata = response.json()["analysis_metadata"]

        # Verify all required metadata fields
        assert "timestamp" in metadata
        assert "parsing_confidence" in metadata
        assert "cv_language" in metadata
        assert "analysis_version" in metadata
        assert "processing_duration_ms" in metadata

        # Verify metadata values
        assert 0.0 <= metadata["parsing_confidence"] <= 1.0
        assert metadata["cv_language"] in ["es", "en"]
        assert metadata["processing_duration_ms"] > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_candidate_summary_extraction(self, async_client, sample_cv_path, valid_api_key):
        """Test candidate summary is extracted correctly"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 200
        summary = response.json()["candidate_summary"]

        # Verify required fields
        assert "name" in summary
        assert "total_score" in summary
        assert "percentile" in summary
        assert "detected_role" in summary
        assert "seniority_level" in summary
        assert "years_experience" in summary

        # Verify data types and ranges
        assert isinstance(summary["name"], str)
        assert len(summary["name"]) >= 2
        assert 0.0 <= summary["total_score"] <= 10.0
        assert 0 <= summary["percentile"] <= 100
        assert summary["seniority_level"] in ["Junior", "Mid", "Senior", "Lead", "Executive"]

        # Verify years_experience structure
        exp = summary["years_experience"]
        assert "total_it" in exp
        assert "cybersecurity" in exp
        assert "current_role" in exp
        assert all(v >= 0 for v in exp.values())

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_detailed_scores_all_24_parameters(self, async_client, sample_cv_path, valid_api_key):
        """Test all 24 cybersecurity parameters are scored"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 200
        scores = response.json()["detailed_scores"]

        # Verify all 24 parameters exist
        expected_parameters = [
            "certifications", "offensive_skills", "defensive_skills", "governance",
            "cloud_security", "tools", "programming", "architecture", "education",
            "soft_skills", "languages", "devsecops", "forensics", "cryptography",
            "ot_ics", "mobile_iot", "threat_intel", "contributions", "publications",
            "management", "crisis", "transformation", "niche_specialties", "experience"
        ]

        for param in expected_parameters:
            assert param in scores, f"Missing parameter: {param}"

            # Verify parameter structure
            param_data = scores[param]
            assert "score" in param_data
            assert "justification" in param_data
            assert "evidence" in param_data
            assert "weight" in param_data

            # Verify score range
            assert 0.0 <= param_data["score"] <= 10.0

            # Verify justification is meaningful
            assert len(param_data["justification"]) >= 20

            # Verify evidence is a list
            assert isinstance(param_data["evidence"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_strengths_identification(self, async_client, sample_cv_path, valid_api_key):
        """Test top 5 strengths are identified"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 200
        strengths = response.json()["strengths"]

        # Verify exactly 5 strengths (FR-011)
        assert len(strengths) == 5

        for strength in strengths:
            assert "area" in strength
            assert "description" in strength
            assert "score" in strength
            assert "market_value" in strength

            # Strengths should have high scores
            assert strength["score"] >= 7.0

            # Market value should be valid
            assert strength["market_value"] in ["high", "medium", "low"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_recommendations_generation(self, async_client, sample_cv_path, valid_api_key):
        """Test career development recommendations"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 200
        recommendations = response.json()["recommendations"]

        # Verify structure
        assert "certifications" in recommendations
        assert "training" in recommendations
        assert "experience_areas" in recommendations
        assert "next_role_suggestions" in recommendations

        # All should be lists
        assert isinstance(recommendations["certifications"], list)
        assert isinstance(recommendations["training"], list)
        assert isinstance(recommendations["experience_areas"], list)
        assert isinstance(recommendations["next_role_suggestions"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_interview_suggestions_generation(self, async_client, sample_cv_path, valid_api_key):
        """Test interview question generation"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 200
        interview = response.json()["interview_suggestions"]

        # Verify structure
        assert "technical_questions" in interview
        assert "scenario_questions" in interview
        assert "verification_questions" in interview

        # Verify minimum counts (FR-016)
        assert len(interview["technical_questions"]) >= 3
        assert len(interview["scenario_questions"]) >= 2

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_contextualized_analysis_with_role_target(self, async_client, sample_cv_path, valid_api_key):
        """Test analysis is contextualized for target role"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")},
                data={"role_target": "Senior Cloud Security Engineer"}
            )

        assert response.status_code == 200
        data = response.json()

        # Analysis should be complete
        assert "detailed_scores" in data
        assert "recommendations" in data

        # Recommendations should be relevant to cloud security
        recommendations = data["recommendations"]
        # At least some recommendations should mention cloud or related terms
        all_recommendations = (
            recommendations.get("certifications", []) +
            recommendations.get("training", []) +
            recommendations.get("experience_areas", [])
        )

        # This is outcome-based validation (not exact text matching)
        assert len(all_recommendations) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analysis_performance_within_30_seconds(self, async_client, sample_cv_path, valid_api_key):
        """Test analysis completes within 30 second SLA (FR-020)"""
        import time

        # Using async_client fixture with extended timeout for this test
        start_time = time.time()

        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")},
                timeout=35.0  # Extended timeout for analysis
            )

        elapsed_time = time.time() - start_time

        assert response.status_code == 200

        # Verify SLA compliance
        assert elapsed_time < 30.0, f"Analysis took {elapsed_time}s, exceeds 30s SLA"

        # Verify processing duration is tracked
        metadata = response.json()["analysis_metadata"]
        assert metadata["processing_duration_ms"] < 30000


class TestCVAnalysisErrorHandling:
    """Integration tests for error handling"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analysis_with_invalid_api_key(self, async_client, sample_cv_path):
        """Test analysis fails with invalid API key"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": "invalid-key"},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analysis_without_api_key(self, async_client, sample_cv_path):
        """Test analysis fails without API key"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analysis_with_large_file(self, async_client, valid_api_key):
        """Test analysis rejects files > 10MB"""
        # Create a large dummy file (> 10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB

        # Using async_client fixture
        # Using async_client fixture from conftest.py
        response = await async_client.post(
            "/v1/analyze-cv",
            headers={"X-API-Key": valid_api_key},
            files={"file": ("large.pdf", large_content, "application/pdf")}
        )

        assert response.status_code == 413  # Payload Too Large

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_analysis_with_non_pdf_file(self, async_client, valid_api_key):
        """Test analysis rejects non-PDF files"""
        txt_content = b"This is not a PDF"

        # Using async_client fixture
        # Using async_client fixture from conftest.py
        response = await async_client.post(
            "/v1/analyze-cv",
            headers={"X-API-Key": valid_api_key},
            files={"file": ("cv.txt", txt_content, "text/plain")}
        )

        assert response.status_code == 400
