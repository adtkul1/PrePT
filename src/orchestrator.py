"""
Orchestrates the presentation generation pipeline
"""

import logging
from typing import Optional

from models import SlideOutline, SlideType
from content_mapper import ContentMapper
from content_generator import ContentGenerator
from template_manager import TemplateManager
from presentation_builder import PresentationBuilder

logger = logging.getLogger(__name__)

class PresentationOrchestrator:
    """Orchestrates the generation pipeline"""

    def __init__(
        self,
        content_generator=None,
        template_manager=None,
        presentation_builder=None,
        content_mapper=None,
        branded_template_handler=None,
    ):
        self.content_generator = content_generator or ContentGenerator()
        self.template_manager = template_manager or TemplateManager()
        self.presentation_builder_class = presentation_builder or PresentationBuilder
        self.content_mapper = content_mapper or ContentMapper()
        self.branded_template_handler = branded_template_handler

    def generate(
        self,
        topic: str,
        num_slides: int,
        template_name: str = "corporate",
        audience: Optional[str] = None,
        tone: str = "professional",
        use_branded_template: bool = True,
    ) -> str:
        """Generate complete presentation"""

        logger.info(f"Generating presentation: '{topic}' ({num_slides} slides)")

        # Load template
        template_config = self.template_manager.load_template(template_name)
        logger.info(f"Loaded template: {template_name}")

        # Get constraints
        constraints = self.template_manager.get_template_constraints(template_name)

        # Generate content
        outline = self.content_generator.generate_presentation_outline(
            topic=topic,
            num_slides=num_slides,
            audience=audience,
            tone=tone,
            template_constraints=constraints,
        )

        # Validate and adapt slides
        for slide in outline.slides:
            self.content_mapper.validate_slide_outline(slide)

        # Build presentation
        builder = self.presentation_builder_class(template_config)
        prs = builder.build_from_outline(outline)

        # Save output
        output_path = (
            self.template_manager.templates_dir.parent
            / "output"
            / f"{topic.replace(' ', '_')[:30]}.pptx"
        )
        output_path.parent.mkdir(exist_ok=True)

        prs.save(str(output_path))
        logger.info(f"Presentation generated successfully: {output_path}")

        return str(output_path)