"""Configuration management for the resume parser."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .constants import DEFAULT_ENV_PATH, DEFAULT_MODEL, DEFAULT_MAX_TOKENS


@dataclass
class Config:
    """Configuration class for resume parser."""

    openai_api_key: str
    model: str
    max_tokens: int

    @classmethod
    def from_env(cls, env_path: Optional[Path] = None) -> "Config":
        """Load configuration from environment variables.

        Args:
            env_path: Optional path to .env file. Defaults to project root.

        Returns:
            Config instance with settings from environment.

        Raises:
            ValueError: If required environment variables are missing.
        """
        path = env_path or DEFAULT_ENV_PATH
        load_dotenv(path)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please set it in your .env file."
            )

        return cls(
            openai_api_key=api_key,
            model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", str(DEFAULT_MAX_TOKENS))),
        )


_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get cached configuration instance.

    Returns:
        Config instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.from_env()
    return _config_instance


def reset_config() -> None:
    """Reset cached configuration instance."""
    global _config_instance
    _config_instance = None
