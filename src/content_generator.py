from __future__ import annotations

import json
import logging
import os
import random
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple

from litellm import completion

from .models import PresentationOutline, SlideOutline, SlideType
from .config import OPENAI_API_KEY, API_KEY, MODEL, MAX_RETRIES, TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


# -----------------------------
# Model candidate representation
# -----------------------------
@dataclass
class ModelCandidate:
    model: str
    provider: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None


class ContentGenerator:
    """
    Robust outline generator using LiteLLM + multi-provider fallbacks + improved fallback outline.

    Key robustness features:
    - Normalizes LLM output (slide count, bullet lengths, bullet count caps) before validation.
    - Validation is pragmatic: strict enough to avoid broken slides, not so strict it forces fallback.
    - Keeps "best effort" LLM outline if close enough
    - Supports multi-provider chain:
        Groq -> Gemini (if key) -> OpenAI (if key) -> Ollama local (no key, but requires local server)
    """

    # Hard bounds used to keep PPT layout safe
    TITLE_MAX = 80
    SUBTITLE_MAX = 100
    BULLET_MAX = 120

    # Default bullet bounds
    CONTENT_MIN_BULLETS = 3
    CONTENT_MAX_BULLETS = 10
    CLOSING_MIN_BULLETS = 3
    CLOSING_MAX_BULLETS = 7 

    # Strings sometimes returned by LLM that we treat as "filler"
    BAD_BULLET_MARKERS = (
        "lorem ipsum",
        "click to edit",
        "text here",
    )

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.max_retries = max(1, int(MAX_RETRIES))
        self.timeout = int(TIMEOUT_SECONDS)

        # Keys (may be absent)
        self.groq_key = os.getenv("GROQ_API_KEY") or API_KEY
        self.openai_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

        # Default model (from config/env)
        self.model = self._normalize_model_name(model or MODEL or "")

        # Allows forcing fallback for testing
        self.force_fallback = os.getenv("DOCGEN_FORCE_FALLBACK", "0") == "1"

        # Fallback determinism control
        self.deterministic_fallback = os.getenv("DOCGEN_DETERMINISTIC_FALLBACK", "0") == "1"

        # Ollama base (no key; requires local server)
        self.ollama_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

        logger.info(
            f"[ContentGenerator] model={self.model} "
            f"groq_key={'set' if bool(self.groq_key) else 'missing'} "
            f"gemini_key={'set' if bool(self.gemini_key) else 'missing'} "
            f"openai_key={'set' if bool(self.openai_key) else 'missing'} "
            f"ollama_base={self.ollama_base}"
        )

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def generate_presentation_outline(
        self,
        topic: str,
        num_slides: int,
        audience: Optional[str] = None,
        tone: str = "professional",
        template_constraints: Optional[Dict[str, Any]] = None,
    ) -> PresentationOutline:
        topic = (topic or "").strip()
        if not topic:
            return self._fallback_outline("Untitled Topic", int(num_slides or 5), audience, tone)

        num_slides = int(num_slides)
        num_slides = max(3, min(num_slides, 20))

        if self.force_fallback:
            logger.warning("[FALLBACK_OUTLINE] Forced fallback via DOCGEN_FORCE_FALLBACK=1")
            return self._fallback_outline(topic, num_slides, audience, tone)

        # Build prompts
        system_prompt = self._build_system_prompt(tone, template_constraints, num_slides=num_slides)
        user_prompt = self._build_user_prompt(topic, num_slides, audience)

        best_outline: Optional[PresentationOutline] = None
        best_issue_count = 10**9
        feedback: Optional[str] = None
        last_error: Optional[str] = None

        # Attempt loop
        for attempt in range(1, self.max_retries + 1):
            try:
                raw = self._call_api(system_prompt, user_prompt, feedback=feedback)
                data = self._safe_parse_json(raw)

                outline = self._parse_outline_response(data, expected_slides=num_slides)
                outline = self._normalize_outline(outline, expected_slides=num_slides)

                ok, issues = self._validate_outline(outline, expected_slides=num_slides)

                if ok:
                    logger.info(f"[LLM_OUTLINE] Success on attempt {attempt}/{self.max_retries}")
                    return outline

                # Track best effort
                if len(issues) < best_issue_count:
                    best_issue_count = len(issues)
                    best_outline = outline

                logger.warning(
                    f"[LLM_OUTLINE] Validation failed attempt {attempt}/{self.max_retries}. "
                    f"Issues={len(issues)} -> {issues}"
                )

                # If we're close enough, keep it (don't force deterministic fallback)
                # Threshold is pragmatic: 1 issue means usually minor (e.g. bullet count)
                if attempt == self.max_retries and best_outline is not None and best_issue_count <= 1:
                    logger.warning(
                        f"[LLM_OUTLINE] Returning best-effort outline (issues={best_issue_count}) "
                        "instead of deterministic fallback."
                    )
                    return best_outline

                feedback = self._format_feedback(issues, expected_slides=num_slides)
                last_error = "validation_failed"

                # Escalate model if using small Groq model and repeated failures
                if attempt >= 2 and self.model.endswith("llama-3.1-8b-instant"):
                    # switch to higher quality Groq model if available
                    if self.groq_key:
                        logger.warning("[LLM_OUTLINE] Escalating model to groq/llama-3.3-70b-versatile")
                        self.model = "groq/llama-3.3-70b-versatile"

            except Exception as e:
                last_error = str(e)
                logger.exception(f"[LLM_OUTLINE] Attempt {attempt}/{self.max_retries} failed: {e}")
                feedback = (
                    "Your previous output was invalid or unparsable. "
                    "Return ONLY valid JSON matching the schema and constraints."
                )

        # If we have any best outline, return it; else fallback
        if best_outline is not None:
            logger.warning(
                f"[LLM_OUTLINE] LLM failed after retries; returning best outline (issues={best_issue_count}). "
                f"Last error: {last_error}"
            )
            return best_outline

        logger.warning(
            "[FALLBACK_OUTLINE] LLM outline generation failed after retries and no usable outline was produced. "
            f"Last error: {last_error}"
        )
        return self._fallback_outline(topic, num_slides, audience, tone)

    # ---------------------------------------------------------------------
    # Provider/model selection
    # ---------------------------------------------------------------------
    def _normalize_model_name(self, model: str) -> str:
        model = (model or "").strip()
        if not model:
            # default to a safe Groq model if key exists, else local Ollama (if running)
            if self.groq_key:
                return "groq/llama-3.3-70b-versatile"
            return "ollama/llama3"

        # Map deprecated Groq IDs -> supported
        deprecated_map = {
            "llama3-70b-8192": "groq/llama-3.3-70b-versatile",
            "llama3-8b-8192": "groq/llama-3.1-8b-instant",
            "groq/llama3-70b-8192": "groq/llama-3.3-70b-versatile",
            "groq/llama3-8b-8192": "groq/llama-3.1-8b-instant",
        }
        if model in deprecated_map:
            return deprecated_map[model]

        # If user passes Groq model without prefix, assume groq/
        if "/" not in model and model.startswith("llama"):
            return f"groq/{model}"

        return model

    def _candidate_models(self) -> List[ModelCandidate]:
        """
        Ordered candidates. We only include providers that have required keys available.
        Note: Gemini/OpenAI require API keys. Ollama does not require a cloud API key
        but requires a local Ollama server running.
        """
        candidates: List[ModelCandidate] = []

        # Groq candidates (supported production models) 
        if self.groq_key:
            candidates.extend([
                ModelCandidate("groq/llama-3.3-70b-versatile", provider="groq", api_key=self.groq_key),
                ModelCandidate("groq/llama-3.1-8b-instant", provider="groq", api_key=self.groq_key),
            ])

        # Gemini candidates require GEMINI_API_KEY 
        if self.gemini_key:
            candidates.extend([
                ModelCandidate("gemini/gemini-2.0-flash-lite", provider="gemini", api_key=self.gemini_key),
                ModelCandidate("gemini/gemini-pro", provider="gemini", api_key=self.gemini_key),
            ])

        # OpenAI candidates require OPENAI_API_KEY
        if self.openai_key:
            candidates.extend([
                ModelCandidate("openai/gpt-4o-mini", provider="openai", api_key=self.openai_key),
                ModelCandidate("openai/gpt-4.1-mini", provider="openai", api_key=self.openai_key),
            ])

        # Local Ollama (no cloud API key required) but must have Ollama server running
            # ModelCandidate("ollama/llama3", provider="ollama", api_key=None, api_base=self.ollama_base),
            # ModelCandidate("ollama/mistral", provider="ollama", api_key=None, api_base=self.ollama_base)

        return candidates

    # ---------------------------------------------------------------------
    # API call with fallback across models/providers
    # ---------------------------------------------------------------------
    def _call_api(self, system_prompt: str, user_prompt: str, *, feedback: Optional[str] = None) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        if feedback:
            messages.append({"role": "user", "content": f"REGENERATION FEEDBACK:\n{feedback}\nReturn ONLY valid JSON."})

        # Try current model first, then candidates
        candidates = [ModelCandidate(self.model, provider=self.model.split("/", 1)[0] if "/" in self.model else "unknown")] + [
            c for c in self._candidate_models() if c.model != self.model
        ]

        last_err: Optional[Exception] = None

        for cand in candidates:
            try:
                logger.info(f"[LLM_CALL] Trying model={cand.model} provider={cand.provider}")

                resp = completion(
                    model=cand.model,
                    messages=messages,
                    api_key=cand.api_key,
                    api_base=cand.api_base,
                    temperature=0.6 if feedback else 0.7,
                    max_tokens=3500,
                    timeout=self.timeout,
                )

                # lock onto working model
                if cand.model != self.model:
                    logger.warning(f"[LLM_CALL] Switching model from {self.model} -> {cand.model}")
                    self.model = cand.model

                return resp.choices[0].message.content

            except Exception as e:
                last_err = e
                err = str(e).lower()

                # Model decommissioned or invalid -> try next model
                if "model_decommissioned" in err or "decommissioned" in err or "invalid_request_error" in err:
                    logger.warning(f"[LLM_CALL] Model rejected ({cand.model}). Trying next candidate...")
                    continue

                # Rate limiting / overload -> raise so outer retry can handle (same model)
                if "429" in err or "rate limit" in err or "overloaded" in err or "503" in err:
                    raise

                # Ollama not running -> try next candidate
                if cand.provider == "ollama" and ("connection refused" in err or "failed to connect" in err):
                    logger.warning("[LLM_CALL] Ollama not reachable on api_base. Skipping local candidate...")
                    continue

                # For all other errors, raise
                raise

        # Exhausted candidates
        if last_err:
            raise last_err
        raise RuntimeError("LLM call failed with unknown error")

    # ---------------------------------------------------------------------
    # Prompting
    # ---------------------------------------------------------------------
    def _build_system_prompt(self, tone: str, constraints: Optional[Dict[str, Any]] = None, *, num_slides: int) -> str:
        tone = (tone or "professional").strip()

        # pull constraints if available
        title_max = int((constraints or {}).get("title_max_length", self.TITLE_MAX))
        subtitle_max = int((constraints or {}).get("subtitle_max_length", self.SUBTITLE_MAX))
        bullet_max = int((constraints or {}).get("bullet_max_length", self.BULLET_MAX))

        prompt = f"""
                You are an expert executive presentation strategist.

                OUTPUT CONTRACT (STRICT):
                - Return ONLY valid JSON. No markdown, no code fences, no prose.
                - slide_type MUST be one of: "title_slide", "content_slide", "two_column", "closing_slide"
                - Produce exactly {num_slides} slides.

                HARD CONSTRAINTS:
                - Title <= {title_max} chars
                - Subtitle <= {subtitle_max} chars (only when used)
                - Each bullet <= {bullet_max} chars
                - Content slides: 3–10 bullets
                - Closing slide: 3–7 bullets
                - Slide titles must be unique across the deck
                - Avoid repeating the same bullet text across slides

                QUALITY RULES:
                - MECE: each content slide covers a distinct angle (no overlap)
                - Concrete language, minimal fluff
                - Use placeholders for metrics: "XX%", "$X", "N weeks"

                JSON SCHEMA:
                {{
                "title": "Deck title",
                "topic": "Original topic",
                "target_audience": "Audience",
                "key_message": "One-sentence takeaway",
                "slides": [
                    {{
                    "slide_number": 1,
                    "slide_type": "title_slide",
                    "title": "...",
                    "subtitle": "...",
                    "speaker_notes": "Optional"
                    }},
                    {{
                    "slide_number": 2,
                    "slide_type": "content_slide",
                    "title": "...",
                    "bullet_points": ["...", "...", "..."],
                    "speaker_notes": "Optional"
                    }},
                    {{
                    "slide_number": {num_slides},
                    "slide_type": "closing_slide",
                    "title": "...",
                    "subtitle": "...",
                    "bullet_points": ["...", "...", "..."],
                    "speaker_notes": "Optional"
                    }}
                ]
                }}

                TONE: {tone}""".strip()
        return prompt

    def _build_user_prompt(self, topic: str, num_slides: int, audience: Optional[str] = None) -> str:
        target_audience = audience or "General Executive Stakeholders"
        return f"""
                Create a {num_slides}-slide executive presentation outline for: "{topic}"
                Target Audience: {target_audience}

                Structure:
                1) Slide 1: title_slide with a strong 'Why now?' subtitle
                2) Slides 2..{num_slides-1}: content_slide or two_column (distinct angles, MECE)
                3) Slide {num_slides}: closing_slide with decisions + next steps (actionable)

                Return JSON only. No commentary.
                """.strip()

    # ---------------------------------------------------------------------
    # Parsing helpers
    # ---------------------------------------------------------------------
    def _safe_parse_json(self, raw: str) -> Dict[str, Any]:
        if raw is None:
            raise ValueError("Empty LLM response")

        text = raw.strip()

        # remove ``` fences
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

        # try direct
        try:
            return json.loads(text)
        except Exception:
            pass

        # extract biggest JSON object
        objs = []
        for m in re.finditer(r"\{", text):
            start = m.start()
            depth = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i + 1]
                        try:
                            objs.append(json.loads(candidate))
                        except Exception:
                            pass
                        break

        if not objs:
            raise ValueError("Could not parse or extract JSON from response")
        return max(objs, key=lambda o: len(json.dumps(o)))

    # ---------------------------------------------------------------------
    # JSON -> Models
    # ---------------------------------------------------------------------
    def _parse_outline_response(self, data: Dict[str, Any], *, expected_slides: int) -> PresentationOutline:
        slides_data = data.get("slides", []) or []
        if not isinstance(slides_data, list) or not slides_data:
            raise ValueError("JSON missing 'slides' list")

        slides: List[SlideOutline] = []

        for idx, sd in enumerate(slides_data, start=1):
            if not isinstance(sd, dict):
                continue

            raw_type = sd.get("slide_type", "content_slide")
            try:
                slide_type = SlideType(raw_type)
            except Exception:
                slide_type = SlideType.CONTENT_SLIDE

            # enforce title first and closing last
            if idx == 1:
                slide_type = SlideType.TITLE_SLIDE
            elif idx == len(slides_data):
                slide_type = SlideType.CLOSING_SLIDE

            slides.append(
                SlideOutline(
                    slide_number=idx,
                    slide_type=slide_type,
                    title=(sd.get("title") or f"Slide {idx}"),
                    subtitle=sd.get("subtitle"),
                    bullet_points=sd.get("bullet_points", []) or [],
                    speaker_notes=sd.get("speaker_notes"),
                )
            )

        outline = PresentationOutline(
            title=data.get("title") or data.get("topic") or topic_title_fallback(data),
            topic=data.get("topic") or "General Topic",
            target_audience=data.get("target_audience"),
            key_message=data.get("key_message"),
            slides=slides,
        )
        return outline


    # ---------------------------------------------------------------------
    # Normalization (pragmatic)
    # ---------------------------------------------------------------------
    def _normalize_outline(self, outline: PresentationOutline, *, expected_slides: int) -> PresentationOutline:
        slides = list(outline.slides or [])

        # truncate extra slides (common model behavior)
        if len(slides) > expected_slides:
            slides = slides[:expected_slides]

        # enforce first/last slide type when possible
        if slides:
            slides[0].slide_type = SlideType.TITLE_SLIDE
            if len(slides) > 1:
                slides[-1].slide_type = SlideType.CLOSING_SLIDE

        # clean text + cap bullets + truncate long bullets
        for s in slides:
            s.title = (s.title or "").strip()[: self.TITLE_MAX]
            if s.subtitle:
                s.subtitle = str(s.subtitle).strip()[: self.SUBTITLE_MAX]

            bullets = [b for b in (s.bullet_points or []) if isinstance(b, str)]
            bullets = [b.strip() for b in bullets if b.strip()]
            bullets = [b for b in bullets if not self._is_bad_bullet(b)]

            # cap bullet count (don't invent bullets)
            if s.slide_type == SlideType.CLOSING_SLIDE:
                bullets = bullets[: self.CLOSING_MAX_BULLETS]
            elif s.slide_type in (SlideType.CONTENT_SLIDE, SlideType.TWO_COLUMN):
                bullets = bullets[: self.CONTENT_MAX_BULLETS]
            else:
                bullets = []  # title slide

            bullets = [self._truncate(b, self.BULLET_MAX) for b in bullets]
            s.bullet_points = bullets

        outline.slides = slides
        outline.total_slides = len(slides)
        return outline

    def _is_bad_bullet(self, bullet: str) -> bool:
        t = bullet.lower()
        return any(x in t for x in self.BAD_BULLET_MARKERS)

    def _truncate(self, text: str, max_len: int) -> str:
        text = (text or "").strip()
        if len(text) <= max_len:
            return text
        return text[: max_len - 3].rstrip() + "..."

    # ---------------------------------------------------------------------
    # Validation (pragmatic)
    # ---------------------------------------------------------------------
    def _validate_outline(self, outline: PresentationOutline, *, expected_slides: int) -> Tuple[bool, List[str]]:
        issues: List[str] = []
        slides = outline.slides or []

        if len(slides) != expected_slides:
            issues.append(f"Expected {expected_slides} slides, got {len(slides)}.")

        # Unique titles
        titles = [s.title.strip().lower() for s in slides if s.title]
        if len(set(titles)) != len(titles):
            issues.append("Slide titles are not unique.")

        # Bullet rules by slide type
        for s in slides:
            bullets = [b for b in (s.bullet_points or []) if isinstance(b, str) and b.strip()]

            if s.slide_type in (SlideType.CONTENT_SLIDE, SlideType.TWO_COLUMN):
                if len(bullets) < self.CONTENT_MIN_BULLETS:
                    issues.append(f"Slide {s.slide_number} has too few bullets ({len(bullets)}).")
                if len(bullets) > self.CONTENT_MAX_BULLETS:
                    issues.append(f"Slide {s.slide_number} has too many bullets ({len(bullets)}).")

            elif s.slide_type == SlideType.CLOSING_SLIDE:
                if len(bullets) < self.CLOSING_MIN_BULLETS:
                    issues.append(f"Closing slide has too few bullets ({len(bullets)}).")
                if len(bullets) > self.CLOSING_MAX_BULLETS:
                    issues.append(f"Closing slide has too many bullets ({len(bullets)}).")

            else:
                # title slide should have no bullets
                if len(bullets) > 0:
                    issues.append("Title slide should not have bullet_points.")

            for b in bullets:
                if len(b) > self.BULLET_MAX:
                    issues.append(f"Slide {s.slide_number} has bullet >{self.BULLET_MAX} chars.")

        # Duplicate bullets across deck (relaxed)
        all_bullets = []
        for s in slides:
            for b in (s.bullet_points or []):
                if isinstance(b, str):
                    all_bullets.append(b.strip().lower())
        dup_count = len(all_bullets) - len(set(all_bullets))
        if dup_count >= 3:
            issues.append(f"Too many repeated bullets across slides (duplicates={dup_count}).")

        return (len(issues) == 0), issues

    def _format_feedback(self, issues: List[str], *, expected_slides: int) -> str:
        lines = [
            f"- MUST: output exactly {expected_slides} slides",
            "- MUST: slide_type only from {title_slide, content_slide, two_column, closing_slide}",
            "- MUST: content slides have 3–10 bullets; closing slide 3–7; bullets <=120 chars",
            "- MUST: slide titles unique and meaningful",
        ]
        for i in issues:
            lines.append(f"- FIX: {i}")
        return "\n".join(lines)

    # ---------------------------------------------------------------------
    # Improved fallback (generic + non-deterministic by default)
    # ---------------------------------------------------------------------
    def _fallback_outline(
        self,
        topic: str,
        num_slides: int,
        audience: Optional[str],
        tone: str,
    ) -> PresentationOutline:
        logger.warning(
            "[FALLBACK_OUTLINE] Using generic fallback outline. "
            "LLM outline generation failed or was unavailable."
        )

        # Make fallback less deterministic by default:
        # - deterministic if DOCGEN_DETERMINISTIC_FALLBACK=1
        # - otherwise varies per run
        if self.deterministic_fallback:
            seed = abs(hash((topic, audience, tone, num_slides))) % (2**32)
        else:
            seed = int(time.time() * 1000) ^ random.getrandbits(32)

        rng = random.Random(seed)

        # Diverse content angles
        angles = [
            "Signals & Trends",
            "Opportunities",
            "Risks & Guardrails",
            "Workforce & Skills",
            "Operating Model",
            "Technology Enablers",
            "Adoption Roadmap",
            "Ethics & Trust",
        ]
        rng.shuffle(angles)

        # Vary closing slide intent
        closing_titles = [
            "Decisions & Next Steps",
            "Key Takeaways",
            "What to Do Next",
            "Risks to Monitor",
            "Action Plan",
        ]
        closing_subs = [
            "Questions / Discussion",
            "Align on priorities and owners",
            "Move from insight to action",
            "Agree guardrails and metrics",
            "Pick pilots and scale paths",
        ]

        def bullets_for(angle: str) -> List[str]:
            templates = [
                f"Define what changes in {angle.lower()} and why it matters for {topic}.",
                f"Identify 2–3 constraints (cost, adoption, regulation) shaping outcomes in {topic}.",
                f"Propose one concrete experiment to validate impact in {topic} within 2–4 weeks.",
                f"Name the key stakeholder group impacted and what they need to do differently.",
                f"List one risk and one mitigation to keep outcomes safe and predictable.",
            ]
            rng.shuffle(templates)
            return templates[: rng.randint(self.CONTENT_MIN_BULLETS, self.CONTENT_MAX_BULLETS)]

        slides: List[SlideOutline] = []

        # Slide 1
        slides.append(
            SlideOutline(
                slide_number=1,
                slide_type=SlideType.TITLE_SLIDE,
                title=topic[: self.TITLE_MAX],
                subtitle=(f"For {audience}" if audience else "Overview"),
                bullet_points=[],
                speaker_notes=None,
            )
        )

        # Middle slides
        middle_count = max(num_slides - 2, 1)
        for i in range(2, 2 + middle_count):
            angle = angles[(i - 2) % len(angles)]
            slides.append(
                SlideOutline(
                    slide_number=i,
                    slide_type=SlideType.CONTENT_SLIDE,
                    title=f"{angle}: {topic[:45]}",
                    subtitle=None,
                    bullet_points=bullets_for(angle),
                    speaker_notes=None,
                )
            )

        # Closing
        slides.append(
            SlideOutline(
                slide_number=num_slides,
                slide_type=SlideType.CLOSING_SLIDE,
                title=rng.choice(closing_titles),
                subtitle=rng.choice(closing_subs),
                bullet_points=[
                    f"Decide: pick 1–2 priorities that change outcomes for {topic}.",
                    "Assign owners: clarify decision rights, funding, and delivery accountability.",
                    "Pilot: run a 2–4 week test with measurable success criteria (XX%).",
                    "Scale: roll out what works and retire what doesn’t based on evidence.",
                ][: rng.randint(self.CLOSING_MIN_BULLETS, self.CLOSING_MAX_BULLETS)],
                speaker_notes=None,
            )
        )

        return PresentationOutline(
            title=topic,
            topic=topic,
            target_audience=audience,
            key_message=f"A {tone} overview of {topic}.",
            slides=slides,
        )


def topic_title_fallback(data: Dict[str, Any]) -> str:
    # small helper used above
    t = (data.get("topic") or data.get("title") or "Presentation").strip()
    return t[:80]