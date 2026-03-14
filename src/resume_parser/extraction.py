"""Resume text extraction module.

This module handles extracting text from various resume file formats
(PDF, DOCX) and provides text cleaning utilities.
"""

import re
import string
from pathlib import Path
from typing import Final

import PyPDF2
from docx import Document

from .constants import SUPPORTED_FILE_EXTENSIONS
from .logging_config import get_logger

logger = get_logger(__name__)


class ExtractionError(Exception):
    """Exception raised when text extraction fails."""

    pass


class UnsupportedFormatError(ExtractionError):
    """Exception raised when file format is not supported."""

    pass


def extract_text_from_resume(file_path: str) -> str:
    """Extract text from a resume file.

    Args:
        file_path: Path to the resume file (PDF or DOCX).

    Returns:
        Extracted text content as a string.

    Raises:
        UnsupportedFormatError: If file extension is not supported.
        ExtractionError: If text extraction fails.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.suffix.lower()
    if extension not in SUPPORTED_FILE_EXTENSIONS:
        raise UnsupportedFormatError(
            f"Unsupported file format: {extension}. "
            f"Supported formats: {', '.join(SUPPORTED_FILE_EXTENSIONS)}"
        )

    logger.debug("Extracting text from %s", file_path)

    if extension == ".pdf":
        return _extract_from_pdf(path)
    elif extension == ".docx":
        return _extract_from_docx(path)

    raise UnsupportedFormatError(f"Unexpected format: {extension}")


def _extract_from_pdf(path: Path) -> str:
    """Extract text from a PDF file.

    Args:
        path: Path to PDF file.

    Returns:
        Extracted text content.
    """
    try:
        with open(path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pages_text = [page.extract_text() for page in pdf_reader.pages]
            text = "".join(pages_text)
            logger.debug("Extracted %d characters from PDF", len(text))
            return text.strip()
    except Exception as e:
        raise ExtractionError(f"Failed to extract PDF: {e}") from e


def _extract_from_docx(path: Path) -> str:
    """Extract text from a DOCX file.

    Args:
        path: Path to DOCX file.

    Returns:
        Extracted text content.
    """
    try:
        doc = Document(str(path))
        paragraphs = [para.text for para in doc.paragraphs]
        text = "\n".join(paragraphs)
        logger.debug("Extracted %d characters from DOCX", len(text))
        return text.strip()
    except Exception as e:
        raise ExtractionError(f"Failed to extract DOCX: {e}") from e


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing.

    This function:
    - Removes leading/trailing whitespace
    - Normalizes internal whitespace to single spaces
    - Converts to lowercase

    Args:
        text: Raw text to clean.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ""

    cleaned = re.sub(r"\s+", " ", text)
    cleaned = cleaned.strip()
    cleaned = cleaned.lower()

    logger.debug("Cleaned text: %d -> %d characters", len(text), len(cleaned))
    return cleaned
