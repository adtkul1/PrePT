# DocGen: AI-Powered Presentation Generator

Automatically generate professional branded presentations using GenAI. Simply provide a topic, and DocGen handles content creation, template application, and PPTX generation.

## Features

✨ **AI-Powered Content Generation**: Uses OpenAI's GPT models to create compelling presentation outlines and content
- Multi-stage generation for quality and consistency
- Prompt engineering for constraint-aware output
- Intelligent content structuring

📐 **Branded Template System**: Professional template framework
- **Accenture branded template** (TEMPLATE 2026.pptx) integration
- Master slide preservation and theme consistency
- Color schemes and typography management
- Multiple slide layouts with automatic placeholder mapping
- Layout constraint enforcement

🖼️ **Brand Assets Integration**: Connect to your brand library
- SharePoint image support for brand assets
- Local caching of downloaded images
- Automatic image injection into template placeholders
- Support for logos, headers, and design elements

🔧 **Smart Content Mapping**: Ensures generated content fits template perfectly
- Automatic text validation and truncation
- Template placeholder detection and mapping
- Layout-aware content adaptation
- Prevents design breakage

⚡ **Fast & Scalable**: POC designed for extensibility
- Clean architecture for easy template additions
- Modular design for feature expansion
- CLI for quick iteration

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- pip (Python package manager)

### Installation

1. **Clone/Navigate to project**:
```bash
cd docgen
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up API key**:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`:
     ```
     OPENAI_API_KEY=sk-your-key-here
     ```

### Basic Usage

**🎯 With Branded Accenture Template (Automatic)**:

The system automatically detects and uses your branded Accenture template. Simply generate:

```bash
python main.py generate --topic "Digital Transformation Strategy" --slides 8
```

**Generate a presentation**:
```bash
python main.py generate --topic "The Future of AI in Business" --slides 6
```

**Available options**:
```bash
python main.py generate --help
```

```
Usage: main.py generate [OPTIONS]

Options:
  --topic TEXT          Presentation topic (prompted if not provided)
  --slides INTEGER      Number of slides (default: 6, range: 3-20)
  --template TEXT       Template name (default: corporate)
  --audience TEXT       Target audience (optional)
  --tone TEXT           Tone: professional, casual, technical
  --output PATH         Custom output file path
  --help                Show help message
```

**View available templates**:
```bash
python main.py templates
```

**Get template details**:
```bash
python main.py info --template corporate
```

## Example Usage

### Professional Business Presentation
```bash
python main.py generate \
  --topic "Digital Transformation Strategy" \
  --slides 8 \
  --audience "C-Level Executives" \
  --tone professional
```

### Technical Deep Dive
```bash
python main.py generate \
  --topic "Machine Learning Implementation Best Practices" \
  --slides 10 \
  --audience "Engineering Teams" \
  --tone technical
```

### Casual Overview
```bash
python main.py generate \
  --topic "Getting Started with Cloud Computing" \
  --slides 6 \
  --tone casual
```

## Architecture Overview

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface                            │
│              (src/cli.py - User Entry Point)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           PresentationOrchestrator                           │
│    (src/orchestrator.py - Pipeline Orchestration)           │
└─────────────┬────────────────────────┬──────────────────────┘
              │                        │
              ▼                        ▼
┌──────────────────────────┐  ┌──────────────────────┐
│  ContentGenerator        │  │  TemplateManager     │
│  (src/content_generator) │  │  (template_manager)  │
│                          │  │                      │
│ - GenAI API calls        │  │ - Load templates     │
│ - Outline generation     │  │ - Manage configs     │
│ - Multi-stage prompting  │  │ - Validate layouts   │
└───────────┬──────────────┘  └──────────┬───────────┘
            │                           │
            └──────────┬────────────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │   ContentMapper             │
         │  (src/orchestrator.py)      │
         │                             │
         │ - Validate constraints      │
         │ - Adapt content             │
         │ - Ensure layout safety      │
         └────────────┬────────────────┘
                      │
                      ▼
         ┌─────────────────────────────┐
         │  PresentationBuilder        │
         │ (presentation_builder.py)   │
         │                             │
         │ - Build PPTX slides         │
         │ - Apply styling             │
         │ - Save output               │
         └────────────┬────────────────┘
                      │
                      ▼
                  PPTX File
```

### Data Flow

1. **Input**: User provides topic and parameters
2. **Generation**: ContentGenerator creates outline via GPT API
3. **Mapping**: ContentMapper adapts content to template constraints
4. **Building**: PresentationBuilder creates PPTX with styling
5. **Output**: Branded PPTX presentation file

### Key Classes

- **ContentGenerator**: Manages LLM API interactions, prompt engineering, JSON parsing
- **TemplateManager**: Loads and validates template configurations
- **ContentMapper**: Validates slide content against constraints, adapts oversized content
- **PresentationBuilder**: Constructs PPTX slides with proper formatting
- **PresentationOrchestrator**: Coordinates the entire pipeline

## Project Structure

```
docgen/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusions
│
├── DESIGN_OVERVIEW.md        # Design documentation
├── README.md                 # This file
├── SETUP.md                  # Setup instructions
├── EXAMPLES.md               # Usage examples
├── BRANDED_ASSETS.md         # Brand integration guide
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── models.py             # Data models (Pydantic)
│   ├── cli.py                # CLI interface
│   ├── content_generator.py  # GenAI integration
│   ├── template_manager.py   # Template system
│   ├── presentation_builder.py # PPTX generation
│   ├── orchestrator.py       # Pipeline orchestration
│   └── branded_template.py   # Branded template handling
│
├── templates/
│   ├── accenture_template.pptx  # Branded Accenture template
│   ├── brand_images/            # Brand assets (local cache)
│   └── corporate/               # Fallback template
│       ├── config.yaml
│       └── theme/
│
├── tests/                    # Unit tests (placeholder)
│
└── output/                   # Generated presentations (auto-created)
```

## Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (defaults shown)
MODEL=gpt-3.5-turbo
MAX_RETRIES=3
TIMEOUT_SECONDS=30
DEFAULT_SLIDES=6
DEFAULT_TEMPLATE=corporate
DEFAULT_TONE=professional
```

### Template Constraints

Defined in `templates/corporate/config.yaml`:

```yaml
constraints:
  title_max_length: 80
  subtitle_max_length: 100
  bullet_max_length: 120
  bullets_per_slide: 5
  slides_minimum: 3
  slides_maximum: 20
```

These constraints are:
1. Included in GenAI prompts to guide generation
2. Enforced by ContentMapper for safety
3. Configurable per template

## Content Generation Strategy

### Multi-Stage Approach

**Stage 1: Outline Generation**
- Generates high-level slide structure
- Ensures consistency before detail
- Returns JSON with slide types and titles

**Stage 2: Detailed Content** (future)
- Expands bullets and speaker notes
- Adds supporting details
- Generates visual suggestions

### Prompt Engineering

System prompt includes:
- Professional context and guidelines
- Output format specification (JSON schema)
- Template constraints
- Target audience and tone

User prompt includes:
- Topic and purpose
- Slide structure requirements
- Audience context
- Constraint reminders

This ensures GenAI output is:
- Properly structured
- Constraint-aware
- Consistent with template
- Ready for mapping

## Error Handling

- **API Errors**: Automatic retry with exponential backoff
- **Content Validation**: Pre-flight checks before PPTX creation
- **Layout Safety**: Automatic text truncation if content oversized
- **Schema Validation**: Pydantic models enforce data integrity

## Extensibility

### Adding a New Template

1. Create `templates/new-template/` directory
2. Add `config.yaml` with colors, fonts, layouts
3. Create `theme/colors.json` and `fonts.json`
4. Reference in CLI choice options

### Changing Generation Logic

- Edit prompts in `src/content_generator.py`
- Adjust multi-stage strategy
- Add custom validation rules

### Custom Output Formats

Replace `PresentationBuilder` with:
- HTML/CSS for web slides
- PDF with custom rendering
- Markdown for documentation

## Current Limitations & Future Work

### Current (POC)
- Single template (corporate)
- Basic slide layouts (title, content, closing)
- No image/chart generation
- No speaker notes rendering

### Future Enhancements
- Multiple templates library
- REST API for programmatic access
- Web UI for non-technical users
- Multi-language support
- Image and chart generation
- Real-time preview
- Team collaboration features

## Troubleshooting

### "OPENAI_API_KEY not set"
```bash
# Check .env file exists and has valid key
cat .env | grep OPENAI_API_KEY
```

### API timeout errors
```bash
# Increase timeout in .env
TIMEOUT_SECONDS=60
```

### "Template not found"
```bash
# Check available templates
python main.py templates
```

### Content truncation
Check the generated PPTX. If text is truncated:
1. Use shorter topic or reduce slides
2. Adjust `SLIDE_CONSTRAINTS` in `config.py`
3. Check template `config.yaml` constraints

## Development

### Running Tests (Future)
```bash
pytest tests/
```

### Code Style
Uses Python conventions (PEP 8):
```bash
# Format code (optional)
black src/
```

## Technologies Used

| Component | Technology | Why |
|-----------|-----------|-----|
| GenAI | OpenAI GPT-3.5/4 | Industry standard, JSON support |
| PPTX | python-pptx | Pure Python, no Office dependency |
| CLI | Click | User-friendly, professional |
| Data Models | Pydantic | Validation, type safety |
| Config | YAML | Human-readable template configs |

## Performance

- **Outline Generation**: ~10-15 seconds (API latency)
- **PPTX Creation**: ~2-3 seconds (local processing)
- **Total Time**: ~15-20 seconds per presentation

## Security

- API key stored in local `.env` (not committed)
- No data sent to external servers except OpenAI
- No authentication needed for CLI (local use)
- Input validation prevents injection attacks

## Support & Feedback

For issues, feature requests, or improvements:
1. Check `DESIGN_OVERVIEW.md` for architecture details
2. Review code comments in `src/` modules
3. Test with `--help` for command options

## License

Internal project for technical assessment.

---

**Version**: 0.1.0  
**Last Updated**: February 2026
