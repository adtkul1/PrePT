# Quick Test Reference Card

## Three Ways to Test

### 1️⃣ FASTEST: Quick Test Script (2 minutes)
```bash
python quick_test.py
```
**What it tests:**
- ✅ CLI interface
- ✅ Template loading
- ✅ Configuration
- ✅ Data models
- ✅ All basic components
- ✅ Unit tests

**Good for:** Quick validation that everything works

---

### 2️⃣ STANDARD: Manual CLI Testing (5 minutes)
```bash
# 1. Test help
python main.py --help

# 2. List templates
python main.py templates

# 3. Generate presentation
python main.py generate --topic "Cloud Computing" --slides 6

# 4. Find output
ls output/
```

**What it tests:**
- ✅ User interface
- ✅ Parameter handling
- ✅ File generation
- ✅ Output quality

**Good for:** Real-world usage scenarios

---

### 3️⃣ COMPREHENSIVE: Full Test Suite (5-10 minutes)
```bash
# Install test dependencies
pip install pytest pytest-mock pytest-cov

# Run all tests with coverage
pytest tests/test_suite.py -v --cov=src --cov-report=html
```

**What it tests:**
- ✅ All code paths
- ✅ Edge cases
- ✅ Error handling
- ✅ Integration points
- ✅ API functionality
- ✅ Code coverage (>80%)

**Good for:** Quality assurance and debugging

---

## Setup Before Testing

```bash
# 1. Navigate to project
cd docgen

# 2. Create virtual environment (first time only)
python -m venv venv

# 3. Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env with API key
cp .env.example .env
# Edit .env and add:
# OPENAI_API_KEY=sk-your-actual-key

# 6. Ready to test!
```

---

## Test Matrix

| Test | Command | Time | Requires API | Dependencies |
|------|---------|------|--------------|--------------|
| **Help** | `python main.py --help` | 1s | No | None |
| **Templates** | `python main.py templates` | 1s | No | None |
| **Config** | `python -c "from config import *"` | 1s | No | None |
| **Models** | `python -c "from models import *"` | 1s | No | Pydantic |
| **Templates** | `python -c "from template_manager import *"` | 2s | No | PyYAML |
| **Quick Test** | `python quick_test.py` | 2m | Optional | pytest |
| **Unit Tests** | `pytest tests/test_suite.py -v` | 2-3m | No | pytest |
| **Full Tests** | `pytest tests/test_suite.py -v` | 2-3m | Yes | pytest |
| **Generation** | `python main.py generate --topic "X"` | 30s | Yes | OpenAI |

---

## Expected Outputs

### Test 1: Help Works ✅
```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  DocGen - GenAI-Powered Presentation Generator

Commands:
  generate
  info
  templates
```

### Test 2: Templates Listed ✅
```
Available templates:
  1. corporate (YAML-based)
  2. accenture (Branded .pptx)
```

### Test 3: Generation Works ✅
```
✅ Presentation generated successfully!
📁 Saved to: output/Cloud_Computing.pptx
⏱️  Generation time: 24.5 seconds
📊 Slides created: 6
```

### Test 4: File Exists ✅
```
output/Cloud_Computing.pptx exists
File size: ~750 KB
Opens successfully in PowerPoint
Content is relevant and professional
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### "API key not configured"
```bash
# Solution: Add to .env
OPENAI_API_KEY=sk-your-actual-key
```

### "generation takes too long" (>60 seconds)
```bash
# Normal: 20-30 seconds per presentation
# > 60 seconds might indicate:
# - Network latency to OpenAI API
# - API rate limits
# - High system load
# Just wait or try again
```

### "Tests pass/fail inconsistently"
```bash
# Solution: Check internet connection
# API calls can be slow or fail intermittently
# Run again or check OpenAI status
```

### "Output directory permission denied"
```bash
# Solution: Ensure write permissions
mkdir -p output
chmod 755 output
```

---

## Validation Checklist

Run through this checklist to confirm everything works:

- [ ] Python 3.8+ installed: `python --version`
- [ ] Virtual environment activated: `(venv)` in prompt
- [ ] Dependencies installed: `pip list | grep openai`
- [ ] .env file created: `.env` exists in docgen/ folder
- [ ] API key configured: `OPENAI_API_KEY` starts with `sk-`
- [ ] `python main.py --help` shows CLI options
- [ ] `python main.py templates` lists templates
- [ ] `python quick_test.py` passes
- [ ] `pytest tests/test_suite.py -v` passes
- [ ] `python main.py generate --topic "Test"` creates .pptx
- [ ] Output file opens in PowerPoint

---

## Performance Expectations

### Generation Time Breakdown
```
Configuration Load:    ~1 second
GenAI API Call:        ~15-20 seconds (network dependent)
Content Validation:    ~1 second
PPTX Creation:         ~2-3 seconds
Total:                 ~20-30 seconds
```

### File Sizes
- Single 6-slide presentation: 500 KB - 1 MB
- Generation with full branding: 750 KB - 1.5 MB
- Normal range: 300 KB - 2 MB

### Resource Usage
- Memory: ~200-300 MB during generation
- Disk: ~1-2 MB for output files
- Network: ~100-200 KB (OpenAI API)

---

## Test Results Interpretation

### ✅ All Tests Pass
- System is working correctly
- Ready for production use
- Can start generating real presentations

### ⚠️ Some Tests Fail
1. Check error messages carefully
2. Verify API key is set correctly
3. Check internet connection
4. Review SETUP.md for detailed configuration
5. Run tests again (might be temporary)

### ⏭️ Tests Skipped
- This is normal! Some tests skip if:
  - API key not configured (intentional)
  - Optional dependencies not installed
  - Environment variables not set
- Read skip messages for details

---

## Quick Commands Reference

```bash
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Test (fast)
python quick_test.py

# Test (comprehensive)
pytest tests/test_suite.py -v

# Generate
python main.py generate --topic "Your Topic"

# List templates
python main.py templates

# Show help
python main.py --help
```

---

## Next Steps After Successful Testing

1. ✅ System validated
2. ✅ All components working
3. ✅ Ready to generate presentations

**Start using:**
```bash
python main.py generate --topic "Your Topic" --slides 8
```

**Output will be in:** `output/Your_Topic.pptx`

---

**Any issues? Check TESTING.md or SETUP.md for detailed help!**
