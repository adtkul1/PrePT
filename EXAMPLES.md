# DocGen Usage Examples

This document provides real-world examples of using DocGen for different scenarios.

## Example 1: Executive Summary on AI Strategy

**Command:**
```bash
python main.py generate \
  --topic "Artificial Intelligence Strategy for 2025" \
  --slides 8 \
  --audience "Board of Directors" \
  --tone professional
```

**What happens:**
1. GenAI creates 8-slide outline appropriate for executives
2. Uses professional tone with business-focused language
3. Includes strategic messaging and ROI implications
4. Corporate template with conservative styling

**Output:** `output/Artificial_Intelligence_Strategy_for_2025.pptx`

**Expected content:**
- Slide 1: Title with company context
- Slide 2: Current state and market opportunity
- Slide 3: AI adoption benefits
- Slide 4: Implementation roadmap
- Slide 5: Risk mitigation
- Slide 6: Resource requirements
- Slide 7: Timeline and milestones
- Slide 8: Call to action / Next steps

---

## Example 2: Technical Training for Engineering Team

**Command:**
```bash
python main.py generate \
  --topic "Kubernetes Best Practices and Deployment Patterns" \
  --slides 10 \
  --audience "Platform Engineering Team" \
  --tone technical
```

**What happens:**
1. Generates 10 slides with technical depth
2. Uses engineering terminology and best practices
3. Includes architecture considerations
4. Technical tone with detailed explanations

**Output:** `output/Kubernetes_Best_Practices.pptx`

**Expected content:**
- Slide 1: Overview and objectives
- Slide 2: Architecture fundamentals
- Slide 3: Deployment patterns
- Slide 4: StatefulSet vs Deployment
- Slide 5: Network policies
- Slide 6: Storage considerations
- Slide 7: Resource management
- Slide 8: Monitoring and observability
- Slide 9: Common pitfalls
- Slide 10: Hands-on next steps

---

## Example 3: Casual Internal Knowledge Share

**Command:**
```bash
python main.py generate \
  --topic "Our Team's Productivity Tools Review" \
  --slides 6 \
  --tone casual
```

**What happens:**
1. Creates 6-slide overview
2. Casual, conversational language
3. Includes practical insights
4. Relaxed tone suitable for team meeting

**Output:** `output/Our_Team_Productivity_Tools_Review.pptx`

**Expected content:**
- Slide 1: Fun introduction
- Slide 2: Tools we use and why
- Slide 3: What's working well
- Slide 4: Pain points
- Slide 5: Tools to try next
- Slide 6: Let's discuss

---

## Example 4: Customer-Facing Solution Overview

**Command:**
```bash
python main.py generate \
  --topic "Cloud Migration Strategy: Benefits and Implementation Timeline" \
  --slides 7 \
  --audience "Fortune 500 CTO" \
  --tone professional \
  --output "cloud_migration_proposal.pptx"
```

**What happens:**
1. Professional, persuasive content for decision-maker
2. Business benefits highlighted
3. Clear implementation roadmap
4. Custom output filename for distribution

**Output:** `cloud_migration_proposal.pptx`

---

## Example 5: Educational Content

**Command:**
```bash
python main.py generate \
  --topic "Introduction to Machine Learning for Beginners" \
  --slides 12 \
  --audience "MBA Students" \
  --tone professional
```

**What happens:**
1. Creates 12 comprehensive slides
2. Suitable for university-level teaching
3. Clear learning progression
4. Balances theory with practical examples

---

## Example 6: Quick Brainstorm Session

**Command:**
```bash
python main.py generate \
  --topic "Emerging technologies in retail" \
  --slides 5
```

**What happens:**
1. Quick 5-slide overview (minimum slides)
2. Default professional tone
3. No specific audience adjustment
4. Ready for immediate meeting presentation

---

## Example 7: Deep Technical Specification

**Command:**
```bash
python main.py generate \
  --topic "Microservices Architecture: Design Patterns and Trade-offs" \
  --slides 15 \
  --audience "Engineering Architecture Committee" \
  --tone technical
```

**What happens:**
1. Extended 15-slide deep dive
2. Technical decision framework
3. Architecture patterns and alternatives
4. Suitable for architecture review board

---

## Working with Generated Content

### Editing After Generation

All outputs are standard PPTX files. You can:

1. **Edit in PowerPoint:**
   - Right-click slide to change layout
   - Edit text directly
   - Add images or charts
   - Adjust colors within theme

2. **Edit in Google Slides:**
   - Upload to Google Drive
   - "Open with > Google Slides"
   - Make collaborative edits

3. **Convert to PDF:**
   - File > Export As > PDF
   - Perfect for sharing read-only versions

### Combining Multiple Presentations

```bash
# Generate multiple decks
python main.py generate --topic "Topic 1" --slides 5 --output deck1.pptx
python main.py generate --topic "Topic 2" --slides 4 --output deck2.pptx

# Merge in PowerPoint:
# Open deck1.pptx
# Insert > Slides from File > Choose deck2.pptx
```

### Batch Generation

Create a script to generate multiple presentations:

**batch_generate.sh** (macOS/Linux):
```bash
#!/bin/bash

# Activate environment
source venv/bin/activate

# Generate multiple presentations
python main.py generate --topic "Q1 Planning" --slides 6 --audience "Department Heads"
python main.py generate --topic "Product Roadmap" --slides 8 --audience "Product Team"
python main.py generate --topic "Security Review" --slides 7 --audience "Security Team"
python main.py generate --topic "Budget Planning" --slides 5 --audience "Finance"

echo "Batch generation complete!"
ls output/
```

**batch_generate.bat** (Windows):
```batch
@echo off
call venv\Scripts\activate

python main.py generate --topic "Q1 Planning" --slides 6 --audience "Department Heads"
python main.py generate --topic "Product Roadmap" --slides 8 --audience "Product Team"
python main.py generate --topic "Security Review" --slides 7 --audience "Security Team"
python main.py generate --topic "Budget Planning" --slides 5 --audience "Finance"

echo Batch generation complete!
dir output\
```

Run with:
```bash
bash batch_generate.sh    # macOS/Linux
batch_generate.bat        # Windows
```

---

## Optimization Tips

### For Best Results:

1. **Topic Clarity**
   - ✅ "Digital Payment Systems: Security and User Experience"
   - ❌ "Payments"

2. **Audience Specificity**
   - ✅ "--audience 'Senior Product Managers'"
   - ❌ "--audience 'people'"

3. **Slide Count Selection**
   - Quick overview: 5-6 slides
   - Standard presentation: 8-10 slides
   - Comprehensive: 12-15 slides
   - Training session: 15-20 slides

4. **Tone Matching**
   - Match your actual presentation context
   - Technical tone for engineers
   - Professional for executives
   - Casual for internal teams

### Regenerating with Different Parameters

If you don't like a presentation:

```bash
# Try with different slides
python main.py generate --topic "Your Topic" --slides 8  # Changed from 6

# Try with different tone
python main.py generate --topic "Your Topic" --tone casual  # Changed from professional

# Try with audience context
python main.py generate --topic "Your Topic" --audience "Specific Group"

# Or adjust the output yourself in PowerPoint!
```

---

## Real-World Workflow Example

### Scenario: Preparing a Sales Pitch

**Step 1: Generate Initial Deck**
```bash
python main.py generate \
  --topic "SaaS Platform Solution for Enterprise" \
  --slides 10 \
  --audience "VP of Operations" \
  --tone professional \
  --output "sales_pitch_v1.pptx"
```

**Step 2: Review and Edit**
- Open `sales_pitch_v1.pptx` in PowerPoint
- Add company logo to title slide
- Insert customer testimonial slides
- Add pricing information
- Customize colors to match brand

**Step 3: Get Feedback**
- Share with sales manager
- Gather suggestions
- Refine key messages

**Step 4: Final Polish**
- Add video or demo links
- Include call-to-action buttons
- Print as PDF for distribution

---

## Troubleshooting Examples

### Topic Too Vague

**Problem:**
```bash
python main.py generate --topic "Technology"  # Too broad!
```

**Solution:**
```bash
python main.py generate --topic "How Machine Learning is Transforming Customer Service"
```

### Generated Content Doesn't Fit

**Problem:**
Text appears truncated in some slides.

**Solution:**
```bash
# Regenerate with fewer slides for more breathing room
python main.py generate --topic "Your Topic" --slides 5  # Reduced from 8
```

### Tone Doesn't Match Audience

**Problem:**
Technical presentation generated for business audience.

**Solution:**
```bash
python main.py generate \
  --topic "Your Topic" \
  --audience "Finance Department" \
  --tone professional  # Not technical
```

---

## Advanced Usage

### Integration with CI/CD

Generate presentations automatically:

```yaml
# .github/workflows/generate_reports.yml
name: Generate Reports
on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python main.py generate --topic "Daily Status" --slides 6
      - uses: actions/upload-artifact@v2
        with:
          path: output/
```

### Programmatic Usage (Future)

```python
# Direct Python import (future enhancement)
from src.orchestrator import PresentationOrchestrator

orchestrator = PresentationOrchestrator(...)
result = orchestrator.generate(
    topic="Your Topic",
    num_slides=8,
    audience="Your Audience"
)
```

---

## Summary

DocGen makes it easy to:
- ✅ Create presentations in seconds
- ✅ Generate content appropriate for audience
- ✅ Maintain brand consistency
- ✅ Focus on message, not formatting

For more details, see [README.md](README.md) and [DESIGN_OVERVIEW.md](DESIGN_OVERVIEW.md).
