# Testing Guide for DocGen

Complete instructions for testing the DocGen presentation generation system.

---

## QUICK START: Manual Testing (5 minutes)

### Prerequisites
```bash
# 1. Navigate to project
cd docgen

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment (Windows)
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up .env file
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-actual-key-here
```

### Test 1: CLI Help (No API Key Required)
```bash
python main.py --help
```
**Expected Output:**
```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  DocGen - GenAI-Powered Presentation Generator

Options:
  --help  Show this message and exit.

Commands:
  generate   Generate a presentation from a topic
  info       Show template information
  templates  List available templates
```

**Result:** ✅ CLI framework working

---

### Test 2: List Templates (No API Key Required)
```bash
python main.py templates
```
**Expected Output:**
```
Available templates:
  1. corporate (templates/corporate/config.yaml)
  2. accenture (templates/accenture_template.pptx)
```

**Result:** ✅ Template detection working

---

### Test 3: Generate Simple Presentation (API Key Required)
```bash
python main.py generate --topic "Machine Learning Basics" --slides 4
```
**Expected Output:**
```
✅ Presentation generated successfully!
📁 Saved to: output/Machine_Learning_Basics.pptx
⏱️  Generation time: 22.5 seconds
📊 Slides created: 4
```

**Result:** ✅ Full pipeline working

---

### Test 4: Verify Output File
```bash
# Windows - open the file
start output/Machine_Learning_Basics.pptx

# Or verify file exists
dir output/
```

**Expected:**
- File exists: `Machine_Learning_Basics.pptx`
- Size: ~500 KB - 1 MB
- Opens in PowerPoint successfully
- Contains branded Accenture template
- 4 slides with content

**Result:** ✅ Output generation working

---

### Test 5: Generate with All Parameters
```bash
python main.py generate \
  --topic "Digital Transformation Strategy" \
  --slides 8 \
  --audience "Executive Leadership" \
  --tone professional \
  --style modern
```

**Expected Output:**
```
✅ Presentation generated successfully!
📁 Saved to: output/Digital_Transformation_Strategy.pptx
⏱️  Generation time: 28.3 seconds
📊 Slides created: 8
👥 Audience: Executive Leadership
🎨 Tone: professional
```

**Result:** ✅ Parameter handling working

---

## ADVANCED TESTING

### Test 6: Run Unit Tests
```bash
# Install testing dependencies
pip install pytest pytest-mock

# Run all tests
pytest tests/test_suite.py -v

# Run specific test
pytest tests/test_suite.py::test_config_loading -v

# Run with coverage
pytest tests/test_suite.py --cov=src --cov-report=html
```

**Expected:**
- All tests pass
- Coverage > 80%

---

### Test 7: Test Error Handling
```bash
# Test missing required parameter
python main.py generate

# Expected: Error message asking for --topic

# Test invalid API key (if using wrong key in .env)
python main.py generate --topic "Test" --slides 2

# Expected: Graceful error with helpful message
```

---

### Test 8: Test with Different Topics
Try various topics to test robustness:

```bash
# Technical topic
python main.py generate --topic "Kubernetes Architecture" --audience "DevOps Teams" --tone technical

# Business topic
python main.py generate --topic "Q4 Financial Results" --audience "Board of Directors" --tone professional

# Training topic
python main.py generate --topic "Getting Started with Python" --audience "New Developers" --tone casual

# Pitch topic
python main.py generate --topic "Cloud Migration Services" --slides 10 --tone persuasive
```

**Result:** ✅ System works with various inputs

---

### Test 9: Performance Testing
```bash
# Single generation (timing)
time python main.py generate --topic "Test Topic" --slides 6

# Multiple generations (stress test)
for i in {1..5}; do
  python main.py generate --topic "Topic $i" --slides 4
done
```

**Expected:**
- Single: 20-30 seconds
- Multiple: Each ~20-30 seconds
- No memory leaks or crashes
- All files created successfully

---

### Test 10: Brand Template Integration
```bash
# Generate with branded template (auto-detected)
python main.py generate --topic "Accenture Services" --slides 6

# Verify template was used:
# 1. Open output file
# 2. Check for Accenture colors (blue #003366, orange)
# 3. Check for consistent font styling
# 4. Verify master slides preserved
```

---

## AUTOMATED TEST SUITE

### Run Full Test Suite
```bash
# Navigate to project
cd docgen

# Run all tests with verbose output
pytest tests/test_suite.py -v

# Run with detailed failure output
pytest tests/test_suite.py -vv

# Run specific test class
pytest tests/test_suite.py::TestConfigLoading -v

# Run tests and generate HTML report
pytest tests/test_suite.py --html=report.html --self-contained-html
```

### Test Coverage
```bash
# Generate coverage report
pytest tests/test_suite.py --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/test_suite.py --cov=src --cov-report=html
```

---

## TEST CATEGORIES

### 1. Configuration Tests (No Dependencies)
```bash
pytest tests/test_suite.py::TestConfigLoading -v
```
Tests:
- Environment variable loading
- Default values
- Path configuration
- Template constraints

**Run Time:** ~1 second

---

### 2. Model Validation Tests (No Dependencies)
```bash
pytest tests/test_suite.py::TestModels -v
```
Tests:
- Slide outline creation
- Presentation outline validation
- Enum validation
- Type checking

**Run Time:** ~1 second

---

### 3. Template Tests (No Dependencies)
```bash
pytest tests/test_suite.py::TestTemplateManager -v
```
Tests:
- Template loading
- Template validation
- Available templates listing
- Error handling

**Run Time:** ~2 seconds

---

### 4. Content Generation Tests (Requires API Key)
```bash
pytest tests/test_suite.py::TestContentGenerator -v
```
Tests:
- Prompt engineering
- Response parsing
- Retry logic
- Error handling

**Run Time:** ~30 seconds (includes API calls)

**Note:** Set `SKIP_API_TESTS=1` to skip these:
```bash
SKIP_API_TESTS=1 pytest tests/test_suite.py -v
```

---

### 5. Content Validation Tests (No Dependencies)
```bash
pytest tests/test_suite.py::TestContentMapper -v
```
Tests:
- Text validation
- Constraint enforcement
- Slide adaptation
- Presentation validation

**Run Time:** ~2 seconds

---

### 6. Integration Tests (Requires API Key)
```bash
pytest tests/test_suite.py::TestIntegration -v
```
Tests:
- End-to-end pipeline
- File output
- Template integration
- Error handling

**Run Time:** ~30 seconds

---

## TROUBLESHOOTING TESTS

### Issue: Tests Skip with "API Key Not Configured"
**Solution:** Add OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-your-actual-key
```

### Issue: "Module not found" errors
**Solution:** Install in development mode:
```bash
pip install -e .
```

### Issue: Template tests fail
**Solution:** Verify template files exist:
```bash
ls templates/
ls templates/corporate/
ls templates/accenture_template.pptx
```

### Issue: File permission errors
**Solution:** Ensure write access to `output/` and `templates/`:
```bash
mkdir -p output
mkdir -p templates/brand_images
```

---

## CONTINUOUS TESTING

### Run Tests Automatically on File Change
```bash
# Install pytest-watch
pip install pytest-watch

# Run tests in watch mode
ptw tests/test_suite.py
```

---

## TEST RESULTS INTERPRETATION

### Passing Test
```
test_config_loading PASSED                                     [20%]
```
✅ Component working as expected

### Failing Test
```
test_content_generation FAILED                                 [40%]
```
❌ Check error message and debug

### Skipped Test
```
test_api_generation SKIPPED (requires API key)                 [60%]
```
⏭️ Skip condition triggered

### Error Test
```
test_template_loading ERROR                                    [80%]
```
❌ Unexpected exception occurred

---

## COMPLETE TEST RUN

### Quick Test (2 minutes)
```bash
# All tests except API-dependent ones
SKIP_API_TESTS=1 pytest tests/test_suite.py -v
```

### Full Test (2-3 minutes)
```bash
# All tests including API calls
pytest tests/test_suite.py -v
```

### Performance Test (5 minutes)
```bash
# Generate multiple presentations
python sample_generation.py
python main.py generate --topic "Test 1" --slides 5
python main.py generate --topic "Test 2" --slides 8
python main.py generate --topic "Test 3" --slides 6
```

---

## VALIDATION CHECKLIST

After testing, verify:

- [ ] CLI commands execute without errors
- [ ] `--help` shows all available options
- [ ] `templates` command lists available templates
- [ ] `generate` command creates .pptx files
- [ ] Output files open successfully in PowerPoint
- [ ] Generated content is relevant to topic
- [ ] Accenture branding is applied
- [ ] File sizes are reasonable (~500KB - 1MB)
- [ ] No API errors with valid key
- [ ] Graceful error handling with invalid inputs
- [ ] Generation time is 20-30 seconds
- [ ] All unit tests pass
- [ ] Test coverage > 80%

---

## TEST EXECUTION WORKFLOW

### For Initial Setup Testing
```bash
# 1. Verify environment
python main.py --help

# 2. List templates
python main.py templates

# 3. Generate simple test
python main.py generate --topic "Python Programming" --slides 4

# 4. Verify output
start output/Python_Programming.pptx
```

### For Quality Assurance
```bash
# 1. Run unit tests
pytest tests/test_suite.py -v

# 2. Run with coverage
pytest tests/test_suite.py --cov=src

# 3. Manual testing with various topics
python main.py generate --topic "Cloud Architecture" --audience "Engineers" --tone technical

# 4. Verify branding
# Open output file and check design
```

### For Performance Validation
```bash
# 1. Single generation timing
time python main.py generate --topic "Test" --slides 6

# 2. Multiple generations
for i in {1..3}; do python main.py generate --topic "Topic$i"; done

# 3. Monitor system resources
# Task Manager or similar
```

---

## NEXT STEPS

After successful testing:

1. ✅ System is working correctly
2. ✅ Ready for production use
3. ✅ Can generate presentations for real topics
4. ✅ Template integration verified
5. ✅ All components integrated successfully

**Start generating presentations!**

```bash
python main.py generate --topic "Your Topic Here" --slides 8
```

---

## SUPPORT

If tests fail:
1. Check `.env` has valid OpenAI API key
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Ensure Python 3.8+: `python --version`
4. Check internet connection for API calls
5. Review error messages carefully for specific issues
6. Consult README.md and SETUP.md for detailed setup
