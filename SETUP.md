# Setup & Quick Start Guide

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux
- **Internet**: Required for OpenAI API calls

## Step-by-Step Setup

### 1. Prerequisites

Ensure Python is installed:
```bash
python --version
# Python 3.8.0 or higher required
```

### 2. Project Setup

**Option A: From Existing Directory**
```bash
cd path/to/docgen
```

**Option B: Clone or Extract**
```bash
# If from git repository
git clone <repository-url>
cd docgen

# Or if from zip file
unzip docgen.zip
cd docgen
```

### 3. Virtual Environment

Create an isolated Python environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Verify installation:
```bash
pip list
# Should show: openai, python-pptx, click, pydantic, etc.
```

### 5. Configure OpenAI API Key

**Get your API key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Copy the key (you won't see it again)

**Add to .env file:**
```bash
# Copy template
cp .env.example .env

# Edit .env (Windows: notepad .env, Mac/Linux: nano .env)
# Add your API key:
OPENAI_API_KEY=sk-your-actual-key-here
```

**Security note**: Never commit `.env` file to git (it's in `.gitignore`)

### 6. Verify Setup

Test the installation:
```bash
# Check CLI works
python main.py --help

# List available templates
python main.py templates

# Show template details
python main.py info --template corporate
```

You should see help output and the corporate template listed.

## First Generation

### Quick Test

Generate your first presentation:
```bash
python main.py generate --topic "Getting Started with Python" --slides 5
```

This will:
1. Validate your OpenAI API key
2. Generate a 5-slide outline via GPT
3. Map content to the corporate template
4. Create `output/Getting_Started_with_Python.pptx`

### Monitor Progress

The CLI shows status updates:
```
🚀 Generating presentation: 'Getting Started with Python'
Loaded template: corporate
Generating content with GenAI...
Generated outline with 5 slides
Validating and adapting content...
Building presentation...
✅ Presentation generated successfully!
📁 Saved to: .../output/Getting_Started_with_Python.pptx
```

### Open Your Presentation

The PPTX file is ready to use:
- Open with Microsoft PowerPoint
- Or Google Slides (upload the file)
- Or LibreOffice Impress

## Common Tasks

### Generate with Custom Parameters

```bash
python main.py generate \
  --topic "Digital Transformation Strategy" \
  --slides 8 \
  --audience "Executive Leadership Team" \
  --tone professional \
  --output "my_presentation.pptx"
```

### Different Tones

```bash
# Professional (default)
python main.py generate --topic "Strategic Planning" --tone professional

# Casual
python main.py generate --topic "Fun with Data" --tone casual

# Technical
python main.py generate --topic "API Design Patterns" --tone technical
```

### Vary Slide Count

```bash
python main.py generate --topic "Your Topic" --slides 10  # 10 slides
python main.py generate --topic "Your Topic" --slides 3   # 3 slides (minimum)
python main.py generate --topic "Your Topic" --slides 20  # 20 slides (maximum)
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openai'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "OPENAI_API_KEY environment variable is not set"

**Solution:**
```bash
# Verify .env file exists
ls -la .env  # macOS/Linux: ls -la .env

# Check API key is set
cat .env | grep OPENAI_API_KEY

# If missing, add it to .env:
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Issue: "Invalid API Key"

**Solution:**
1. Go to https://platform.openai.com/api-keys
2. Verify the key hasn't been deactivated
3. Create a new key if needed
4. Update `.env` with new key

### Issue: API timeout after 30 seconds

**Solution:**
```bash
# Edit .env to increase timeout
TIMEOUT_SECONDS=60

# Or increase MAX_RETRIES
MAX_RETRIES=5
```

### Issue: Text appears truncated in PowerPoint

**Solution:**
- Some fonts may render differently across systems
- Open in PowerPoint and adjust if needed
- Or use fewer slides or shorter topics

## Development Workflow

### Making Changes

```bash
# Activate environment
source venv/bin/activate  # macOS/Linux

# Edit code
code src/cli.py  # Using VSCode, or any editor

# Test changes
python main.py generate --topic "Test Topic" --slides 3

# Commit changes
git add -A
git commit -m "Feature: Add X functionality"
```

### Adding a New Feature

1. Create new module in `src/`
2. Add imports to `cli.py` or orchestrator
3. Test thoroughly
4. Commit with clear message

### Testing

Currently minimal tests. To add:
```bash
# Create test file
touch tests/test_content_generator.py

# Add test code
# Run tests
pytest tests/
```

## Project Structure Quick Reference

```
docgen/
├── main.py              ← Entry point (python main.py)
├── README.md            ← Full documentation
├── SETUP.md            ← This file
├── DESIGN_OVERVIEW.md  ← Architecture & design
│
├── src/
│   ├── cli.py          ← Command-line interface
│   ├── config.py       ← Settings & API keys
│   ├── content_generator.py  ← GenAI integration
│   ├── template_manager.py   ← Template loading
│   ├── presentation_builder.py ← PPTX generation
│   ├── orchestrator.py ← Pipeline coordinator
│   └── models.py       ← Data structures
│
├── templates/
│   └── corporate/      ← Branded template
│       ├── config.yaml ← Colors, fonts, layouts
│       └── theme/
│
├── output/             ← Generated presentations (auto-created)
├── tests/              ← Unit tests (future)
├── requirements.txt    ← Python packages
├── .env.example       ← Template for .env
└── .gitignore         ← Git exclusions
```

## Next Steps

1. ✅ **Setup complete** - You've installed DocGen
2. 📝 **Generate presentations** - Try the quick test above
3. 📖 **Read documentation** - Check README.md for full details
4. 🎨 **Customize templates** - Edit `templates/corporate/config.yaml`
5. 🚀 **Extend functionality** - Add features as needed

## Tips & Best Practices

### Topic Selection
- Be specific: "Digital Transformation in Healthcare" not "Technology"
- Include context: "Remote Work Best Practices for Engineers"
- Keep it clear: Avoid ambiguous or very long topics

### Slide Count
- 6 slides: Quick overview (default)
- 8-10 slides: Standard presentation
- 15+ slides: Deep dive/training

### Target Audience
- Always provide if generating for specific group
- GenAI adjusts language and complexity accordingly
- Example: "--audience 'High School Students'"

### Tone Selection
- **professional**: Business, conferences, proposals
- **casual**: Internal meetings, informal sharing
- **technical**: Engineering teams, technical audiences

## Getting Help

### Check Existing Documentation
- [README.md](README.md) - Full feature documentation
- [DESIGN_OVERVIEW.md](DESIGN_OVERVIEW.md) - Architecture details
- Command help: `python main.py --help`

### Common Questions

**Q: Can I edit the presentation after generation?**
A: Yes! Open the PPTX in PowerPoint and edit normally.

**Q: Can I use different templates?**
A: Currently, only "corporate" template included. More coming soon.

**Q: Does it need internet?**
A: Yes, for OpenAI API calls. Local PPTX creation is instant.

**Q: What if I run out of API credits?**
A: Check your OpenAI usage at https://platform.openai.com/account/usage/limits

## Feedback & Issues

Document any issues:
- Check `.env` configuration first
- Review generated PowerPoint content
- Test with different topics
- Try adjusting --slides parameter

---

**Ready to generate awesome presentations! 🎉**

For detailed architecture information, see [DESIGN_OVERVIEW.md](DESIGN_OVERVIEW.md).
