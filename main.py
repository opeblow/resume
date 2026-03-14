"""Resume Parser CLI Entry Point.

This module provides a simple entry point for running the resume parser
from the command line.
"""

import sys

from src.resume_parser.cli import main

if __name__ == "__main__":
    sys.exit(main())
