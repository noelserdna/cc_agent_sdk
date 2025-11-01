"""PDF content models for enriched extraction.

This module defines data models for enriched PDF content extraction,
including text, tables, images, URLs, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ImageInfo:
    """Information about an embedded image in a PDF."""

    page_number: int
    image_index: int
    format: str  # jpg, png, etc.
    size_bytes: int
    extracted_path: str | None = None


@dataclass
class EnrichedPDFContent:
    """Enriched PDF content with text, tables, images, URLs, and metadata."""

    text: str
    tables: list[list[list[str]]] = field(default_factory=list)
    images: list[ImageInfo] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    page_count: int = 1
    char_count: int = 0
    cv_language: str = "en"
    parsing_confidence: float = 0.0
