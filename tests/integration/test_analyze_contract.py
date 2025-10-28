"""
Contract tests for POST /analyze-cv endpoint.

Validates API contract matches OpenAPI specification.
Tests request/response schema validation using Pydantic models.
"""
import pytest
from pathlib import Path
import json

from src.models.response import CVAnalysisResponse
from pydantic import ValidationError


@pytest.fixture
def sample_cv_path():
    """Path to sample cybersecurity CV"""
    return Path("tests/fixtures/sample_cvs/sample_cybersecurity_cv.pdf")


@pytest.fixture
def valid_api_key():
    """Valid API key for testing"""
    return "test-api-key-123"


@pytest.fixture
def openapi_spec_path():
    """Path to OpenAPI specification"""
    return Path("specs/001-cv-cybersecurity-analyzer-api/contracts/openapi.yaml")


class TestAnalyzeEndpointContract:
    """Contract tests for /analyze-cv endpoint"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_endpoint_exists(self, async_client, valid_api_key):
        """Test /analyze-cv endpoint exists and accepts POST"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        # OPTIONS request to check endpoint
        response = await async_client.options("/v1/analyze-cv")

        # Endpoint should exist (not 404)
        assert response.status_code != 404

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_request_requires_multipart_form_data(self, async_client, sample_cv_path, valid_api_key):
        """Test endpoint requires multipart/form-data"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        # Try sending JSON instead of multipart
        response = await async_client.post(
            "/v1/analyze-cv",
            headers={
                "X-API-Key": valid_api_key,
                "Content-Type": "application/json"
            },
            json={"file": "not-a-file"}
        )

        # Should fail with 400 or 422 (validation error)
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_request_requires_file_field(self, async_client, valid_api_key):
        """Test request requires 'file' field"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        # Send request without file field
        response = await async_client.post(
            "/v1/analyze-cv",
            headers={"X-API-Key": valid_api_key},
            data={"language": "en"}  # No file field
        )

        assert response.status_code in [400, 422]
        error_detail = response.json()
        assert "file" in str(error_detail).lower()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_request_validates_file_type(self, async_client, valid_api_key):
        """Test request validates file is PDF"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        # Send non-PDF file
        response = await async_client.post(
            "/v1/analyze-cv",
            headers={"X-API-Key": valid_api_key},
            files={"file": ("test.txt", b"not a pdf", "text/plain")}
        )

        assert response.status_code == 400
        error_detail = response.json()
        assert "pdf" in str(error_detail).lower()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_request_validates_file_size(self, async_client, valid_api_key):
        """Test request validates file size <= 10MB"""
        # Create file > 10MB
        large_content = b"x" * (11 * 1024 * 1024)

        # Using async_client fixture
        # Using async_client fixture from conftest.py
        response = await async_client.post(
            "/v1/analyze-cv",
            headers={"X-API-Key": valid_api_key},
            files={"file": ("large.pdf", large_content, "application/pdf")}
        )

        assert response.status_code == 413

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_request_accepts_optional_role_target(self, async_client, sample_cv_path, valid_api_key):
        """Test request accepts optional role_target parameter"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")},
                data={"role_target": "Cloud Security Engineer"}
            )

        # Should accept the parameter
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_request_validates_role_target_length(self, async_client, sample_cv_path, valid_api_key):
        """Test role_target must be 3-100 characters"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        # Too short (< 3 chars)
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")},
                data={"role_target": "AB"}  # Only 2 chars
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_request_accepts_optional_language(self, async_client, sample_cv_path, valid_api_key):
        """Test request accepts optional language parameter"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        for language in ["es", "en"]:
            with open(sample_cv_path, 'rb') as cv_file:
                response = await async_client.post(
                    "/v1/analyze-cv",
                    headers={"X-API-Key": valid_api_key},
                    files={"file": ("cv.pdf", cv_file, "application/pdf")},
                    data={"language": language}
                )

            assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_request_validates_language_enum(self, async_client, sample_cv_path, valid_api_key):
        """Test language must be 'es' or 'en'"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")},
                data={"language": "fr"}  # Invalid language
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_status_code_success(self, async_client, sample_cv_path, valid_api_key):
        """Test successful response returns 200 OK"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_content_type_json(self, async_client, sample_cv_path, valid_api_key):
        """Test response Content-Type is application/json"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert "application/json" in response.headers["content-type"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_matches_pydantic_schema(self, async_client, sample_cv_path, valid_api_key):
        """Test response matches CVAnalysisResponse Pydantic model"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 200

        # Validate against Pydantic model
        try:
            validated_response = CVAnalysisResponse(**response.json())
            assert validated_response is not None
        except ValidationError as e:
            pytest.fail(f"Response doesn't match schema: {e}")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_has_all_required_top_level_fields(self, async_client, sample_cv_path, valid_api_key):
        """Test response has all 8 required top-level fields"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        data = response.json()

        required_fields = [
            "analysis_metadata",
            "candidate_summary",
            "detailed_scores",
            "strengths",
            "improvement_areas",
            "red_flags",
            "recommendations",
            "interview_suggestions"
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_analysis_metadata_schema(self, async_client, sample_cv_path, valid_api_key):
        """Test analysis_metadata matches schema"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        metadata = response.json()["analysis_metadata"]

        # Required fields
        assert "timestamp" in metadata
        assert "parsing_confidence" in metadata
        assert "cv_language" in metadata
        assert "analysis_version" in metadata
        assert "processing_duration_ms" in metadata

        # Validate types and ranges
        assert isinstance(metadata["parsing_confidence"], (int, float))
        assert 0.0 <= metadata["parsing_confidence"] <= 1.0
        assert isinstance(metadata["cv_language"], str)
        assert len(metadata["cv_language"]) == 2
        assert isinstance(metadata["processing_duration_ms"], int)
        assert metadata["processing_duration_ms"] > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_candidate_summary_schema(self, async_client, sample_cv_path, valid_api_key):
        """Test candidate_summary matches schema"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        summary = response.json()["candidate_summary"]

        # Required fields
        assert "name" in summary
        assert "total_score" in summary
        assert "percentile" in summary
        assert "detected_role" in summary
        assert "seniority_level" in summary
        assert "years_experience" in summary

        # Validate ranges
        assert 0.0 <= summary["total_score"] <= 10.0
        assert 0 <= summary["percentile"] <= 100
        assert summary["seniority_level"] in ["Junior", "Mid", "Senior", "Lead", "Executive"]

        # Validate years_experience structure
        exp = summary["years_experience"]
        assert "total_it" in exp
        assert "cybersecurity" in exp
        assert "current_role" in exp

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_detailed_scores_has_24_parameters(self, async_client, sample_cv_path, valid_api_key):
        """Test detailed_scores contains all 24 parameters"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        scores = response.json()["detailed_scores"]

        # All 24 parameters must be present
        expected_params = [
            "certifications", "offensive_skills", "defensive_skills", "governance",
            "cloud_security", "tools", "programming", "architecture", "education",
            "soft_skills", "languages", "devsecops", "forensics", "cryptography",
            "ot_ics", "mobile_iot", "threat_intel", "contributions", "publications",
            "management", "crisis", "transformation", "niche_specialties", "experience"
        ]

        assert len(scores) == 24
        for param in expected_params:
            assert param in scores

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_parameter_structure(self, async_client, sample_cv_path, valid_api_key):
        """Test each parameter has correct structure"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        scores = response.json()["detailed_scores"]

        # Check first parameter as example
        param = scores["certifications"]

        assert "score" in param
        assert "justification" in param
        assert "evidence" in param
        assert "weight" in param

        # Validate types and ranges
        assert 0.0 <= param["score"] <= 10.0
        assert len(param["justification"]) >= 20
        assert isinstance(param["evidence"], list)
        assert 0.5 <= param["weight"] <= 1.5

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_strengths_exactly_5_items(self, async_client, sample_cv_path, valid_api_key):
        """Test strengths array contains exactly 5 items"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        strengths = response.json()["strengths"]

        assert len(strengths) == 5

        for strength in strengths:
            assert "area" in strength
            assert "description" in strength
            assert "score" in strength
            assert "market_value" in strength

            assert strength["score"] >= 7.0
            assert strength["market_value"] in ["high", "medium", "low"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_recommendations_structure(self, async_client, sample_cv_path, valid_api_key):
        """Test recommendations has correct structure"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        recommendations = response.json()["recommendations"]

        assert "certifications" in recommendations
        assert "training" in recommendations
        assert "experience_areas" in recommendations
        assert "next_role_suggestions" in recommendations

        # All should be arrays
        assert isinstance(recommendations["certifications"], list)
        assert isinstance(recommendations["training"], list)
        assert isinstance(recommendations["experience_areas"], list)
        assert isinstance(recommendations["next_role_suggestions"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_response_interview_suggestions_minimum_questions(self, async_client, sample_cv_path, valid_api_key):
        """Test interview_suggestions meets minimum question requirements"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": valid_api_key},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        interview = response.json()["interview_suggestions"]

        assert "technical_questions" in interview
        assert "scenario_questions" in interview
        assert "verification_questions" in interview

        # Minimum requirements (FR-016)
        assert len(interview["technical_questions"]) >= 3
        assert len(interview["scenario_questions"]) >= 2

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_response_401_structure(self, async_client, sample_cv_path):
        """Test 401 Unauthorized error response structure"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        with open(sample_cv_path, 'rb') as cv_file:
            response = await async_client.post(
                "/v1/analyze-cv",
                headers={"X-API-Key": "invalid-key"},
                files={"file": ("cv.pdf", cv_file, "application/pdf")}
            )

        assert response.status_code == 401
        error = response.json()
        assert "detail" in error

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_response_400_structure(self, async_client, valid_api_key):
        """Test 400 Bad Request error response structure"""
        # Using async_client fixture
        # Using async_client fixture from conftest.py
        # Send invalid file type
        response = await async_client.post(
            "/v1/analyze-cv",
            headers={"X-API-Key": valid_api_key},
            files={"file": ("test.txt", b"not a pdf", "text/plain")}
        )

        assert response.status_code == 400
        error = response.json()
        assert "detail" in error

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_response_413_structure(self, async_client, valid_api_key):
        """Test 413 Payload Too Large error response structure"""
        large_content = b"x" * (11 * 1024 * 1024)

        # Using async_client fixture
        # Using async_client fixture from conftest.py
        response = await async_client.post(
            "/v1/analyze-cv",
            headers={"X-API-Key": valid_api_key},
            files={"file": ("large.pdf", large_content, "application/pdf")}
        )

        assert response.status_code == 413
        error = response.json()
        assert "detail" in error
