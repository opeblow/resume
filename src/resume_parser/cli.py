"""Command-line interface for the resume parser.

This module provides the CLI entry point for the resume parser application.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

from .config import Config, reset_config
from .extraction import (
    ExtractionError,
    extract_text_from_resume,
    clean_text,
)
from .logging_config import configure_logging, get_logger
from .parser import ParseError, parse_resume
from .question_generator import (
    QuestionGenerationError,
    generate_questions,
)

logger = get_logger(__name__)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments. Defaults to sys.argv.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = _create_parser()
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose)
    logger.info("Starting resume parser")

    try:
        result = process_resume(args.file, args.output)
        return 0
    except ExtractionError as e:
        logger.error("Extraction failed: %s", e)
        print(f"Error: Failed to extract text from resume: {e}", file=sys.stderr)
        return 1
    except ParseError as e:
        logger.error("Parsing failed: %s", e)
        print(f"Error: Failed to parse resume: {e}", file=sys.stderr)
        return 1
    except QuestionGenerationError as e:
        logger.error("Question generation failed: %s", e)
        print(f"Error: Failed to generate questions: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return 1


def process_resume(file_path: Path, output_path: Path | None = None) -> None:
    """Process a resume file and generate interview questions.

    Args:
        file_path: Path to the resume file.
        output_path: Optional path to save JSON output.

    Raises:
        ExtractionError: If text extraction fails.
        ParseError: If parsing fails.
        QuestionGenerationError: If question generation fails.
    """
    logger.info("Processing resume: %s", file_path)

    print(f"Reading resume: {file_path}")
    raw_text = extract_text_from_resume(str(file_path))
    print(f"Extracted {len(raw_text)} characters")

    print("Cleaning text...")
    cleaned_text = clean_text(raw_text)
    print(f"Cleaned text: {len(cleaned_text)} characters")

    print("Parsing resume with AI...")
    parsed_resume = parse_resume(cleaned_text)
    print("Parsing complete!")

    print("\nParsed Resume Data:")
    print(json.dumps(parsed_resume.to_dict(), indent=2))

    print("\nGenerating interview questions...")
    questions = generate_questions(parsed_resume)
    print("Question generation complete!")

    print("\nInterview Questions:")
    print("\nTechnical Questions:")
    for i, q in enumerate(questions.technical, 1):
        print(f"  {i}. {q}")

    print("\nBehavioral Questions:")
    for i, q in enumerate(questions.behavioral, 1):
        print(f"  {i}. {q}")

    if output_path:
        output_data = {
            "parsed_resume": parsed_resume.to_dict(),
            "questions": questions.to_dict(),
        }
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nOutput saved to: {output_path}")


def _create_parser() -> argparse.ArgumentParser:
    """Create the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="resume-parser",
        description="AI-powered resume parser that generates interview questions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to resume file (PDF or DOCX)",
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Path to save JSON output",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser


if __name__ == "__main__":
    sys.exit(main())
