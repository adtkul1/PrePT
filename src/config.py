"""
Configuration management for DocGen
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please create a .env file with your API key."
    )

MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))

# Generation Settings
DEFAULT_SLIDES = int(os.getenv("DEFAULT_SLIDES", "6"))
DEFAULT_TEMPLATE = os.getenv("DEFAULT_TEMPLATE", "corporate")
DEFAULT_TONE = os.getenv("DEFAULT_TONE", "professional")

# Template Constraints
SLIDE_CONSTRAINTS = {
    "title_max_length": 80,
    "subtitle_max_length": 100,
    "bullet_max_length": 120,
    "bullets_per_slide": (3, 5),
    "min_chars_per_bullet": 20,
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
