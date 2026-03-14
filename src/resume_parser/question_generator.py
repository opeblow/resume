"""Interview question generation module.

This module generates technical and behavioral interview questions
based on parsed resume data using OpenAI's GPT models.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .config import get_config
from .constants import (
    DEFAULT_MODEL,
    NUM_BEHAVIORAL_QUESTIONS,
    NUM_TECHNICAL_QUESTIONS,
    QUESTION_TEMPERATURE,
)
from .logging_config import get_logger
from .parser import ParsedResume

logger = get_logger(__name__)


@dataclass
class InterviewQuestions:
    """Structured interview questions."""

    technical: List[str]
    behavioral: List[str]

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary."""
        return {
            "technical": self.technical,
            "behavioral": self.behavioral,
        }


class QuestionGenerationError(Exception):
    """Exception raised when question generation fails."""

    pass


def generate_questions(parsed_resume: ParsedResume) -> InterviewQuestions:
    """Generate interview questions based on parsed resume data.

    Args:
        parsed_resume: ParsedResume instance with structured data.

    Returns:
        InterviewQuestions instance with technical and behavioral questions.

    Raises:
        QuestionGenerationError: If question generation fails.
    """
    logger.info("Generating interview questions")

    if not _has_valid_data(parsed_resume):
        raise QuestionGenerationError("No valid data to generate questions from")

    config = get_config()
    client = OpenAI(api_key=config.openai_api_key)

    prompt = _build_question_prompt(parsed_resume)

    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an interview question generator. Return ONLY valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=QUESTION_TEMPERATURE,
            max_tokens=config.max_tokens,
            response_format={"type": "json_object"},
        )

        raw_response = response.choices[0].message.content
        if raw_response is None:
            raise QuestionGenerationError("Empty response from OpenAI")

        questions_data = _parse_json_response(raw_response)
        logger.info("Successfully generated interview questions")

        return InterviewQuestions(
            technical=_normalize_questions(questions_data.get("technical", [])),
            behavioral=_normalize_questions(questions_data.get("behavioral", [])),
        )

    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response: %s", e)
        raise QuestionGenerationError(f"Invalid JSON response: {e}") from e
    except Exception as e:
        logger.error("Question generation failed: %s", e)
        raise QuestionGenerationError(f"Failed to generate questions: {e}") from e


def _has_valid_data(parsed_resume: ParsedResume) -> bool:
    """Check if parsed resume has valid data for question generation.

    Args:
        parsed_resume: Parsed resume data.

    Returns:
        True if resume has at least one field with data.
    """
    return bool(
        parsed_resume.skills
        or parsed_resume.experience
        or parsed_resume.education
        or parsed_resume.job_titles
    )


def _build_question_prompt(parsed_resume: ParsedResume) -> str:
    """Build prompt for generating interview questions.

    Args:
        parsed_resume: Parsed resume data.

    Returns:
        Formatted prompt string.
    """
    summary_parts = []

    if parsed_resume.skills:
        summary_parts.append(f"Skills: {', '.join(parsed_resume.skills)}")
    if parsed_resume.experience:
        summary_parts.append(f"Experience: {parsed_resume.experience}")
    if parsed_resume.education:
        summary_parts.append(f"Education: {', '.join(parsed_resume.education)}")
    if parsed_resume.job_titles:
        summary_parts.append(f"Job Titles: {', '.join(parsed_resume.job_titles)}")

    summary = "\n".join(summary_parts)

    return f"""Generate interview questions for a candidate with the following profile:
{summary}

Create:
- {NUM_TECHNICAL_QUESTIONS} technical questions (focus on skills, tools, problem-solving)
- {NUM_BEHAVIORAL_QUESTIONS} behavioral questions (focus on experience, teamwork, challenges)

Return ONLY this JSON structure:
{{
  "technical": ["question1", "question2", "question3", "question4", "question5"],
  "behavioral": ["question1", "question2", "question3", "question4", "question5"]
}}
"""


def _parse_json_response(response: str) -> Dict:
    """Parse JSON from API response.

    Args:
        response: Raw response string from API.

    Returns:
        Parsed JSON as dictionary.

    Raises:
        json.JSONDecodeError: If response is not valid JSON.
    """
    cleaned = re.sub(r"^```(?:json)?\s*|```$", "", response, flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def _normalize_questions(questions: Any) -> List[str]:
    """Normalize questions to a list of strings.

    Args:
        questions: Either a list or other type.

    Returns:
        List of question strings.
    """
    if isinstance(questions, list):
        return [str(q) for q in questions if q]
    return []
