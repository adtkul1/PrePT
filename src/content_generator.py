"""
GenAI content generation using OpenAI API
"""

import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from src.models import PresentationOutline, SlideOutline, SlideType
from src.config import (
    OPENAI_API_KEY, MODEL, MAX_RETRIES, TIMEOUT_SECONDS
)

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates presentation content using GenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = MODEL
        self.max_retries = MAX_RETRIES
    
    def generate_presentation_outline(
        self,
        topic: str,
        num_slides: int,
        audience: Optional[str] = None,
        tone: str = "professional",
        template_constraints: Optional[Dict[str, Any]] = None
    ) -> PresentationOutline:
        """Generate complete presentation outline"""
        
        system_prompt = self._build_system_prompt(tone, template_constraints)
        user_prompt = self._build_user_prompt(topic, num_slides, audience)
        
        response = self._call_api(system_prompt, user_prompt)
        
        # Parse JSON response
        try:
            content = json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse GenAI response as JSON")
            # Try to extract JSON from response
            content = self._extract_json_from_response(response)
        
        # Validate and convert to model
        outline = self._parse_outline_response(content, num_slides)
        return outline
    
    def _build_system_prompt(
        self,
        tone: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build system prompt with constraints"""
        
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
- Use clear, actionable language
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
    
    def _build_user_prompt(
        self,
        topic: str,
        num_slides: int,
        audience: Optional[str] = None
    ) -> str:
        """Build user prompt"""
        
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
- Ready for presentation delivery

Return only valid JSON, no other text."""
        
        return prompt
    
    def _call_api(self, system_prompt: str, user_prompt: str, retry_count: int = 0) -> str:
        """Call OpenAI API with retry logic"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                timeout=TIMEOUT_SECONDS
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            
            if retry_count < self.max_retries:
                logger.info(f"Retrying... (attempt {retry_count + 1}/{self.max_retries})")
                return self._call_api(system_prompt, user_prompt, retry_count + 1)
            
            raise Exception(f"Failed to generate content after {self.max_retries} retries: {str(e)}")
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from response if wrapped in text"""
        
        # Try to find JSON object in response
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        
        raise ValueError("Could not extract JSON from response")
    
    def _parse_outline_response(
        self,
        response_data: Dict[str, Any],
        expected_slides: int
    ) -> PresentationOutline:
        """Parse and validate outline response"""
        
        # Ensure proper slide types and structure
        slides = []
        slides_data = response_data.get('slides', [])
        
        for idx, slide_data in enumerate(slides_data, 1):
            # Determine slide type
            slide_type = slide_data.get('slide_type', 'content_slide')
            
            # First slide should be title
            if idx == 1:
                slide_type = SlideType.TITLE_SLIDE
            # Last slide should be closing
            elif idx == len(slides_data):
                slide_type = SlideType.CLOSING_SLIDE
            # Middle slides are content
            else:
                slide_type = SlideType.CONTENT_SLIDE
            
            # Ensure valid slide type
            try:
                slide_type = SlideType(slide_type)
            except ValueError:
                slide_type = SlideType.CONTENT_SLIDE
            
            # Build slide outline
            slide = SlideOutline(
                slide_number=idx,
                slide_type=slide_type,
                title=slide_data.get('title', f'Slide {idx}'),
                subtitle=slide_data.get('subtitle'),
                bullet_points=slide_data.get('bullet_points', []),
                speaker_notes=slide_data.get('speaker_notes')
            )
            slides.append(slide)
        
        # Create presentation outline
        outline = PresentationOutline(
            title=response_data.get('title', 'Untitled Presentation'),
            topic=response_data.get('topic', 'General Topic'),
            target_audience=response_data.get('target_audience'),
            key_message=response_data.get('key_message'),
            slides=slides
        )
        
        return outline
