from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

from models import PresentationOutline, SlideOutline, SlideType  # <-- models.py

logger = logging.getLogger(__name__)


class PresentationBuilder:
    """Builds PPTX presentations from outlines"""

    def __init__(self, template_config: Optional[Union[Dict[str, Any], str, Path]] = None):
        """
        template_config can be:
          - None (blank Presentation)
          - dict containing 'path' to pptx template
          - direct path string/Path to pptx template
        """
        self.template_config: Dict[str, Any] = {}

        template_path: Optional[Path] = None
        if isinstance(template_config, dict):
            self.template_config = template_config
            p = template_config.get("path")
            if p:
                template_path = Path(p)
        elif isinstance(template_config, (str, Path)):
            template_path = Path(template_config)

        # Load from template pptx if provided, else blank
        if template_path and template_path.exists():
            self.prs = Presentation(str(template_path))
        else:
            self.prs = Presentation()

        # Provide safe default theme values (works even without theme config)
        self.theme = (self.template_config.get("theme") or {})
        self._apply_default_theme()

        # Set slide dimensions (standard 16:9)
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(7.5)

    def _apply_default_theme(self) -> None:
        """Ensure theme has minimal keys so slides can render even without config.yaml."""
        colors = self.theme.get("colors") or {}
        sizes = self.theme.get("sizes") or {}

        colors.setdefault("primary", "#3A0CA3")        # deep purple-ish
        colors.setdefault("accent", "#7209B7")         # accent purple
        colors.setdefault("background", "#FFFFFF")
        colors.setdefault("subtle_bg", "#F2F2F2")
        colors.setdefault("text_dark", "#111111")
        colors.setdefault("text_light", "#FFFFFF")

        sizes.setdefault("heading_large", 36)
        sizes.setdefault("heading_medium", 28)
        sizes.setdefault("heading_small", 18)
        sizes.setdefault("body_text", 16)

        self.theme["colors"] = colors
        self.theme["sizes"] = sizes

    def _hex_to_rgb(self, hex_color: str) -> RGBColor:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip("#")
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )

    def _add_title_slide(self, slide: SlideOutline) -> None:
        blank_layout = self.prs.slide_layouts[6]  # blank
        prs_slide = self.prs.slides.add_slide(blank_layout)

        # background
        background = prs_slide.shapes.add_shape(
            1, 0, 0, self.prs.slide_width, self.prs.slide_height
        )
        background.fill.solid()
        background.fill.fore_color.rgb = self._hex_to_rgb(self.theme["colors"]["primary"])
        background.line.color.rgb = self._hex_to_rgb(self.theme["colors"]["primary"])
        prs_slide.shapes._spTree.remove(background._element)
        prs_slide.shapes._spTree.insert(2, background._element)

        # title
        title_box = prs_slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1.5))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide.title
        p.font.size = Pt(self.theme["sizes"]["heading_large"])
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(self.theme["colors"]["text_light"])
        p.alignment = PP_ALIGN.CENTER

        # subtitle
        if slide.subtitle:
            subtitle_box = prs_slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(1))
            stf = subtitle_box.text_frame
            stf.word_wrap = True
            sp = stf.paragraphs[0]
            sp.text = slide.subtitle
            sp.font.size = Pt(self.theme["sizes"]["heading_small"])
            sp.font.color.rgb = self._hex_to_rgb(self.theme["colors"]["text_light"])
            sp.alignment = PP_ALIGN.CENTER

    def _add_content_slide(self, slide: SlideOutline) -> None:
        blank_layout = self.prs.slide_layouts[6]
        prs_slide = self.prs.slides.add_slide(blank_layout)

        # background
        background = prs_slide.shapes.add_shape(
            1, 0, 0, self.prs.slide_width, self.prs.slide_height
        )
        background.fill.solid()
        background.fill.fore_color.rgb = self._hex_to_rgb(self.theme["colors"]["background"])
        background.line.color.rgb = self._hex_to_rgb(self.theme["colors"]["subtle_bg"])
        prs_slide.shapes._spTree.remove(background._element)
        prs_slide.shapes._spTree.insert(2, background._element)

        # title
        title_box = prs_slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(9), Inches(0.8))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide.title
        p.font.size = Pt(self.theme["sizes"]["heading_medium"])
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(self.theme["colors"]["primary"])

        # bullets (support both .bullet_points and .content alias)
        bullets = slide.bullet_points or slide.content
        if bullets:
            content_box = prs_slide.shapes.add_textbox(Inches(0.75), Inches(1.5), Inches(8.5), Inches(5.5))
            text_frame = content_box.text_frame
            text_frame.word_wrap = True

            for idx, bullet in enumerate(bullets):
                para = text_frame.paragraphs[0] if idx == 0 else text_frame.add_paragraph()
                para.text = bullet
                para.level = 0
                para.font.size = Pt(self.theme["sizes"]["body_text"])
                para.font.color.rgb = self._hex_to_rgb(self.theme["colors"]["text_dark"])
                para.space_before = Pt(6)
                para.space_after = Pt(6)

    def _add_closing_slide(self, slide: SlideOutline) -> None:
        blank_layout = self.prs.slide_layouts[6]
        prs_slide = self.prs.slides.add_slide(blank_layout)

        background = prs_slide.shapes.add_shape(
            1, 0, 0, self.prs.slide_width, self.prs.slide_height
        )
        background.fill.solid()
        background.fill.fore_color.rgb = self._hex_to_rgb(self.theme["colors"]["accent"])
        background.line.color.rgb = self._hex_to_rgb(self.theme["colors"]["accent"])
        prs_slide.shapes._spTree.remove(background._element)
        prs_slide.shapes._spTree.insert(2, background._element)

        title_box = prs_slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1.5))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide.title
        p.font.size = Pt(self.theme["sizes"]["heading_large"])
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(self.theme["colors"]["text_light"])
        p.alignment = PP_ALIGN.CENTER

        if slide.subtitle:
            subtitle_box = prs_slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(1))
            stf = subtitle_box.text_frame
            stf.word_wrap = True
            sp = stf.paragraphs[0]
            sp.text = slide.subtitle
            sp.font.size = Pt(self.theme["sizes"]["heading_small"])
            sp.font.color.rgb = self._hex_to_rgb(self.theme["colors"]["text_light"])
            sp.alignment = PP_ALIGN.CENTER

    def build_from_outline(self, outline: PresentationOutline) -> Presentation:
        """Build presentation from outline"""
        for slide in outline.slides:
            if slide.slide_type == SlideType.TITLE_SLIDE:
                self._add_title_slide(slide)
            elif slide.slide_type == SlideType.CLOSING_SLIDE:
                self._add_closing_slide(slide)
            else:
                self._add_content_slide(slide)

            logger.info(f"Added slide {slide.slide_number}: {slide.title}")

        return self.prs

    def save(self, output_path: Path) -> str:
        """Save presentation to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(str(output_path))
        logger.info(f"Presentation saved to {output_path}")
        return str(output_path)