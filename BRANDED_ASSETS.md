# Branded Assets Integration Guide

## Overview

DocGen now integrates with your branded Accenture template and SharePoint brand images. This guide explains how the integration works and how to manage branded assets.

## What's Integrated

### ✅ Branded Template
- **Location:** `templates/accenture_template.pptx`
- **Source:** `C:\Users\aditi.e.kulkarni\OneDrive - Accenture\Downloads\TEMPLATE 2026.pptx`
- **Status:** Loaded and ready to use
- **Usage:** Automatically detected and applied when generating presentations

### 🖼️ Brand Images from SharePoint
- **Location:** https://ts.accenture.com/sites/BrandSpace/Collectives/Forms/AllItems.aspx
- **Type:** Brand assets, logos, images
- **Integration:** Supported via local caching

## How It Works

### Generation Pipeline with Branded Template

```
User Topic
    ↓
GenAI Content Generation
    ↓
Content Validation & Mapping
    ↓
Branded Template Loading ← accenture_template.pptx
    ↓
Content Injection into Template
    ↓
Master Slide Preservation
    ↓
Brand Image Integration ← SharePoint Images
    ↓
Final PPTX Output
```

### Key Components

1. **BrandedTemplateHandler** (`src/branded_template.py`)
   - Analyzes template structure
   - Extracts slide layouts
   - Identifies placeholders for content injection
   - Preserves master slides and theme

2. **TemplateContentInjector**
   - Injects GenAI content into template placeholders
   - Maintains template formatting and styling
   - Applies images from brand library

3. **ImageDownloader**
   - Handles SharePoint image access
   - Local caching to avoid repeated downloads
   - Fallback guidance for manual downloads

## Using Brand Images

### Option 1: Automatic (Requires SharePoint Access)

The system attempts to automatically download images from SharePoint:

```python
from src.branded_template import ImageDownloader

downloader = ImageDownloader()
image_path = downloader.get_sharepoint_image(
    sharepoint_url="https://ts.accenture.com/sites/BrandSpace/Collectives/Images",
    image_name="logo.png",
    local_cache_dir=Path("templates/brand_images")
)
```

### Option 2: Manual Download (Recommended)

For reliable access, download images manually:

1. Visit SharePoint: https://ts.accenture.com/sites/BrandSpace/Collectives/
2. Download required brand images
3. Place in: `templates/brand_images/`
4. Reference in content generation

```bash
# Create brand images directory
mkdir -p templates/brand_images

# Place downloaded images here
# - logo.png
# - header_image.png
# - accent_graphics.png
```

### Option 3: CLI Integration

Future enhancement to specify images during generation:

```bash
python main.py generate \
  --topic "Your Topic" \
  --brand-images "path/to/images" \
  --use-branded-template
```

## Branded Template Features

### Analyzing Your Template

The system automatically:
- ✅ Detects slide layouts in your template
- ✅ Identifies content placeholders
- ✅ Preserves master slides
- ✅ Maintains color scheme and fonts
- ✅ Extracts theme information

### Available Layouts

View available layouts in your template:

```python
from src.branded_template import BrandedTemplateHandler
from pathlib import Path

handler = BrandedTemplateHandler(
    Path("templates/accenture_template.pptx")
)

layouts = handler.list_layouts()
for layout in layouts:
    print(f"Layout {layout['index']}: {layout['name']} "
          f"({layout['shapes']} shapes)")
```

### Content Injection Process

When generating presentations:

1. **Template Loading**
   - Loads accenture_template.pptx as base
   - Clears example slides
   - Preserves master slides

2. **Slide Creation**
   - Uses template layouts for new slides
   - Identifies title and body placeholders
   - Injects GenAI-generated content

3. **Content Application**
   - Titles → Title placeholders
   - Bullets → Body/content placeholders
   - Images → Image placeholders (when available)

4. **Styling Preservation**
   - Master slide formatting applied
   - Theme colors and fonts respected
   - Layout consistency maintained

## Integration with GenAI Content

### Content Generation for Templates

GenAI content is generated with template constraints in mind:

```yaml
# Template Constraints (from branded template analysis)
title_max_length: 80
subtitle_max_length: 100
bullet_max_length: 120
bullets_per_slide: 5

# These are passed to GenAI for constraint-aware generation
```

### Placeholder Matching

The injector matches content to template placeholders:

```
Template Placeholder → Content Type → GenAI Output
Title (type 1)      → Slide Title  → Generated Title
Body (type 2)       → Bullets      → Generated Bullets
Image (type 14)     → Logo/Image   → Brand Image or Generated
```

## Managing Brand Assets

### Directory Structure

```
docgen/
├── templates/
│   ├── accenture_template.pptx     ← Your branded template
│   ├── brand_images/               ← Brand assets (local cache)
│   │   ├── logo.png
│   │   ├── logo_white.png
│   │   ├── header_image.png
│   │   └── accent_graphics/
│   │
│   └── corporate/
│       └── config.yaml             ← Fallback config
```

### Adding More Brand Images

1. **Download from SharePoint**
   ```
   SharePoint URL: https://ts.accenture.com/sites/BrandSpace/Collectives/
   ```

2. **Save to local directory**
   ```
   templates/brand_images/
   ```

3. **Reference in generation**
   - Images are automatically detected
   - Used where placeholders exist

## Troubleshooting

### Template Not Loading

```
Error: Template not found: accenture_template.pptx
```

**Solution:**
1. Verify file location: `templates/accenture_template.pptx`
2. Copy template:
   ```bash
   copy "C:\Users\aditi.e.kulkarni\OneDrive - Accenture\Downloads\TEMPLATE 2026.pptx" \
        "docgen\templates\accenture_template.pptx"
   ```

### SharePoint Image Access Failed

```
Warning: Could not download image from SharePoint
```

**Solution:**
1. Download images manually from SharePoint
2. Save to `templates/brand_images/`
3. Restart generation (images will be found locally)

### Content Not Fitting in Placeholders

**Solution:**
1. Adjust template constraints
2. Reduce slide count for more space
3. Shorter topics for less content

## Advanced Usage

### Custom Template Constraints

Analyze your template and set constraints:

```python
from src.branded_template import BrandedTemplateHandler

handler = BrandedTemplateHandler(
    Path("templates/accenture_template.pptx")
)

# Get template dimensions
print(f"Slide size: {handler.slide_width} x {handler.slide_height}")

# List all layouts
layouts = handler.list_layouts()
print(f"Available layouts: {len(layouts)}")
```

### Programmatic Content Injection

Inject content directly into template:

```python
from src.branded_template import TemplateContentInjector, BrandedTemplateHandler
from pathlib import Path

# Load template handler
handler = BrandedTemplateHandler(
    Path("templates/accenture_template.pptx")
)

# Create presentation from template
prs = handler.create_presentation_from_template()

# Inject content
injector = TemplateContentInjector(handler)
prs = injector.inject_content(prs, outline.slides, image_paths)

# Save
prs.save("output/custom_presentation.pptx")
```

## Image Organization in SharePoint

### Recommended Structure

```
BrandSpace/Collectives/Images/
├── Logos/
│   ├── accenture_logo_full.png
│   ├── accenture_logo_mark.png
│   └── accenture_logo_white.png
├── Headers/
│   ├── header_blue.png
│   └── header_gradient.png
├── Accents/
│   └── accent_shapes.png
└── Icons/
    ├── icon_cloud.png
    ├── icon_digital.png
    └── icon_innovation.png
```

### Using in Generation

Specify which images to use:

```python
image_paths = {
    1: Path("templates/brand_images/header_blue.png"),  # Slide 1 header
    2: Path("templates/brand_images/accenture_logo_full.png"),  # Slide 2 logo
}

prs = injector.inject_content(prs, outline.slides, image_paths)
```

## Integration Checklist

- [x] Branded template copied to `templates/accenture_template.pptx`
- [ ] Brand images downloaded from SharePoint to `templates/brand_images/`
- [ ] Test generation with branded template
- [ ] Verify layouts and placeholders
- [ ] Confirm images display correctly
- [ ] Adjust template constraints if needed

## Next Steps

1. **Download Brand Images**
   - Visit SharePoint link above
   - Save images to `templates/brand_images/`

2. **Test Generation**
   ```bash
   python main.py generate --topic "Test Presentation with Branded Template"
   ```

3. **Verify Output**
   - Open generated PPTX
   - Check template formatting
   - Verify images appear correctly

4. **Fine-tune**
   - Adjust template constraints if needed
   - Customize placeholder matching
   - Add more brand images as needed

## References

- **Branded Template:** `templates/accenture_template.pptx`
- **Brand Images URL:** https://ts.accenture.com/sites/BrandSpace/Collectives/
- **Implementation:** `src/branded_template.py`
- **Integration:** `src/orchestrator.py` and `src/cli.py`

---

**For questions about brand asset usage, contact your brand team or refer to the BrandSpace portal.**
