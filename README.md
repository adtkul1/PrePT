# DocGen – GenAI‑Powered Branded Presentation Generator

DocGen is a proof‑of‑concept system that automatically generates **branded PowerPoint presentations** using GenAI.

A user provides a topic (and optional parameters), DocGen generates structured slide content using an LLM, and safely injects that content into a **provided branded PPTX template** without breaking layouts, colors, or styles.

This repository is intentionally scoped and structured to align with the **DocGen Challenge** evaluation criteria.

---

## What This Demonstrates

- ✅ End‑to‑end GenAI‑driven document generation
- ✅ Practical use of a real branded PowerPoint template
- ✅ Layout‑safe, placeholder‑based content injection
- ✅ Clear separation of concerns (generation vs rendering)
- ✅ A working proof of concept runnable from the CLI

---

## End‑to‑End Workflow

```text
User Input (CLI)
      ↓
GenAI Content Generation (OpenAI/ variety of models from LiteLLM/local)
      ↓
Structured Slide Outline (titles, bullets, slide types)
      ↓
Template‑Aware Content Injection
      ↓
Branded PowerPoint (.pptx)
```

---

## User Input

The system accepts input via a **command‑line interface (CLI)**.

### Required Input

- **Topic** – The subject of the presentation

### Optional Inputs

- **Number of slides** – Controls presentation length
- **Audience** – Used to adjust tone and terminology
- **Tone** – e.g. professional, technical, executive

Example:

```bash
python main.py generate   --topic "The Value of GenAI in Enterprise"   --slides 6   --audience "Executive Leadership"   --tone professional
```

---

## GenAI Content Generation

DocGen uses **LiteLLM** as an abstraction layer for LLM calls. This allows the system to:

- Remain provider‑agnostic (OpenAI, Azure OpenAI, etc.)
- Keep GenAI usage isolated from the rest of the pipeline
- Easily swap or extend models in the future

The model generates **structured output**, including:

- Slide titles
- Bullet points per slide
- Slide types (title, content, closing)

This structure is validated and converted into Python models before rendering.

---

## Branded Template Application

A provided branded PowerPoint template (`accenture_template.pptx`) is used as the base presentation.

### Key Design Principles

- ✅ Master slides are **never modified**
- ✅ No shapes or backgrounds are drawn programmatically
- ✅ All content is injected into **existing placeholders**

### Layout Selection

Layouts are selected based on **slide type** (title, content, closing), not by heuristic shape counts.

Layouts that resemble one‑pagers or grid‑heavy designs are intentionally avoided to preserve visual clarity.

---

## Layout Safety & Content Injection

Content injection follows a **placeholder‑first strategy**:

- Titles → TITLE or CENTER_TITLE placeholders
- Bullet points → BODY placeholders
- OBJECT placeholders are used only when BODY placeholders are unavailable
- Unused placeholders are cleared to avoid empty boxes

This ensures:

- No overlap with template visuals
- No layout breakage
- Full preservation of brand styling

---

## Output

The final output is a **standard PowerPoint (.pptx) file** that:

- Opens directly in Microsoft PowerPoint
- Is fully editable
- Preserves colors, fonts, spacing, and layouts from the branded template

Generated files are written to the `output/` directory.

---

## Project Structure

```text
.
├── main.py
├── README.md
├── DESIGN_OVERVIEW.md
├── requirements.txt
├── .env.example
├── src/
│   ├── cli.py
│   ├── orchestrator.py
│   ├── content_generator.py
│   ├── branded_template.py
│   ├── models.py
│   └── config.py
├── templates/
│   └── accenture_template.pptx
└── output/
```

---

## Limitations (POC Scope)

- Single branded template
- Text‑only slides (no charts or images generated)
- CLI interface only

These constraints keep the proof of concept focused and easy to evaluate.

---

## Summary

DocGen demonstrates how GenAI can be combined with **real corporate PowerPoint templates** to generate professional presentations automatically while respecting brand and layout constraints.

For architectural details, see **DESIGN_OVERVIEW.md**.
