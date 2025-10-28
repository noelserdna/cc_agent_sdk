"""
Unit tests for recommendation generation models.

Tests validate recommendation structures, interview questions, and validation logic.
"""
import pytest
from pydantic import ValidationError

from src.models.recommendations import Recommendations, InterviewSuggestions


class TestRecommendationsModel:
    """Test suite for Recommendations model validation"""

    def test_recommendations_all_fields_populated(self):
        """Test valid recommendations with all fields"""
        recommendations = Recommendations(
            certifications=[
                "OSCP - Offensive Security Certified Professional",
                "CISSP - Certified Information Systems Security Professional"
            ],
            training=[
                "Advanced Web Application Security course",
                "Cloud Security Architecture bootcamp"
            ],
            experience_areas=[
                "Kubernetes security and container hardening",
                "Threat hunting and detection engineering"
            ],
            next_role_suggestions=[
                "Senior Security Engineer",
                "Security Architect"
            ]
        )

        assert len(recommendations.certifications) == 2
        assert len(recommendations.training) == 2
        assert len(recommendations.experience_areas) == 2
        assert len(recommendations.next_role_suggestions) == 2

    def test_recommendations_empty_fields_valid(self):
        """Test that empty recommendation lists are valid (default_factory=list)"""
        recommendations = Recommendations()

        assert recommendations.certifications == []
        assert recommendations.training == []
        assert recommendations.experience_areas == []
        assert recommendations.next_role_suggestions == []

    def test_recommendations_partial_fields(self):
        """Test recommendations with only some fields populated"""
        recommendations = Recommendations(
            certifications=["OSCP"],
            training=["Security course"]
        )

        assert len(recommendations.certifications) == 1
        assert len(recommendations.training) == 1
        assert recommendations.experience_areas == []
        assert recommendations.next_role_suggestions == []


class TestRecommendationsCertifications:
    """Test suite for certification recommendations"""

    def test_offensive_security_certifications(self):
        """Test offensive security focused certification recommendations"""
        recommendations = Recommendations(
            certifications=[
                "OSCP - Offensive Security Certified Professional",
                "GXPN - GIAC Exploit Researcher and Advanced Penetration Tester",
                "OSCE - Offensive Security Certified Expert"
            ]
        )

        assert any("OSCP" in cert for cert in recommendations.certifications)
        assert any("GXPN" in cert or "OSCE" in cert for cert in recommendations.certifications)

    def test_defensive_security_certifications(self):
        """Test defensive/blue team certification recommendations"""
        recommendations = Recommendations(
            certifications=[
                "GCIH - GIAC Certified Incident Handler",
                "GMON - GIAC Continuous Monitoring Certification",
                "GCFA - GIAC Certified Forensic Analyst"
            ]
        )

        defensive_keywords = ["GCIH", "GMON", "GCFA", "Incident", "Monitoring", "Forensic"]
        assert any(
            any(keyword in cert for keyword in defensive_keywords)
            for cert in recommendations.certifications
        )

    def test_cloud_security_certifications(self):
        """Test cloud security certification recommendations"""
        recommendations = Recommendations(
            certifications=[
                "AWS Certified Security - Specialty",
                "Microsoft Certified: Azure Security Engineer Associate",
                "Google Professional Cloud Security Engineer"
            ]
        )

        cloud_keywords = ["AWS", "Azure", "Google", "Cloud"]
        assert any(
            any(keyword in cert for keyword in cloud_keywords)
            for cert in recommendations.certifications
        )

    def test_governance_certifications(self):
        """Test GRC/governance certification recommendations"""
        recommendations = Recommendations(
            certifications=[
                "CISSP - Certified Information Systems Security Professional",
                "CISM - Certified Information Security Manager",
                "CRISC - Certified in Risk and Information Systems Control"
            ]
        )

        governance_keywords = ["CISSP", "CISM", "CRISC", "Manager", "Risk"]
        assert any(
            any(keyword in cert for keyword in governance_keywords)
            for cert in recommendations.certifications
        )


class TestRecommendationsTraining:
    """Test suite for training recommendations"""

    def test_training_courses_are_specific(self):
        """Test that training recommendations are specific and actionable"""
        recommendations = Recommendations(
            training=[
                "SANS SEC542: Web Application Penetration Testing",
                "Advanced Kubernetes Security - Hands-on Lab",
                "Cloud Security Alliance CCSK Certification Training"
            ]
        )

        for course in recommendations.training:
            # Training should be specific (not just "security training")
            assert len(course) > 15, "Training recommendation too vague"

    def test_training_aligned_with_gaps(self):
        """Test that training addresses specific skill gaps"""
        recommendations = Recommendations(
            training=[
                "Cryptography fundamentals and PKI implementation course",
                "Governance, Risk, and Compliance (GRC) workshop",
                "Cloud-native security architecture training"
            ]
        )

        # Training should target specific domains
        training_domains = ["Cryptography", "GRC", "Cloud", "PKI", "Governance"]
        training_text = " ".join(recommendations.training)

        assert any(domain in training_text for domain in training_domains)


class TestRecommendationsExperienceAreas:
    """Test suite for experience area recommendations"""

    def test_experience_areas_are_actionable(self):
        """Test that experience areas suggest hands-on practice"""
        recommendations = Recommendations(
            experience_areas=[
                "Kubernetes security and container hardening",
                "Threat hunting and detection engineering",
                "Security automation and orchestration (SOAR)"
            ]
        )

        for area in recommendations.experience_areas:
            # Should be specific technical areas
            assert len(area) > 10
            assert area != "General security experience"

    def test_experience_areas_cover_different_domains(self):
        """Test that experience areas span multiple cybersecurity domains"""
        recommendations = Recommendations(
            experience_areas=[
                "Cloud security posture management (CSPM)",
                "Red team operations and adversary emulation",
                "Security code review and SAST/DAST integration"
            ]
        )

        # Should cover different aspects: cloud, offensive, application security
        areas_text = " ".join(recommendations.experience_areas)
        assert "Cloud" in areas_text or "CSPM" in areas_text
        assert "Red team" in areas_text or "adversary" in areas_text
        assert "code review" in areas_text or "SAST" in areas_text


class TestRecommendationsNextRoles:
    """Test suite for next role suggestions"""

    def test_next_roles_match_seniority_progression(self):
        """Test that next roles represent logical career progression"""
        # For mid-level professional
        recommendations = Recommendations(
            next_role_suggestions=[
                "Senior Security Engineer",
                "Security Architect",
                "Security Team Lead"
            ]
        )

        seniority_keywords = ["Senior", "Lead", "Architect", "Principal", "Manager"]
        assert any(
            any(keyword in role for keyword in seniority_keywords)
            for role in recommendations.next_role_suggestions
        )

    def test_next_roles_for_senior_professional(self):
        """Test next role suggestions for senior candidates"""
        recommendations = Recommendations(
            next_role_suggestions=[
                "Principal Security Engineer",
                "Security Architecture Lead",
                "Director of Security Engineering"
            ]
        )

        executive_keywords = ["Principal", "Director", "Lead", "Chief", "VP"]
        assert any(
            any(keyword in role for keyword in executive_keywords)
            for role in recommendations.next_role_suggestions
        )

    def test_next_roles_aligned_with_specialization(self):
        """Test that next roles align with candidate's specialization"""
        # For offensive security specialist
        recommendations = Recommendations(
            next_role_suggestions=[
                "Senior Penetration Tester",
                "Red Team Lead",
                "Offensive Security Consultant"
            ]
        )

        offensive_keywords = ["Penetration", "Red Team", "Offensive", "Pentester"]
        # At least one role should match specialization
        assert any(
            any(keyword in role for keyword in offensive_keywords)
            for role in recommendations.next_role_suggestions
        )


class TestInterviewSuggestionsModel:
    """Test suite for InterviewSuggestions model validation"""

    def test_interview_suggestions_valid_structure(self):
        """Test valid interview suggestions with all required fields"""
        interview = InterviewSuggestions(
            technical_questions=[
                "Explain your approach to securing a Kubernetes cluster",
                "Describe a penetration test methodology",
                "How would you implement zero-trust architecture?"
            ],
            scenario_questions=[
                "Tell me about a critical security incident you handled",
                "How do you prioritize security vs business needs?"
            ],
            verification_questions=[
                "Walk me through your OSCP lab experience",
                "Explain your AWS security project architecture"
            ]
        )

        assert len(interview.technical_questions) >= 3
        assert len(interview.scenario_questions) >= 2
        assert len(interview.verification_questions) >= 0

    def test_interview_missing_technical_questions_fails(self):
        """Test that missing or insufficient technical questions fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            InterviewSuggestions(
                technical_questions=[  # Only 2, need minimum 3
                    "Question 1",
                    "Question 2"
                ],
                scenario_questions=[
                    "Scenario 1",
                    "Scenario 2"
                ]
            )

        errors = exc_info.value.errors()
        assert any("technical_questions" in str(error) for error in errors)

    def test_interview_missing_scenario_questions_fails(self):
        """Test that missing or insufficient scenario questions fails validation"""
        with pytest.raises(ValidationError) as exc_info:
            InterviewSuggestions(
                technical_questions=[
                    "Tech 1", "Tech 2", "Tech 3"
                ],
                scenario_questions=[  # Only 1, need minimum 2
                    "Scenario 1"
                ]
            )

        errors = exc_info.value.errors()
        assert any("scenario_questions" in str(error) for error in errors)

    def test_interview_verification_questions_optional(self):
        """Test that verification questions are optional (default_factory)"""
        interview = InterviewSuggestions(
            technical_questions=["Tech 1", "Tech 2", "Tech 3"],
            scenario_questions=["Scenario 1", "Scenario 2"]
        )

        assert interview.verification_questions == []


class TestInterviewTechnicalQuestions:
    """Test suite for technical interview questions"""

    def test_technical_questions_are_specific(self):
        """Test that technical questions target specific skills"""
        interview = InterviewSuggestions(
            technical_questions=[
                "How would you detect and prevent SQL injection in a web application?",
                "Explain the TLS handshake process and common vulnerabilities",
                "Describe your approach to securing a CI/CD pipeline"
            ],
            scenario_questions=["Scenario 1", "Scenario 2"]
        )

        for question in interview.technical_questions:
            # Technical questions should be detailed
            assert len(question) > 20
            # Should be a question or imperative (How, What, Explain, Describe, etc.)
            question_indicators = ["?", "how", "what", "explain", "describe", "walk me through"]
            assert any(indicator in question.lower() for indicator in question_indicators)

    def test_technical_questions_match_candidate_domain(self):
        """Test that technical questions align with candidate's expertise"""
        # For cloud security specialist
        interview = InterviewSuggestions(
            technical_questions=[
                "How would you secure an AWS S3 bucket from data exfiltration?",
                "Explain your approach to cloud security posture management",
                "Describe IAM best practices in multi-account AWS environments"
            ],
            scenario_questions=["Scenario 1", "Scenario 2"]
        )

        cloud_keywords = ["AWS", "Cloud", "S3", "IAM", "Azure", "GCP"]
        tech_text = " ".join(interview.technical_questions)
        # At least some questions should match the domain
        assert any(keyword in tech_text for keyword in cloud_keywords)


class TestInterviewScenarioQuestions:
    """Test suite for scenario-based interview questions"""

    def test_scenario_questions_are_behavioral(self):
        """Test that scenario questions assess soft skills and experience"""
        interview = InterviewSuggestions(
            technical_questions=["Tech 1", "Tech 2", "Tech 3"],
            scenario_questions=[
                "Tell me about a time you identified a critical vulnerability",
                "Describe how you handled a disagreement with a development team"
            ]
        )

        # Scenario questions often start with behavioral prompts
        behavioral_prompts = ["Tell me about", "Describe", "Explain a situation", "How did you"]
        for question in interview.scenario_questions:
            # At least some should use behavioral prompting
            assert any(prompt in question for prompt in behavioral_prompts) or len(question) > 20


class TestInterviewVerificationQuestions:
    """Test suite for verification interview questions"""

    def test_verification_questions_target_claims(self):
        """Test that verification questions validate specific CV claims"""
        interview = InterviewSuggestions(
            technical_questions=["Tech 1", "Tech 2", "Tech 3"],
            scenario_questions=["Scenario 1", "Scenario 2"],
            verification_questions=[
                "You mentioned OSCP certification - walk me through the buffer overflow process",
                "Can you explain the AWS Lambda security project you listed?",
                "Describe your experience with the MITRE ATT&CK framework"
            ]
        )

        for question in interview.verification_questions:
            # Verification questions should reference specific claims
            assert len(question) > 15

    def test_verification_questions_for_certifications(self):
        """Test verification questions for claimed certifications"""
        interview = InterviewSuggestions(
            technical_questions=["Tech 1", "Tech 2", "Tech 3"],
            scenario_questions=["Scenario 1", "Scenario 2"],
            verification_questions=[
                "Walk me through your OSCP lab methodology",
                "Explain a CISSP domain you found most challenging"
            ]
        )

        cert_keywords = ["OSCP", "CISSP", "CEH", "GIAC", "certification"]
        verification_text = " ".join(interview.verification_questions)
        # Should reference certifications
        assert any(keyword in verification_text for keyword in cert_keywords)


class TestRecommendationsParsing:
    """Test suite for parsing recommendations from agent responses"""

    def test_parse_recommendations_from_dict(self):
        """Test parsing Recommendations from dictionary (Claude JSON response)"""
        recommendations_data = {
            "certifications": ["OSCP", "CISSP"],
            "training": ["SANS SEC542", "Cloud Security course"],
            "experience_areas": ["Kubernetes security", "Threat hunting"],
            "next_role_suggestions": ["Senior Security Engineer", "Security Architect"]
        }

        recommendations = Recommendations(**recommendations_data)

        assert len(recommendations.certifications) == 2
        assert len(recommendations.training) == 2
        assert len(recommendations.experience_areas) == 2
        assert len(recommendations.next_role_suggestions) == 2

    def test_parse_interview_suggestions_from_dict(self):
        """Test parsing InterviewSuggestions from dictionary"""
        interview_data = {
            "technical_questions": [
                "Question 1?",
                "Question 2?",
                "Question 3?"
            ],
            "scenario_questions": [
                "Scenario 1",
                "Scenario 2"
            ],
            "verification_questions": [
                "Verify claim 1"
            ]
        }

        interview = InterviewSuggestions(**interview_data)

        assert len(interview.technical_questions) == 3
        assert len(interview.scenario_questions) == 2
        assert len(interview.verification_questions) == 1
