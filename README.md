# AI Resume Parser

## Color Palette

### Light Mode
| Variable | Color | Hex |
|----------|-------|-----|
| Text | Gray | `#6b6375` |
| Text (Headings) | Near Black | `#08060d` |
| Background | White | `#fff` |
| Border | Light Gray | `#e5e4e7` |
| Code Background | Off White | `#f4f3ec` |
| Accent | Purple | `#aa3bff` |
| Accent Background | Light Purple | `rgba(170, 59, 255, 0.1)` |
| Accent Border | Medium Purple | `rgba(170, 59, 255, 0.5)` |

### Dark Mode
| Variable | Color | Hex |
|----------|-------|-----|
| Text | Light Gray | `#9ca3af` |
| Text (Headings) | Off White | `#f3f4f6` |
| Background | Dark | `#16171d` |
| Border | Dark Gray | `#2e303a` |
| Code Background | Darker | `#1f2028` |
| Accent | Light Purple | `#c084fc` |
| Accent Background | Light Purple | `rgba(192, 132, 252, 0.15)` |
| Accent Border | Medium Purple | `rgba(192, 132, 252, 0.5)` |

<p align="center">
  AI-powered resume parser that extracts structured data and generates custom interview questions.
</p>

## Table of Contents

*   [Overview](#overview)
*   [Features](#features)
*   [Prerequisites](#prerequisites)
*   [Installation](#installation)
*   [Configuration](#configuration)
*   [Usage](#usage)
*   [Project Structure](#project-structure)
*   [Troubleshooting](#troubleshooting)

## Overview

Resume Parser is an AI-powered tool that:

1.  Extracts text from PDF or DOCX resume files
2.  Parses structured data (skills, experience, education, job titles) using OpenAI GPT-4o
3.  Generates tailored technical and behavioral interview questions

## Features

*   **Multi-format support**: PDF and DOCX resume parsing
*   **Structured extraction**: Skills, experience, education, job titles
*   **Interview question generation**: 5 technical + 5 behavioral questions
*   **Clean JSON output**: Easy integration with other systems
*   **Command-line interface**: Simple and efficient workflow

## Prerequisites

*   Python 3.10 or higher
*   OpenAI API key

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/opeblow/resume.git
cd resume-parser
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-api-key-here
```

Optional configuration (defaults shown):

```
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
```

## Usage

### Basic usage

```bash
python main.py path/to/resume.pdf
```

### With output file

```bash
python main.py path/to/resume.pdf -o output.json
```

### Verbose logging

```bash
python main.py path/to/resume.pdf -v
```

### Command-line options

| Option | Description |
|--------|-------------|
| `file` | Path to resume file (PDF or DOCX) |
| `-o, --output` | Path to save JSON output |
| `-v, --verbose` | Enable verbose logging |

### Using as a Python module

```python
from src.resume_parser.extraction import extract_text_from_resume, clean_text
from src.resume_parser.parser import parse_resume
from src.resume_parser.question_generator import generate_questions

# Extract text
raw_text = extract_text_from_resume("resume.pdf")
cleaned = clean_text(raw_text)

# Parse resume
parsed = parse_resume(cleaned)

# Generate questions
questions = generate_questions(parsed)

print(parsed.to_dict())
print(questions.to_dict())
```

## Project Structure

```
resume-parser/
├── src/
│   └── resume_parser/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface
│       ├── config.py            # Configuration management
│       ├── constants.py        # Application constants
│       ├── extraction.py       # Text extraction (PDF/DOCX)
│       ├── logging_config.py   # Logging configuration
│       ├── parser.py            # Resume parsing logic
│       └── question_generator.py # Question generation
├── main.py                      # Entry point
├── requirements.txt              # Python dependencies
├── .env                         # Environment variables (create this)
└── README.md                    # This file
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o` | OpenAI model to use |
| `OPENAI_MAX_TOKENS` | No | `4096` | Max tokens for API calls |

## Troubleshooting

### "OPENAI_API_KEY not found"

Make sure your `.env` file exists and contains a valid `OPENAI_API_KEY`.

### "Unsupported file format"

Ensure your resume is in PDF or DOCX format.

### "Failed to extract text"

The PDF may be scanned or password-protected. Ensure it's a text-based PDF.

### API rate limits

If you hit rate limits, you may need to upgrade your OpenAI plan or add retry logic.

## License

MIT License
