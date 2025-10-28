"""PDF text extraction service using Claude Code pdf skill.

This module provides functionality for extracting text from PDF CVs
and calculating parsing confidence scores.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

import structlog

logger = structlog.get_logger(__name__)


# PDF text extraction using pypdf
async def invoke_pdf_skill(operation: str, file_path: Path) -> str:
    """
    Extract text from PDF using pypdf library.

    Args:
        operation: The operation to perform (e.g., "extract_text")
        file_path: Path to the PDF file

    Returns:
        Extracted text from the PDF

    Raises:
        ValueError: If operation is not supported or PDF is invalid
    """
    if operation != "extract_text":
        raise ValueError(f"Unsupported operation: {operation}")

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(file_path))
        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()
    except Exception as e:
        logger.error("pdf_extraction_failed", file_path=str(file_path), error=str(e))
        raise ValueError(f"Failed to extract text from PDF: {e}") from e


@dataclass
class PDFExtractionResult:
    """Result of PDF text extraction."""

    text: str
    parsing_confidence: float
    page_count: int
    char_count: int
    cv_language: str


# Alias for backward compatibility with tests
ExtractionResult = PDFExtractionResult


class PDFExtractor:
    """
    PDF text extraction service class.

    This class provides a stateful PDF extraction service with configurable
    extraction strategies (useful for testing and mocking).
    """

    def __init__(self, use_pdf_skill: bool = True):
        """
        Initialize the PDF extractor.

        Args:
            use_pdf_skill: Whether to use Claude Code pdf skill (True) or placeholder (False)
        """
        self.use_pdf_skill = use_pdf_skill

    async def extract(self, file_path: Path) -> PDFExtractionResult:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF file to extract text from

        Returns:
            PDFExtractionResult containing extracted text, confidence score,
            and metadata

        Raises:
            FileNotFoundError: If the PDF file does not exist
            ValueError: If the file is not a valid PDF
        """
        return await extract_text_from_pdf(file_path)

    async def extract_text(self, file_path: Path) -> PDFExtractionResult:
        """
        Extract text from a PDF file.

        Alias for extract() method to maintain backward compatibility with tests.

        Args:
            file_path: Path to the PDF file to extract text from

        Returns:
            PDFExtractionResult containing extracted text, confidence score,
            and metadata

        Raises:
            FileNotFoundError: If the PDF file does not exist
            ValueError: If the file is not a valid PDF
        """
        return await self.extract(file_path)

    def calculate_confidence(self, text: str, page_count: int = 1) -> float:
        """
        Calculate parsing confidence score based on text characteristics.

        Args:
            text: Extracted text from PDF
            page_count: Number of pages in the PDF

        Returns:
            Confidence score between 0.0 and 1.0
        """
        return calculate_parsing_confidence(text, page_count)

    def calculate_parsing_confidence(self, text: str, page_count: int = 1) -> float:
        """
        Calculate parsing confidence score based on text characteristics.

        Alias for calculate_confidence() to maintain backward compatibility with tests.

        Args:
            text: Extracted text from PDF
            page_count: Number of pages in the PDF

        Returns:
            Confidence score between 0.0 and 1.0
        """
        return self.calculate_confidence(text, page_count)

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the extracted text.

        Uses simple heuristics to detect Spanish (es) or English (en).
        Defaults to English if unsure.

        Args:
            text: Extracted text from PDF

        Returns:
            Language code: "es" for Spanish, "en" for English
        """
        return detect_language(text)


async def extract_text_from_pdf(file_path: Path) -> PDFExtractionResult:
    """Extract text from a PDF file using Claude Code pdf skill.

    Args:
        file_path: Path to the PDF file to extract text from

    Returns:
        PDFExtractionResult containing extracted text, confidence score,
        and metadata

    Raises:
        FileNotFoundError: If the PDF file does not exist
        ValueError: If the file is not a valid PDF
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if file_path.suffix.lower() != ".pdf":
        raise ValueError(f"File is not a PDF: {file_path}")

    logger.info("extracting_pdf_text", file_path=str(file_path))

    # Placeholder: Read file size to simulate extraction
    file_size = file_path.stat().st_size
    logger.debug("pdf_file_size", file_size_bytes=file_size)

    # Extract text using pdf skill
    extracted_text = await invoke_pdf_skill("extract_text", file_path)

    # Calculate parsing confidence
    confidence = calculate_parsing_confidence(extracted_text, page_count=1)

    # Detect language
    language = detect_language(extracted_text)

    result = PDFExtractionResult(
        text=extracted_text,
        parsing_confidence=confidence,
        page_count=1,  # Will be from pdf skill
        char_count=len(extracted_text),
        cv_language=language,
    )

    logger.info(
        "pdf_extraction_complete",
        char_count=result.char_count,
        page_count=result.page_count,
        confidence=result.parsing_confidence,
        language=result.cv_language,
    )

    return result


def calculate_parsing_confidence(text: str, page_count: int = 1) -> float:
    """Calculate parsing confidence score based on text characteristics.

    The confidence score is based on:
    - Text length (longer text = higher confidence)
    - Character diversity (more unique chars = higher confidence)
    - Presence of common CV keywords
    - Ratio of alphanumeric to total characters

    Args:
        text: Extracted text from PDF
        page_count: Number of pages in the PDF

    Returns:
        Confidence score between 0.0 and 1.0
    """
    if not text or len(text.strip()) == 0:
        return 0.0

    # Factor 1: Text length relative to expected CV length
    # Typical CV: 2-4 pages ~= 2000-8000 characters
    text_length = len(text.strip())
    length_score = min(text_length / 2000.0, 1.0)

    # Factor 2: Character diversity (unique characters ratio)
    unique_chars = len(set(text))
    total_chars = len(text)
    diversity_score = min(unique_chars / 100.0, 1.0) if total_chars > 0 else 0.0

    # Factor 3: Alphanumeric ratio (should be high for text, low for garbage)
    alphanumeric_count = sum(1 for c in text if c.isalnum())
    alphanumeric_ratio = alphanumeric_count / total_chars if total_chars > 0 else 0.0
    alphanumeric_score = min(alphanumeric_ratio * 2.0, 1.0)

    # Factor 4: Common CV keywords presence (bonus)
    cv_keywords = [
        "experience",
        "education",
        "skills",
        "professional",
        "certification",
        "security",
        "developer",
        "engineer",
        "analyst",
        "manager",
        "project",
        "technical",
        "years",
        "university",
        "degree",
    ]
    text_lower = text.lower()
    keyword_matches = sum(1 for keyword in cv_keywords if keyword in text_lower)
    keyword_score = min(keyword_matches / 5.0, 1.0)

    # Weighted average of all factors
    confidence = (
        length_score * 0.25
        + diversity_score * 0.20
        + alphanumeric_score * 0.30
        + keyword_score * 0.25
    )

    # Adjust for very short texts (likely OCR failures)
    if text_length < 500:
        confidence *= text_length / 500.0

    # Adjust for multi-page documents
    if page_count > 1:
        expected_chars_per_page = text_length / page_count
        if expected_chars_per_page < 800:  # Too few chars per page
            confidence *= 0.8

    # Ensure confidence is in valid range
    confidence = max(0.0, min(1.0, confidence))

    logger.debug(
        "confidence_calculation",
        text_length=text_length,
        unique_chars=unique_chars,
        alphanumeric_ratio=alphanumeric_ratio,
        keyword_matches=keyword_matches,
        final_confidence=confidence,
    )

    return round(confidence, 2)


def detect_language(text: str) -> str:
    """Detect the language of the extracted text.

    Uses simple heuristics to detect Spanish (es) or English (en).
    Defaults to English if unsure.

    Args:
        text: Extracted text from PDF

    Returns:
        Language code: "es" for Spanish, "en" for English
    """
    if not text or len(text.strip()) == 0:
        return "en"  # Default to English for empty text

    text_lower = text.lower()

    # Spanish language indicators
    spanish_keywords = [
        "experiencia",
        "profesional",
        "educación",
        "habilidades",
        "certificación",
        "certificaciones",
        "años",
        "universidad",
        "licenciatura",
        "maestría",
        "español",
        "conocimientos",
        "proyectos",
        "técnico",
        "desarrollador",
        "ingeniero",
        "analista",
        "gerente",
        "trabajé",
        "trabajó",
    ]

    # English language indicators
    english_keywords = [
        "experience",
        "professional",
        "education",
        "skills",
        "certification",
        "certifications",
        "years",
        "university",
        "bachelor",
        "master",
        "english",
        "knowledge",
        "projects",
        "technical",
        "developer",
        "engineer",
        "analyst",
        "manager",
        "worked",
        "developed",
    ]

    # Count matches for each language
    spanish_matches = sum(1 for keyword in spanish_keywords if keyword in text_lower)
    english_matches = sum(1 for keyword in english_keywords if keyword in text_lower)

    # Determine language based on keyword matches
    if spanish_matches > english_matches:
        return "es"
    else:
        return "en"  # Default to English if tied or English has more matches
