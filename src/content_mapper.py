from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple

from .config import SLIDE_CONSTRAINTS
from .models import SlideOutline, SlideType

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValidationIssue:
    severity: str  # "hard" | "soft"
    code: str
    message: str


class ContentMapper:
    """
    Validator + Normalizer for LLM-generated slide content.

    Best-practice principles:
    1) Normalize deterministically to prevent rendering/layout breaks (truncate/cap).
    2) Validate explicitly. Do NOT invent content.
    3) Tell orchestrator when we need regeneration.

    This class is intentionally model-agnostic and template-agnostic.
    It can accept constraints from TemplateManager or defaults from SLIDE_CONSTRAINTS.
    """

    def __init__(self, template_constraints: Optional[Dict[str, Any]] = None):
        self.constraints: Dict[str, Any] = {}
        self.update_constraints(template_constraints or SLIDE_CONSTRAINTS)

    # ----------------------------
    # Constraint normalization
    # ----------------------------
    def update_constraints(self, incoming: Dict[str, Any]) -> None:
        merged = dict(self.constraints)
        merged.update(incoming or {})

        # Normalize bullet bounds
        if "bullets_per_slide" in merged and ("min_bullets" not in merged or "max_bullets" not in merged):
            bps = merged.get("bullets_per_slide")
            if isinstance(bps, (tuple, list)) and len(bps) == 2:
                merged["min_bullets"] = int(bps[0])
                merged["max_bullets"] = int(bps[1])
            elif isinstance(bps, int):
                merged["min_bullets"] = max(0, int(bps))
                merged["max_bullets"] = int(bps)

        # Defaults (safe for PPT layout)
        merged.setdefault("title_max_length", 80)
        merged.setdefault("subtitle_max_length", 100)
        merged.setdefault("bullet_max_length", 120)
        merged.setdefault("min_chars_per_bullet", 0)  # keep 0 unless you want strictness
        merged.setdefault("min_bullets", 3)
        merged.setdefault("max_bullets", 5)
        merged.setdefault("slides_minimum", 3)

        self.constraints = merged

    def _min_max_bullets(self) -> Tuple[int, int]:
        return int(self.constraints["min_bullets"]), int(self.constraints["max_bullets"])

    # ----------------------------
    # Public API expected by orchestrator
    # ----------------------------
    def validate_slide_outline(self, slide: SlideOutline) -> SlideOutline:
        """
        Normalize + validate slide. Returns normalized slide.
        Issues are discoverable via assess_slide() which orchestrator uses for regen decisions.
        """
        normalized, _issues, _needs_regen = self.assess_slide(slide)
        return normalized

    # Backward-compat alias (your old API)
    def validate_and_adapt_slide(self, slide: SlideOutline) -> SlideOutline:
        return self.validate_slide_outline(slide)

    def validate_presentation(self, outline) -> bool:
        slides = getattr(outline, "slides", None) or []
        return len(slides) >= int(self.constraints.get("slides_minimum", 3))

    # ----------------------------
    # Core: assess + normalize
    # ----------------------------
    def assess_slide(self, slide: SlideOutline) -> Tuple[SlideOutline, List[ValidationIssue], bool]:
        """
        Returns: (normalized_slide, issues, needs_regen)
        needs_regen=True if slide violates structural expectations in a way that should trigger LLM regen.
        """
        # Copy to avoid mutating caller state unexpectedly
        updated = slide.model_copy(deep=True)

        issues: List[ValidationIssue] = []
        needs_regen = False

        # --- Normalize text lengths deterministically ---
        updated.title = self._truncate(updated.title, int(self.constraints["title_max_length"]))
        if getattr(updated, "subtitle", None):
            updated.subtitle = self._truncate(updated.subtitle, int(self.constraints["subtitle_max_length"]))

        # --- Title presence (hard) ---
        if not updated.title or not updated.title.strip():
            issues.append(ValidationIssue("hard", "empty_title", "Slide title is empty."))
            needs_regen = True

        # --- Bullets normalization ---
        bullets = list(getattr(updated, "bullet_points", []) or [])
        bullets = [b.strip() for b in bullets if isinstance(b, str) and b.strip()]

        min_b, max_b = self._min_max_bullets()
        max_len = int(self.constraints["bullet_max_length"])

        # Cap bullet count
        if len(bullets) > max_b:
            issues.append(
                ValidationIssue(
                    "soft",
                    "too_many_bullets",
                    f"Had {len(bullets)} bullets; capped to {max_b} to prevent layout overflow.",
                )
            )
            bullets = bullets[:max_b]

        # Truncate bullets (safe normalization)
        bullets = [self._truncate(b, max_len) for b in bullets]
        updated.bullet_points = bullets

        # --- Structural expectations by slide type ---
        # Title slides may have no bullets; content slides should.
        if updated.slide_type in (SlideType.CONTENT_SLIDE, SlideType.TWO_COLUMN):
            if len(updated.bullet_points) == 0:
                issues.append(ValidationIssue("hard", "missing_bullets", "Content slide has no bullets."))
                needs_regen = True
            elif len(updated.bullet_points) < min_b:
                issues.append(
                    ValidationIssue(
                        "soft",
                        "too_few_bullets",
                        f"Content slide has {len(updated.bullet_points)} bullets; expected at least {min_b}.",
                    )
                )
                # For docgen quality, treat too-few bullets as regen-worthy (soft regen)
                needs_regen = True

        # Closing slide can be more flexible, but should usually have bullets
        if updated.slide_type == SlideType.CLOSING_SLIDE and len(updated.bullet_points) == 0:
            issues.append(ValidationIssue("soft", "closing_no_bullets", "Closing slide has no bullets."))
            # optional: regen; typically yes for quality
            needs_regen = True

        return updated, issues, needs_regen

    # ----------------------------
    # Helpers
    # ----------------------------
    def _truncate(self, text: str, max_length: int) -> str:
        if not text or not isinstance(text, str):
            return ""
        text = text.strip()
        if len(text) <= max_length:
            return text

        ellipsis = "..."
        cut = max_length - len(ellipsis)
        if cut <= 0:
            return ellipsis[:max_length]

        chunk = text[:cut]
        # Prefer word boundary near the end
        last_space = chunk.rfind(" ")
        if last_space > int(cut * 0.8):
            chunk = chunk[:last_space]
        return chunk.rstrip() + ellipsis