# DocGen – Design Overview

## 1. Objective

The objective of DocGen is to demonstrate a simple, practical solution that uses GenAI to automatically generate **branded PowerPoint presentations**.

The system focuses on safely combining:
- GenAI‑generated content
- A real corporate PowerPoint template
- Layout‑safe rendering techniques

---

## 2. Architecture Overview

```text
CLI Input
   ↓
Content Generator (LiteLLM)
   ↓
Structured Presentation Outline
   ↓
Template Content Injector
   ↓
Branded PowerPoint (.pptx)
```

The architecture clearly separates **content generation** from **presentation rendering**.

## Components

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

---

## 3. User Input Handling

Input is provided through a CLI. The required input is a presentation topic. Optional inputs include slide count, audience, and tone.

The CLI validates inputs before invoking the orchestration layer.

---

## 4. GenAI Integration

DocGen uses **LiteLLM** to interact with large language models.

Key characteristics:
- Provider‑agnostic LLM access
- Structured JSON‑style output
- Isolation of GenAI logic from rendering logic

The GenAI model generates slide‑level content rather than free‑form text.

---

## 5. Template Handling

A branded PowerPoint template is loaded as the base presentation. The system:

- Preserves master slides and themes
- Reuses existing slide layouts
- Avoids any modification of template styling

Layouts are selected based on slide type rather than layout density or shape count.

---

## 6. Content Injection & Layout Safety

The injector maps generated content strictly to PowerPoint placeholders:

- Titles → title placeholders
- Bullets → body placeholders
- Object placeholders only as fallback

Unused placeholders are cleared to avoid visual artifacts.

This guarantees layout integrity and brand consistency.

---

## 7. Output Generation

The output is a fully editable `.pptx` file suitable for immediate use in PowerPoint.

---

## 8. Scope & Limitations

This POC intentionally limits scope to:
- One branded template
- Text‑only content
- CLI‑based usage

---

## 9. Summary

DocGen demonstrates a robust and evaluation‑ready approach to GenAI‑powered document generation by combining structured content generation with template‑aware rendering.
