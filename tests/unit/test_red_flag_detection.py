"""
Unit tests for red flag detection in CV analysis.

Tests validate red flag parsing, classification, and validation logic.
"""
import pytest
from pydantic import ValidationError

from src.models.redflag import RedFlag


class TestRedFlagModel:
    """Test suite for RedFlag model validation"""

    def test_employment_gap_red_flag_valid(self):
        """Test valid employment gap red flag creation"""
        red_flag = RedFlag(
            type="employment_gap",
            severity="medium",
            description="Unexplained 8-month gap between June 2023 and February 2024 without justification",
            impact="May indicate unstable employment history or personal issues requiring clarification"
        )

        assert red_flag.type == "employment_gap"
        assert red_flag.severity == "medium"
        assert len(red_flag.description) >= 20
        assert len(red_flag.impact) >= 20

    def test_employment_gap_high_severity(self):
        """Test high severity employment gap (>12 months)"""
        red_flag = RedFlag(
            type="employment_gap",
            severity="high",
            description="Critical employment gap of 18 months between January 2022 and July 2023 with no explanation provided",
            impact="Significant concern for hiring decision. Extended gap may indicate career transition issues or personal problems"
        )

        assert red_flag.severity == "high"
        assert "18 months" in red_flag.description

    def test_employment_gap_low_severity(self):
        """Test low severity employment gap (3-6 months)"""
        red_flag = RedFlag(
            type="employment_gap",
            severity="low",
            description="Short 4-month gap between jobs may be normal job search period or sabbatical",
            impact="Minor concern, likely normal transition period between positions"
        )

        assert red_flag.severity == "low"


class TestCertificationMismatch:
    """Test suite for certification mismatch detection"""

    def test_certification_mismatch_high_severity(self):
        """Test high severity certification mismatch"""
        red_flag = RedFlag(
            type="certification_mismatch",
            severity="high",
            description="Claims OSCP certification but no evidence of practical penetration testing in work history",
            impact="Potential resume embellishment. Verification questions about OSCP lab scenarios required in interview"
        )

        assert red_flag.type == "certification_mismatch"
        assert red_flag.severity == "high"
        assert "OSCP" in red_flag.description

    def test_certification_without_practice(self):
        """Test certification claimed without supporting experience"""
        red_flag = RedFlag(
            type="certification_mismatch",
            severity="medium",
            description="Holds CISSP certification but work experience shows purely technical roles without governance responsibilities",
            impact="May indicate cert was obtained for resume value without practical application of GRC principles"
        )

        assert "CISSP" in red_flag.description
        assert "grc" in red_flag.impact.lower() or "governance" in red_flag.impact.lower()

    def test_expired_certification(self):
        """Test detection of expired or outdated certifications"""
        red_flag = RedFlag(
            type="certification_mismatch",
            severity="low",
            description="CEH certification listed from 2018 but no evidence of renewal or continuing education in ethical hacking",
            impact="Certification may be expired. Technical knowledge could be outdated given rapid evolution of pentesting tools"
        )

        assert red_flag.severity == "low"
        assert "CEH" in red_flag.description


class TestSkillInconsistency:
    """Test suite for skill inconsistency detection"""

    def test_skill_claimed_without_evidence(self):
        """Test skills claimed in summary but not evidenced in experience"""
        red_flag = RedFlag(
            type="skill_inconsistency",
            severity="medium",
            description="Lists 'Azure Security Center' in skills section but no Azure projects or experience documented in work history, only AWS",
            impact="Possible skill padding. Requires verification of actual Azure hands-on experience during technical interview"
        )

        assert red_flag.type == "skill_inconsistency"
        assert "Azure" in red_flag.description

    def test_tool_mismatch(self):
        """Test mismatch between claimed tools and project evidence"""
        red_flag = RedFlag(
            type="skill_inconsistency",
            severity="low",
            description="Claims expertise in Splunk SIEM but all documented SOC experience uses ELK stack and no Splunk mentioned in projects",
            impact="Tool proficiency may be overstated. Clarify actual hands-on experience with Splunk vs theoretical knowledge"
        )

        assert "Splunk" in red_flag.description
        assert "ELK" in red_flag.description


class TestRedFlagValidation:
    """Test suite for RedFlag Pydantic validation"""

    def test_description_too_short_fails(self):
        """Test that description < 20 chars fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            RedFlag(
                type="employment_gap",
                severity="low",
                description="Too short",  # Only 9 characters
                impact="This should fail validation due to short description field"
            )

        errors = exc_info.value.errors()
        assert any("description" in str(error) for error in errors)

    def test_impact_too_short_fails(self):
        """Test that impact < 20 chars fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            RedFlag(
                type="skill_inconsistency",
                severity="medium",
                description="Valid description with more than 20 characters to pass validation",
                impact="Too short"  # Only 9 characters
            )

        errors = exc_info.value.errors()
        assert any("impact" in str(error) for error in errors)

    def test_invalid_severity_fails(self):
        """Test that invalid severity literal fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            RedFlag(
                type="employment_gap",
                severity="critical",  # Invalid: only low/medium/high allowed
                description="Valid description with more than 20 characters",
                impact="Valid impact description with more than 20 characters"
            )

        errors = exc_info.value.errors()
        assert any("severity" in str(error) for error in errors)

    def test_all_severity_levels_valid(self):
        """Test that all valid severity levels are accepted"""
        for severity in ["low", "medium", "high"]:
            red_flag = RedFlag(
                type="missing_fundamentals",
                severity=severity,
                description="Valid description with sufficient character count for validation",
                impact="Valid impact description with sufficient character count for validation"
            )
            assert red_flag.severity == severity


class TestRedFlagTypes:
    """Test suite for different red flag type classifications"""

    def test_frequent_job_changes(self):
        """Test detection of frequent job changes pattern"""
        red_flag = RedFlag(
            type="frequent_job_changes",
            severity="medium",
            description="Five job changes in last 3 years with average tenure of 7 months suggests potential retention risk",
            impact="Pattern indicates possible job-hopping behavior. Investigate reasons for short tenures during interview"
        )

        assert red_flag.type == "frequent_job_changes"

    def test_missing_fundamentals(self):
        """Test detection of missing fundamental security knowledge"""
        red_flag = RedFlag(
            type="missing_fundamentals",
            severity="low",
            description="No evidence of cryptography or PKI knowledge despite senior security role claims",
            impact="Gap in foundational security knowledge may limit architecture design capabilities"
        )

        assert red_flag.type == "missing_fundamentals"

    def test_unclear_progression(self):
        """Test detection of unclear career progression"""
        red_flag = RedFlag(
            type="unclear_progression",
            severity="medium",
            description="Career path shows lateral moves without clear advancement from Junior to Senior roles over 8 years",
            impact="Unclear growth trajectory may indicate performance issues or lack of increasing responsibilities"
        )

        assert red_flag.type == "unclear_progression"


class TestRedFlagParsing:
    """Test suite for red flag parsing from agent responses"""

    def test_parse_red_flag_from_dict(self):
        """Test parsing RedFlag from dictionary (simulating Claude JSON response)"""
        red_flag_data = {
            "type": "employment_gap",
            "severity": "medium",
            "description": "Unexplained 8-month gap between positions without documented reason or explanation",
            "impact": "May indicate career instability or personal issues requiring clarification in interview"
        }

        red_flag = RedFlag(**red_flag_data)

        assert red_flag.type == "employment_gap"
        assert red_flag.severity == "medium"
        assert len(red_flag.description) >= 20
        assert len(red_flag.impact) >= 20

    def test_parse_multiple_red_flags(self):
        """Test parsing multiple red flags from list"""
        red_flags_data = [
            {
                "type": "skill_inconsistency",
                "severity": "low",
                "description": "Claims Azure expertise but no documented Azure projects in experience section",
                "impact": "Requires verification of actual hands-on Azure experience during interview"
            },
            {
                "type": "missing_fundamentals",
                "severity": "low",
                "description": "No cryptography or PKI experience documented despite senior security analyst position",
                "impact": "May limit architecture design capabilities requiring cryptographic components"
            }
        ]

        red_flags = [RedFlag(**data) for data in red_flags_data]

        assert len(red_flags) == 2
        assert red_flags[0].type == "skill_inconsistency"
        assert red_flags[1].type == "missing_fundamentals"

    def test_empty_red_flags_list(self):
        """Test handling of CV with no red flags detected"""
        red_flags_data = []
        red_flags = [RedFlag(**data) for data in red_flags_data]

        assert len(red_flags) == 0
        assert isinstance(red_flags, list)
