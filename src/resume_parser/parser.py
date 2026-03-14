"""Resume parsing module using OpenAI API.

This module handles parsing raw resume text into structured data
(skills, experience, education, job titles) using OpenAI's GPT models.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .config import get_config
from .constants import (
    DEFAULT_EXPERIENCE,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    OUTPUT_FIELDS,
)
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedResume:
    """Structured resume data."""

    skills: List[str]
    experience: str
    education: List[str]
    job_titles: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "skills": self.skills,
            "experience": self.experience,
            "education": self.education,
            "job_titles": self.job_titles,
        }


class ParseError(Exception):
    """Exception raised when resume parsing fails."""

    pass


def parse_resume(resume_text: str) -> ParsedResume:
    """Parse resume text into structured data using OpenAI.

    Args:
        resume_text: Raw text extracted from resume.

    Returns:
        ParsedResume instance with structured data.

    Raises:
        ParseError: If parsing fails.
    """
    logger.info("Starting resume parsing")
    logger.debug("Input text length: %d characters", len(resume_text))

    config = get_config()
    client = OpenAI(api_key=config.openai_api_key)

    prompt = _build_parsing_prompt(resume_text)

    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": "You are a resume parsing assistant. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=config.max_tokens,
        )

        raw_response = response.choices[0].message.content
        if raw_response is None:
            raise ParseError("Empty response from OpenAI")

        parsed_data = _parse_json_response(raw_response)
        logger.info("Successfully parsed resume")

        return ParsedResume(
            skills=_normalize_list(parsed_data.get("skills")),
            experience=parsed_data.get("experience", DEFAULT_EXPERIENCE),
            education=_normalize_list(parsed_data.get("education")),
            job_titles=_normalize_list(parsed_data.get("job_titles")),
        )

    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response: %s", e)
        raise ParseError(f"Invalid JSON response: {e}") from e
    except Exception as e:
        logger.error("Parsing failed: %s", e)
        raise ParseError(f"Failed to parse resume: {e}") from e


def _build_parsing_prompt(resume_text: str) -> str:
    """Build the prompt for parsing resume text.

    Args:
        resume_text: Raw resume text.

    Returns:
        Formatted prompt string.
    """
    return f"""Extract the following information from this resume and return ONLY a JSON object with these exact keys:
{{
    "skills": ["list of technical skills"],
    "experience": "number of years as a string, e.g. '5 years'",
    "education": ["list of degrees or education"],
    "job_titles": ["list of job titles"]
}}

If any field is not found, use an empty list [] for lists or "Not specified" for experience.

Resume:
{resume_text}

Return ONLY the JSON object, nothing else."""


def _parse_json_response(response: str) -> Dict[str, Any]:
    """Parse and clean JSON from API response.

    Strips markdown code blocks if present.

    Args:
        response: Raw response string from API.

    Returns:
        Parsed JSON as dictionary.

    Raises:
        json.JSONDecodeError: If response is not valid JSON.
    """
    cleaned = re.sub(r"^```(?:json)?\s*|```$", "", response, flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def _normalize_list(value: Any) -> List[str]:
    """Normalize a value to a list of strings.

    Args:
        value: Either a list, string, or other type.

    Returns:
        List of strings.
    """
    if isinstance(value, list):
        return [str(item) for item in value if item]
    elif isinstance(value, str) and value:
        return [value]
    return []
