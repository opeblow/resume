"""Constants used throughout the resume parser."""

from pathlib import Path

SUPPORTED_FILE_EXTENSIONS = {".pdf", ".docx"}

DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.0
QUESTION_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096

NUM_TECHNICAL_QUESTIONS = 5
NUM_BEHAVIORAL_QUESTIONS = 5

PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"

OUTPUT_FIELDS = ["skills", "experience", "education", "job_titles"]

DEFAULT_EXPERIENCE = "Not specified"
