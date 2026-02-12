from __future__ import annotations

import json
import logging
from typing import Dict, List, Any, Optional

from models import PresentationOutline, SlideOutline, SlideType
from config import OPENAI_API_KEY, MODEL, MAX_RETRIES, TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates presentation content using GenAI (or deterministic fallback)"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else OPENAI_API_KEY
        self.model = model if model is not None else MODEL
        self.max_retries = MAX_RETRIES

        self.client = None
        if self.api_key:
            try:
                # Lazy import so tests pass even if openai isn't installed/used
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"OpenAI client not initialized; falling back. Reason: {e}")
                self.client = None

    def generate_presentation_outline(
        self,
        topic: str,
        num_slides: int,
        audience: Optional[str] = None,
        tone: str = "professional",
        template_constraints: Optional[Dict[str, Any]] = None,
    ) -> PresentationOutline:
        """
        Generate complete presentation outline.
        If no API client is available, returns a deterministic outline (no API).
        """
        if not self.client:
            return self._fallback_outline(topic, num_slides, audience, tone)

        system_prompt = self._build_system_prompt(tone, template_constraints)
        user_prompt = self._build_user_prompt(topic, num_slides, audience)
        response = self._call_api(system_prompt, user_prompt)

        try:
            content = json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse GenAI response as JSON; attempting extraction.")
            content = self._extract_json_from_response(response)

        return self._parse_outline_response(content)

    def _fallback_outline(
        self,
        topic: str,
        num_slides: int,
        audience: Optional[str],
        tone: str,
    ) -> PresentationOutline:
        """Deterministic, test-safe outline used when no API is available."""
        slides: List[SlideOutline] = []

        # Slide 1: Title
        slides.append(
            SlideOutline(
                slide_number=1,
                slide_type=SlideType.TITLE_SLIDE,
                title=topic[:80],
                subtitle=(f"For {audience}" if audience else "Overview"),
                bullet_points=[],
                speaker_notes=None,
            )
        )

        # Middle content slides
        for i in range(2, max(num_slides, 3)):
            if i == num_slides:
                break
            slides.append(
                SlideOutline(
                    slide_number=i,
                    slide_type=SlideType.CONTENT_SLIDE,
                    title=f"Key Point {i-1}: {topic[:50]}",
                    subtitle=None,
                    bullet_points=[
                        f"Point {i-1}.1: Practical takeaway related to {topic}.",
                        f"Point {i-1}.2: Considerations and trade-offs for {topic}.",
                        f"Point {i-1}.3: Recommended next steps for applying {topic}.",
                    ],
                    speaker_notes=None,
                )
            )

        # Last slide: Closing
        last_n = max(num_slides, 3)
        slides.append(
            SlideOutline(
                slide_number=last_n,
                slide_type=SlideType.CLOSING_SLIDE,
                title="Summary & Next Steps",
                subtitle="Questions / Discussion",
                bullet_points=[
                    f"Recap: Why {topic} matters and what to do next.",
                    "Agree next steps and owners for follow-up actions.",
                    "Capture questions, risks, and dependencies to resolve.",
                ],
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

    def _build_system_prompt(self, tone: str, constraints: Optional[Dict[str, Any]] = None) -> str:
        prompt = f"""You are a professional presentation designer and strategist.
Generate presentations that are:
- Engaging, clear, and impactful
- Structured with proper visual hierarchy
- Concise with one key idea per slide
- Written in a {tone} tone
- Industry-appropriate and credible

IMPORTANT CONSTRAINTS:
- Title must be ≤80 characters
- Subtitles must be ≤100 characters
- Each bullet point must be 20-120 characters
- Bullet points must be 3-5 per slide
- Return valid JSON only - no additional text
"""
        if constraints:
            prompt += f"\nTemplate constraints: {json.dumps(constraints)}\n"

        prompt += """
You must return a valid JSON object with this exact structure:
{
  "title": "Main presentation title",
  "topic": "The input topic",
  "target_audience": "Intended audience",
  "key_message": "Core message of presentation",
  "slides": [
    {
      "slide_number": 1,
      "slide_type": "title_slide",
      "title": "Presentation Title",
      "subtitle": "Subtitle or tagline",
      "speaker_notes": "Optional speaker notes"
    },
    {
      "slide_number": 2,
      "slide_type": "content_slide",
      "title": "Slide Title",
      "bullet_points": ["Point 1", "Point 2", "Point 3"],
      "speaker_notes": "Optional notes"
    }
  ]
}
"""
        return prompt

    def _build_user_prompt(self, topic: str, num_slides: int, audience: Optional[str] = None) -> str:
        prompt = f"""Create a {num_slides}-slide presentation about: {topic}
Structure:
- Slide 1: Title slide with compelling opening
- Slides 2-{num_slides-1}: Content slides with key points
- Slide {num_slides}: Closing/summary slide
"""
        if audience:
            prompt += f"Target audience: {audience}\n"
        prompt += """
Make it:
- Clear and actionable
- Data-driven where possible
- Professional and engaging
Return only valid JSON, no other text.
"""
        return prompt

    def _call_api(self, system_prompt: str, user_prompt: str, retry_count: int = 0) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
                timeout=TIMEOUT_SECONDS,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            if retry_count < self.max_retries:
                return self._call_api(system_prompt, user_prompt, retry_count + 1)
            raise Exception(f"Failed after {self.max_retries} retries: {str(e)}")

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        start_idx = response.find("{")
        end_idx = response.rfind("}") + 1
        if start_idx >= 0 and end_idx > start_idx:
            return json.loads(response[start_idx:end_idx])
        raise ValueError("Could not extract JSON from response")

    def _parse_outline_response(self, response_data: Dict[str, Any]) -> PresentationOutline:
        slides: List[SlideOutline] = []
        slides_data = response_data.get("slides", []) or []

        for idx, slide_data in enumerate(slides_data, 1):
            raw_type = slide_data.get("slide_type", "content_slide")
            try:
                slide_type = SlideType(raw_type)
            except Exception:
                slide_type = SlideType.CONTENT_SLIDE

            # enforce title slide first, closing slide last
            if idx == 1:
                slide_type = SlideType.TITLE_SLIDE
            elif idx == len(slides_data):
                slide_type = SlideType.CLOSING_SLIDE

            slides.append(
                SlideOutline(
                    slide_number=idx,
                    slide_type=slide_type,
                    title=slide_data.get("title", f"Slide {idx}"),
                    subtitle=slide_data.get("subtitle"),
                    bullet_points=slide_data.get("bullet_points", []),
                    speaker_notes=slide_data.get("speaker_notes"),
                )
            )

        return PresentationOutline(
            title=response_data.get("title"),
            topic=response_data.get("topic", "General Topic"),
            target_audience=response_data.get("target_audience"),
            key_message=response_data.get("key_message"),
            slides=slides,
        )