"""
Configuration management for DocGen
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
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
# NOTE: Do NOT raise on import. Unit tests expect config to load with no API key.
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

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

# Logging (fix: remove trailing comma that turns this into a tuple)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# A single dict export expected by tests
CONFIG: Dict[str, Any] = {
    "PROJECT_ROOT": PROJECT_ROOT,
    "TEMPLATES_DIR": TEMPLATES_DIR,
    "OUTPUT_DIR": OUTPUT_DIR,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "MODEL": MODEL,
    "MAX_RETRIES": MAX_RETRIES,
    "TIMEOUT_SECONDS": TIMEOUT_SECONDS,
    "DEFAULT_SLIDES": DEFAULT_SLIDES,
    "DEFAULT_TEMPLATE": DEFAULT_TEMPLATE,
    "DEFAULT_TONE": DEFAULT_TONE,
    "SLIDE_CONSTRAINTS": SLIDE_CONSTRAINTS,
    "LOG_LEVEL": LOG_LEVEL,
}