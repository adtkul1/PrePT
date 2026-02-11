"""
PPTX generation and rendering
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from src.models import PresentationOutline, SlideOutline, SlideType

logger = logging.getLogger(__name__)


class PresentationBuilder:
    """Builds PPTX presentations from outlines"""
    
    def __init__(self, template_config: Dict[str, Any]):
        self.template_config = template_config
        self.theme = template_config.get('theme', {})
        self.constraints = template_config.get('constraints', {})
        self.spacing = template_config.get('spacing', {})
        
        # Create presentation
        self.prs = Presentation()
        self._setup_presentation()
    
    def _setup_presentation(self):
        """Initialize presentation with template defaults"""
        # Set slide dimensions (standard 16:9)
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(7.5)
    
    def _hex_to_rgb(self, hex_color: str) -> RGBColor:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
    
    def _add_title_slide(self, slide: SlideOutline):
        """Add title slide"""
        # Create blank slide
        blank_layout = self.prs.slide_layouts[6]  # Blank layout
        prs_slide = self.prs.slides.add_slide(blank_layout)
        
        # Add background shape
        background = prs_slide.shapes.add_shape(
            1,  # Rectangle
            0, 0,
            self.prs.slide_width,
            self.prs.slide_height
        )
        background.fill.solid()
        background.fill.fore_color.rgb = self._hex_to_rgb(
            self.theme['colors']['primary']
        )
        background.line.color.rgb = self._hex_to_rgb(
            self.theme['colors']['primary']
        )
        
        # Move background to back
        prs_slide.shapes._spTree.remove(background._element)
        prs_slide.shapes._spTree.insert(2, background._element)
        
        # Add title
        title_box = prs_slide.shapes.add_textbox(
            Inches(0.5), Inches(2.5),
            Inches(9), Inches(1.5)
        )
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        title_p = title_frame.paragraphs[0]
        title_p.text = slide.title
        title_p.font.size = Pt(self.theme['sizes']['heading_large'])
        title_p.font.bold = True
        title_p.font.color.rgb = self._hex_to_rgb(
            self.theme['colors']['text_light']
        )
        title_p.alignment = PP_ALIGN.CENTER
        
        # Add subtitle
        if slide.subtitle:
            subtitle_box = prs_slide.shapes.add_textbox(
                Inches(0.5), Inches(4.2),
                Inches(9), Inches(1)
            )
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.word_wrap = True
            subtitle_p = subtitle_frame.paragraphs[0]
            subtitle_p.text = slide.subtitle
            subtitle_p.font.size = Pt(self.theme['sizes']['heading_small'])
            subtitle_p.font.color.rgb = self._hex_to_rgb(
                self.theme['colors']['text_light']
            )
            subtitle_p.alignment = PP_ALIGN.CENTER
    
    def _add_content_slide(self, slide: SlideOutline):
        """Add content slide with bullets"""
        blank_layout = self.prs.slide_layouts[6]
        prs_slide = self.prs.slides.add_slide(blank_layout)
        
        # Add background
        background = prs_slide.shapes.add_shape(
            1,
            0, 0,
            self.prs.slide_width,
            self.prs.slide_height
        )
        background.fill.solid()
        background.fill.fore_color.rgb = self._hex_to_rgb(
            self.theme['colors']['background']
        )
        background.line.color.rgb = self._hex_to_rgb(
            self.theme['colors']['subtle_bg']
        )
        
        # Move background to back
        prs_slide.shapes._spTree.remove(background._element)
        prs_slide.shapes._spTree.insert(2, background._element)
        
        # Add title
        title_box = prs_slide.shapes.add_textbox(
            Inches(0.5), Inches(0.4),
            Inches(9), Inches(0.8)
        )
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        title_p = title_frame.paragraphs[0]
        title_p.text = slide.title
        title_p.font.size = Pt(self.theme['sizes']['heading_medium'])
        title_p.font.bold = True
        title_p.font.color.rgb = self._hex_to_rgb(
            self.theme['colors']['primary']
        )
        
        # Add bullet points
        if slide.bullet_points:
            content_box = prs_slide.shapes.add_textbox(
                Inches(0.75), Inches(1.5),
                Inches(8.5), Inches(5.5)
            )
            text_frame = content_box.text_frame
            text_frame.word_wrap = True
            
            for idx, bullet in enumerate(slide.bullet_points):
                if idx == 0:
                    p = text_frame.paragraphs[0]
                else:
                    p = text_frame.add_paragraph()
                
                p.text = bullet
                p.level = 0
                p.font.size = Pt(self.theme['sizes']['body_text'])
                p.font.color.rgb = self._hex_to_rgb(
                    self.theme['colors']['text_dark']
                )
                p.space_before = Pt(6)
                p.space_after = Pt(6)
    
    def _add_closing_slide(self, slide: SlideOutline):
        """Add closing/summary slide"""
        blank_layout = self.prs.slide_layouts[6]
        prs_slide = self.prs.slides.add_slide(blank_layout)
        
        # Add background with accent color
        background = prs_slide.shapes.add_shape(
            1,
            0, 0,
            self.prs.slide_width,
            self.prs.slide_height
        )
        background.fill.solid()
        background.fill.fore_color.rgb = self._hex_to_rgb(
            self.theme['colors']['accent']
        )
        background.line.color.rgb = self._hex_to_rgb(
            self.theme['colors']['accent']
        )
        
        # Move background to back
        prs_slide.shapes._spTree.remove(background._element)
        prs_slide.shapes._spTree.insert(2, background._element)
        
        # Add title
        title_box = prs_slide.shapes.add_textbox(
            Inches(0.5), Inches(2.5),
            Inches(9), Inches(1.5)
        )
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        title_p = title_frame.paragraphs[0]
        title_p.text = slide.title
        title_p.font.size = Pt(self.theme['sizes']['heading_large'])
        title_p.font.bold = True
        title_p.font.color.rgb = self._hex_to_rgb(
            self.theme['colors']['text_light']
        )
        title_p.alignment = PP_ALIGN.CENTER
        
        # Add subtitle
        if slide.subtitle:
            subtitle_box = prs_slide.shapes.add_textbox(
                Inches(0.5), Inches(4.2),
                Inches(9), Inches(1)
            )
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.word_wrap = True
            subtitle_p = subtitle_frame.paragraphs[0]
            subtitle_p.text = slide.subtitle
            subtitle_p.font.size = Pt(self.theme['sizes']['heading_small'])
            subtitle_p.font.color.rgb = self._hex_to_rgb(
                self.theme['colors']['text_light']
            )
            subtitle_p.alignment = PP_ALIGN.CENTER
    
    def build_from_outline(self, outline: PresentationOutline) -> Presentation:
        """Build presentation from outline"""
        
        for slide in outline.slides:
            try:
                if slide.slide_type == SlideType.TITLE_SLIDE:
                    self._add_title_slide(slide)
                elif slide.slide_type == SlideType.CLOSING_SLIDE:
                    self._add_closing_slide(slide)
                else:  # content_slide, two_column, etc.
                    self._add_content_slide(slide)
                
                logger.info(f"Added slide {slide.slide_number}: {slide.title}")
                
            except Exception as e:
                logger.error(f"Failed to add slide {slide.slide_number}: {str(e)}")
                raise
        
        return self.prs
    
    def save(self, output_path: Path) -> str:
        """Save presentation to file"""
        
        try:
            self.prs.save(str(output_path))
            logger.info(f"Presentation saved to {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Failed to save presentation: {str(e)}")
            raise
