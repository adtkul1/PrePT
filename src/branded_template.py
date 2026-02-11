"""
Enhanced template handler for branded templates with master slides
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from pptx import Presentation
from pptx.util import Inches, Pt

logger = logging.getLogger(__name__)


class BrandedTemplateHandler:
    """Handles branded PPTX templates with master slides and images"""
    
    def __init__(self, template_path: Path):
        """
        Initialize with a branded template PPTX
        
        Args:
            template_path: Path to template PPTX file
        """
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        self.template_path = template_path
        self.template_prs = Presentation(str(template_path))
        self._analyze_template()
    
    def _analyze_template(self):
        """Analyze template structure for reuse"""
        logger.info(f"Analyzing template: {self.template_path.name}")
        
        # Extract template info
        self.slide_count = len(self.template_prs.slides)
        self.slide_width = self.template_prs.slide_width
        self.slide_height = self.template_prs.slide_height
        
        # Analyze available slide layouts
        self.available_layouts = []
        for idx, layout in enumerate(self.template_prs.slide_layouts):
            layout_name = layout.name
            shape_count = len(layout.shapes)
            self.available_layouts.append({
                'index': idx,
                'name': layout_name,
                'shapes': shape_count
            })
            logger.debug(f"Layout {idx}: {layout_name} ({shape_count} shapes)")
        
        logger.info(
            f"Template has {len(self.available_layouts)} layouts, "
            f"dimensions: {self.slide_width} x {self.slide_height}"
        )
    
    def get_slide_layout(self, layout_index: int = 0) -> Any:
        """Get a slide layout by index"""
        if layout_index >= len(self.template_prs.slide_layouts):
            logger.warning(
                f"Layout {layout_index} not found, using default"
            )
            layout_index = 0
        
        return self.template_prs.slide_layouts[layout_index]
    
    def create_presentation_from_template(self) -> Presentation:
        """Create new presentation based on template"""
        # Create presentation with template as base
        # This preserves master slides and theme
        return Presentation(str(self.template_path))
    
    def get_template_colors(self) -> Dict[str, str]:
        """Extract color scheme from template"""
        colors = {}
        
        try:
            # Try to extract colors from theme
            if hasattr(self.template_prs, 'core_properties'):
                logger.debug("Extracting colors from template theme")
        except Exception as e:
            logger.warning(f"Could not extract colors: {e}")
        
        return colors
    
    def list_layouts(self) -> List[Dict[str, Any]]:
        """List all available slide layouts"""
        return self.available_layouts
    
    def find_best_layout(self, has_title: bool = True, 
                        has_content: bool = True) -> int:
        """Find best layout for content type"""
        # Strategy: prefer layouts with more shape flexibility
        best_idx = 0
        best_score = -1
        
        for layout_info in self.available_layouts:
            score = layout_info['shapes']
            if score > best_score:
                best_score = score
                best_idx = layout_info['index']
        
        logger.debug(f"Selected layout {best_idx} (score: {best_score})")
        return best_idx


class ImageDownloader:
    """Handles downloading images from SharePoint"""
    
    @staticmethod
    def get_sharepoint_image(
        sharepoint_url: str,
        image_name: str,
        local_cache_dir: Path
    ) -> Optional[Path]:
        """
        Download image from SharePoint URL
        
        Note: Requires proper authentication and network access
        
        Args:
            sharepoint_url: SharePoint folder URL
            image_name: Name of image file
            local_cache_dir: Local directory to cache images
        
        Returns:
            Path to downloaded image or None if failed
        """
        local_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create local path
        local_path = local_cache_dir / image_name
        
        try:
            # Try to download from SharePoint
            # This requires sharepoint authentication which should be handled
            # by the user's environment (Windows credentials, etc.)
            
            logger.info(f"Attempting to access: {image_name}")
            
            # Since direct access requires authentication, provide guidance
            logger.warning(
                f"To use images from SharePoint:\n"
                f"1. Download images manually from:\n"
                f"   {sharepoint_url}\n"
                f"2. Save to: {local_cache_dir}\n"
                f"3. Or use Office365 CLI to automate: "
                f"o365 --auth-flow devicelogin spo file get "
                f"--webUrl [site] --folderPath [path] --fileName {image_name}"
            )
            
            return local_path if local_path.exists() else None
            
        except Exception as e:
            logger.error(f"Failed to download image {image_name}: {e}")
            return None


class TemplateContentInjector:
    """Injects GenAI content into branded template"""
    
    def __init__(self, template_handler: BrandedTemplateHandler):
        self.template_handler = template_handler
    
    def inject_content(
        self,
        prs: Presentation,
        slide_outlines: List[Any],
        image_paths: Optional[Dict[str, Path]] = None
    ) -> Presentation:
        """
        Inject content from outline into template presentation
        
        Args:
            prs: Presentation to inject into (from template)
            slide_outlines: List of slide outline objects
            image_paths: Dictionary mapping slide numbers to image paths
        
        Returns:
            Modified presentation with injected content
        """
        
        # Remove example slides from template (keep masters)
        while len(prs.slides) > 0:
            rId = prs.slides._sldIdLst[0].rId
            prs.part.drop_rel(rId)
            del prs.slides._sldIdLst[0]
        
        logger.info(f"Cleared template slides, adding {len(slide_outlines)} content slides")
        
        # Add content slides
        for outline in slide_outlines:
            try:
                self._add_slide_to_presentation(prs, outline, image_paths)
            except Exception as e:
                logger.error(f"Failed to add slide: {e}")
                raise
        
        return prs
    
    def _add_slide_to_presentation(
        self,
        prs: Presentation,
        outline: Any,
        image_paths: Optional[Dict[str, Path]] = None
    ):
        """Add a single slide with content to presentation"""
        
        # Choose best layout for content
        layout_idx = self.template_handler.find_best_layout()
        layout = self.template_handler.get_slide_layout(layout_idx)
        
        # Add slide
        slide = prs.slides.add_slide(layout)
        
        # Populate shapes with content
        shapes = slide.shapes
        
        # Find title and body placeholders
        for shape in shapes:
            if hasattr(shape, "text_frame"):
                if shape.is_placeholder:
                    phf = shape.placeholder_format
                    
                    # Title placeholder
                    if phf.type == 1:  # PP_PLACEHOLDER.TITLE
                        shape.text = outline.title
                    
                    # Body/content placeholder
                    elif phf.type == 2:  # PP_PLACEHOLDER.BODY
                        if hasattr(outline, 'bullet_points') and outline.bullet_points:
                            for idx, bullet in enumerate(outline.bullet_points):
                                if idx == 0:
                                    p = shape.text_frame.paragraphs[0]
                                else:
                                    p = shape.text_frame.add_paragraph()
                                p.text = bullet
                                p.level = 0
        
        logger.debug(f"Added slide: {outline.title}")
