"""
Maps generated content to template constraints
"""

import logging
from typing import List, Dict, Any, Optional
from src.models import SlideOutline, SlideType

logger = logging.getLogger(__name__)


class ContentMapper:
    """Maps GenAI content to template requirements"""
    
    def __init__(self, template_constraints: Dict[str, Any]):
        self.constraints = template_constraints
    
    def validate_and_adapt_slide(self, slide: SlideOutline) -> SlideOutline:
        """Validate slide content and adapt to constraints"""
        
        # Validate and truncate title
        slide.title = self._validate_text(
            slide.title,
            self.constraints.get('title_max_length', 80),
            field_name='title'
        )
        
        # Validate and adapt subtitle
        if slide.subtitle:
            slide.subtitle = self._validate_text(
                slide.subtitle,
                self.constraints.get('subtitle_max_length', 100),
                field_name='subtitle'
            )
        
        # Validate and adapt bullets
        if slide.bullet_points:
            max_bullets = self.constraints.get('bullets_per_slide', 5)
            max_bullet_length = self.constraints.get('bullet_max_length', 120)
            
            # Limit number of bullets
            if len(slide.bullet_points) > max_bullets:
                logger.warning(
                    f"Slide has {len(slide.bullet_points)} bullets, "
                    f"limiting to {max_bullets}"
                )
                slide.bullet_points = slide.bullet_points[:max_bullets]
            
            # Validate each bullet
            validated_bullets = []
            for bullet in slide.bullet_points:
                validated = self._validate_text(
                    bullet,
                    max_bullet_length,
                    min_length=20,
                    field_name='bullet'
                )
                if validated:
                    validated_bullets.append(validated)
            
            slide.bullet_points = validated_bullets
            
            # Ensure minimum bullets
            min_bullets = 3
            if len(slide.bullet_points) < min_bullets:
                logger.warning(
                    f"Slide has only {len(slide.bullet_points)} bullets, "
                    f"minimum recommended is {min_bullets}"
                )
        
        return slide
    
    def _validate_text(
        self,
        text: str,
        max_length: int,
        min_length: int = 0,
        field_name: str = "text"
    ) -> str:
        """Validate and adapt text content"""
        
        if not text or not isinstance(text, str):
            return ""
        
        text = text.strip()
        
        # Check minimum length
        if min_length > 0 and len(text) < min_length:
            logger.debug(
                f"{field_name} too short ({len(text)} < {min_length}): {text}"
            )
            return text  # Return as-is, may be handled by validation
        
        # Truncate if too long
        if len(text) > max_length:
            logger.warning(
                f"{field_name} exceeds max length ({len(text)} > {max_length}), "
                f"truncating: {text[:30]}..."
            )
            # Truncate at word boundary
            truncated = text[:max_length]
            # Find last space for cleaner cut
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:  # If last space is within 80% of max
                truncated = truncated[:last_space]
            truncated += "..." if len(text) > max_length else ""
            return truncated.rstrip()
        
        return text
    
    def validate_presentation(self, outline) -> bool:
        """Validate entire presentation"""
        
        min_slides = self.constraints.get('slides_minimum', 3)
        max_slides = self.constraints.get('slides_maximum', 20)
        
        if len(outline.slides) < min_slides:
            logger.error(
                f"Presentation has {len(outline.slides)} slides, "
                f"minimum is {min_slides}"
            )
            return False
        
        if len(outline.slides) > max_slides:
            logger.warning(
                f"Presentation has {len(outline.slides)} slides, "
                f"maximum recommended is {max_slides}"
            )
            return True
        
        # Validate each slide
        for slide in outline.slides:
            if not slide.title:
                logger.error(f"Slide {slide.slide_number} missing title")
                return False
        
        return True


class PresentationOrchestrator:
    """Orchestrates the generation pipeline"""
    
    def __init__(
        self,
        content_generator,
        template_manager,
        presentation_builder,
        content_mapper
    ):
        self.content_generator = content_generator
        self.template_manager = template_manager
        self.presentation_builder_class = presentation_builder
        self.content_mapper = content_mapper
    
    def generate(
        self,
        topic: str,
        num_slides: int,
        template_name: str = "corporate",
        audience: Optional[str] = None,
        tone: str = "professional"
    ) -> str:
        """
        Generate complete presentation
        
        Args:
            topic: Presentation topic
            num_slides: Number of slides
            template_name: Template to use
            audience: Target audience
            tone: Tone of presentation
        
        Returns:
            Path to generated PPTX file
        """
        
        logger.info(f"Generating presentation: '{topic}' ({num_slides} slides)")
        
        # Load template
        template_config = self.template_manager.load_template(template_name)
        logger.info(f"Loaded template: {template_name}")
        
        # Get constraints
        constraints = self.template_manager.get_template_constraints(template_name)
        
        # Generate content outline
        logger.info("Generating content with GenAI...")
        outline = self.content_generator.generate_presentation_outline(
            topic=topic,
            num_slides=num_slides,
            audience=audience,
            tone=tone,
            template_constraints=constraints
        )
        logger.info(f"Generated outline with {len(outline.slides)} slides")
        
        # Validate and adapt content to template
        logger.info("Validating and adapting content...")
        for slide in outline.slides:
            self.content_mapper.validate_and_adapt_slide(slide)
        
        # Validate entire presentation
        if not self.content_mapper.validate_presentation(outline):
            logger.warning("Presentation validation issues detected")
        
        # Build PPTX
        logger.info("Building presentation...")
        builder = self.presentation_builder_class(template_config)
        prs = builder.build_from_outline(outline)
        
        # Save presentation
        output_path = self.template_manager.templates_dir.parent / "output" / \
                      f"{topic.replace(' ', '_')[:30]}.pptx"
        output_path.parent.mkdir(exist_ok=True)
        
        result = builder.save(output_path)
        logger.info(f"Presentation generated successfully: {result}")
        
        return result
