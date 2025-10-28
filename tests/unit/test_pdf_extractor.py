"""
Unit tests for PDF text extraction service.

Tests use mocks to avoid actual PDF processing during unit tests.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.services.pdf_extractor import PDFExtractor, ExtractionResult


@pytest.fixture
def sample_cv_path():
    """Path to sample CV fixture"""
    return Path("tests/fixtures/sample_cvs/sample_cybersecurity_cv.pdf")


@pytest.fixture
def mock_pdf_text():
    """Sample extracted text from a cybersecurity CV"""
    return """
    ADRIÀ PÉREZ GARCÍA
    Senior Cybersecurity Analyst

    PROFESSIONAL EXPERIENCE
    - 5 years in penetration testing
    - OSCP and CEH certified
    - Expert in cloud security (AWS, Azure)
    - Programming: Python, Bash, PowerShell

    CERTIFICATIONS
    - OSCP (Offensive Security Certified Professional)
    - CEH (Certified Ethical Hacker)
    - Security+ CompTIA

    SKILLS
    - Penetration Testing
    - Vulnerability Assessment
    - Incident Response
    - SIEM (Splunk, ELK)
    """


class TestPDFExtractor:
    """Test suite for PDFExtractor service"""

    @pytest.mark.asyncio
    async def test_extract_text_success(self, sample_cv_path, mock_pdf_text):
        """Test successful PDF text extraction"""
        # Mock the pdf skill invocation
        with patch('src.services.pdf_extractor.invoke_pdf_skill', new_callable=AsyncMock) as mock_skill:
            mock_skill.return_value = mock_pdf_text

            extractor = PDFExtractor()
            result = await extractor.extract_text(sample_cv_path)

            # Assertions
            assert isinstance(result, ExtractionResult)
            assert result.text == mock_pdf_text
            assert result.parsing_confidence > 0.0
            assert result.parsing_confidence <= 1.0
            assert len(result.text) > 100

            # Verify skill was called with correct parameters
            mock_skill.assert_called_once_with("extract_text", sample_cv_path)

    @pytest.mark.asyncio
    async def test_calculate_parsing_confidence_high(self, mock_pdf_text):
        """Test confidence calculation for high-quality extraction"""
        extractor = PDFExtractor()

        # Good quality text: long, diverse characters, readable
        confidence = extractor.calculate_parsing_confidence(mock_pdf_text)

        # Mock text is relatively short (~500 chars), so 0.7+ is reasonable
        # Full CV would get 0.8+
        assert confidence >= 0.7
        assert confidence <= 1.0

    @pytest.mark.asyncio
    async def test_calculate_parsing_confidence_low(self):
        """Test confidence calculation for poor-quality extraction"""
        extractor = PDFExtractor()

        # Poor quality text: short, repetitive, unreadable
        poor_text = "@@@ ### %%% &&& *** @@@ ### %%% &&&"
        confidence = extractor.calculate_parsing_confidence(poor_text)

        assert confidence < 0.6

    @pytest.mark.asyncio
    async def test_detect_language_spanish(self):
        """Test language detection for Spanish CV"""
        extractor = PDFExtractor()

        spanish_text = """
        Experiencia profesional en ciberseguridad
        Analista de seguridad con 5 años de experiencia
        Certificaciones: OSCP, CEH
        """

        language = extractor.detect_language(spanish_text)
        assert language == "es"

    @pytest.mark.asyncio
    async def test_detect_language_english(self, mock_pdf_text):
        """Test language detection for English CV"""
        extractor = PDFExtractor()

        language = extractor.detect_language(mock_pdf_text)
        assert language == "en"

    @pytest.mark.asyncio
    async def test_extract_text_empty_pdf(self, sample_cv_path):
        """Test handling of empty PDF"""
        with patch('src.services.pdf_extractor.invoke_pdf_skill', new_callable=AsyncMock) as mock_skill:
            mock_skill.return_value = ""

            extractor = PDFExtractor()
            result = await extractor.extract_text(sample_cv_path)

            assert result.text == ""
            assert result.parsing_confidence == 0.0

    @pytest.mark.asyncio
    async def test_extract_text_file_not_found(self):
        """Test handling of non-existent PDF file"""
        extractor = PDFExtractor()
        non_existent_path = Path("non_existent_cv.pdf")

        with pytest.raises(FileNotFoundError):
            await extractor.extract_text(non_existent_path)

    @pytest.mark.asyncio
    async def test_extract_text_corrupted_pdf(self, sample_cv_path):
        """Test handling of corrupted PDF"""
        with patch('src.services.pdf_extractor.invoke_pdf_skill', new_callable=AsyncMock) as mock_skill:
            mock_skill.side_effect = Exception("PDF parsing error")

            extractor = PDFExtractor()

            with pytest.raises(Exception) as exc_info:
                await extractor.extract_text(sample_cv_path)

            assert "PDF parsing error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_confidence_calculation_character_diversity(self):
        """Test confidence considers character diversity"""
        extractor = PDFExtractor()

        # High diversity text
        diverse_text = "The quick brown fox jumps over the lazy dog. 0123456789!"
        high_confidence = extractor.calculate_parsing_confidence(diverse_text)

        # Low diversity text (repetitive)
        repetitive_text = "aaaa aaaa aaaa aaaa aaaa aaaa aaaa aaaa aaaa aaaa aaaa"
        low_confidence = extractor.calculate_parsing_confidence(repetitive_text)

        assert high_confidence > low_confidence

    @pytest.mark.asyncio
    async def test_confidence_calculation_text_length(self):
        """Test confidence considers text length"""
        extractor = PDFExtractor()

        # Short text
        short_text = "CV"
        short_confidence = extractor.calculate_parsing_confidence(short_text)

        # Long text
        long_text = "Professional Experience\n" * 50
        long_confidence = extractor.calculate_parsing_confidence(long_text)

        assert long_confidence > short_confidence

    @pytest.mark.asyncio
    async def test_full_extraction_result_structure(self, sample_cv_path, mock_pdf_text):
        """Test complete ExtractionResult data structure"""
        with patch('src.services.pdf_extractor.invoke_pdf_skill', new_callable=AsyncMock) as mock_skill:
            mock_skill.return_value = mock_pdf_text

            extractor = PDFExtractor()
            result = await extractor.extract_text(sample_cv_path)

            # Verify all required fields exist
            assert hasattr(result, 'text')
            assert hasattr(result, 'parsing_confidence')
            assert hasattr(result, 'cv_language')

            # Verify types
            assert isinstance(result.text, str)
            assert isinstance(result.parsing_confidence, float)
            assert isinstance(result.cv_language, str)

            # Verify cv_language is detected
            assert result.cv_language in ["es", "en"]
