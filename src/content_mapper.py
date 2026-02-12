from __future__ import annotations

import logging
from typing import Dict, Any, Optional, List

from config import SLIDE_CONSTRAINTS
from models import SlideOutline  # models.py

logger = logging.getLogger(__name__)


class ContentMapper:
    """Maps GenAI content to template requirements"""

    def __init__(self, template_constraints: Optional[Dict[str, Any]] = None):
        # Tests call ContentMapper() with no args
        self.constraints: Dict[str, Any] = template_constraints or SLIDE_CONSTRAINTS

    def _max_bullets(self) -> int:
        bps = self.constraints.get("bullets_per_slide", (3, 5))
        if isinstance(bps, (tuple, list)) and len(bps) == 2:
            return int(bps[1])
        return int(bps)

    def _min_bullets(self) -> int:
        bps = self.constraints.get("bullets_per_slide", (3, 5))
        if isinstance(bps, (tuple, list)) and len(bps) == 2:
            return int(bps[0])
        return 3

    def validate_and_adapt_slide(self, slide: SlideOutline) -> SlideOutline:
        """Validate slide content and adapt to constraints."""

        # Title
        slide.title = self._validate_text(
            slide.title,
            max_length=int(self.constraints.get("title_max_length", 80)),
            field_name="title",
        )

        # Subtitle
        if getattr(slide, "subtitle", None):
            slide.subtitle = self._validate_text(
                slide.subtitle,
                max_length=int(self.constraints.get("subtitle_max_length", 100)),
                field_name="subtitle",
            )

        # Bullets
        bullets: List[str] = list(getattr(slide, "bullet_points", []) or [])
        if bullets:
            max_bullets = self._max_bullets()
            max_bullet_len = int(self.constraints.get("bullet_max_length", 120))

            if len(bullets) > max_bullets:
                bullets = bullets[:max_bullets]

            validated: List[str] = []
            for b in bullets:
                v = self._validate_text(
                    b,
                    max_length=max_bullet_len,
                    min_length=int(self.constraints.get("min_chars_per_bullet", 0)),
                    field_name="bullet",
                )
                if v:
                    validated.append(v)

            slide.bullet_points = validated

            if len(slide.bullet_points) < self._min_bullets():
                logger.debug(
                    f"Slide {slide.slide_number}: bullet count {len(slide.bullet_points)} below recommended minimum"
                )

        return slide

    def _validate_text(
        self,
        text: str,
        max_length: Optional[int] = None,
        min_length: int = 0,
        field_name: str = "text",
    ) -> str:
        """
        Test expectations:
        - callable as _validate_text(text)
        - callable as _validate_text(text, 100)
        - returned length must be <= max_length
        """
        if not text or not isinstance(text, str):
            return ""

        text = text.strip()

        if max_length is None:
            max_length = int(self.constraints.get("subtitle_max_length", 100))

        if min_length > 0 and len(text) < min_length:
            return text

        if len(text) > max_length:
            ellipsis = "..."
            cut = max_length - len(ellipsis)
            if cut <= 0:
                return ellipsis[:max_length]

            truncated = text[:cut]
            last_space = truncated.rfind(" ")
            if last_space > int(cut * 0.8):
                truncated = truncated[:last_space]

            return truncated.rstrip() + ellipsis

        return text

    def validate_presentation(self, outline) -> bool:
        slides = getattr(outline, "slides", None) or []
        return len(slides) >= int(self.constraints.get("slides_minimum", 3))