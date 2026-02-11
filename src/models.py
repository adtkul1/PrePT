"""
Data models for presentation structure
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class SlideType(str, Enum):
    """Types of slides in presentation"""
    TITLE_SLIDE = "title_slide"
    CONTENT_SLIDE = "content_slide"
    TWO_COLUMN = "two_column"
    CLOSING_SLIDE = "closing_slide"


class SlideOutline(BaseModel):
    """Slide outline structure"""
    slide_number: int
    slide_type: SlideType
    title: str = Field(..., max_length=80)
    subtitle: Optional[str] = Field(None, max_length=100)
    bullet_points: Optional[List[str]] = []
    speaker_notes: Optional[str] = None
    
    @validator('bullet_points')
    def validate_bullets(cls, v):
        """Validate bullet points"""
        if v:
            for bullet in v:
                if len(bullet) > 120:
                    raise ValueError(f"Bullet point exceeds 120 characters: {bullet[:50]}...")
                if len(bullet) < 20:
                    raise ValueError(f"Bullet point too short: {bullet}")
        return v
    
    @validator('title')
    def validate_title(cls, v):
        """Ensure title is not empty"""
        if not v or not v.strip():
            raise ValueError("Slide title cannot be empty")
        return v.strip()


class PresentationOutline(BaseModel):
    """Complete presentation outline"""
    title: str = Field(..., max_length=100)
    topic: str
    target_audience: Optional[str] = None
    key_message: Optional[str] = None
    slides: List[SlideOutline]
    total_slides: int
    
    def __init__(self, **data):
        super().__init__(**data)
        self.total_slides = len(self.slides)


class TemplateConfig(BaseModel):
    """Template configuration"""
    name: str
    description: str
    colors: Dict[str, str]
    fonts: Dict[str, str]
    slide_layouts: Dict[str, Any]
    
    
class GenerationRequest(BaseModel):
    """User request for presentation generation"""
    topic: str = Field(..., min_length=10, max_length=200)
    num_slides: int = Field(default=6, ge=3, le=20)
    template: str = Field(default="corporate")
    audience: Optional[str] = None
    tone: str = Field(default="professional")
    custom_prompt: Optional[str] = None
