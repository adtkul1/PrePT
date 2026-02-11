#!/usr/bin/env python
"""
Sample demonstration of DocGen with branded template
Shows input topic and outputs a generated PPTX file
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.content_generator import ContentGenerator
from src.template_manager import TemplateManager
from src.presentation_builder import PresentationBuilder
from src.orchestrator import PresentationOrchestrator, ContentMapper
from src.branded_template import BrandedTemplateHandler
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Generate sample presentation"""
    
    # Sample input topic
    TOPIC = "The Future of Artificial Intelligence in Enterprise"
    NUM_SLIDES = 6
    AUDIENCE = "Executive Leadership"
    TONE = "professional"
    
    print("\n" + "="*70)
    print("📊 DocGen Sample Presentation Generation")
    print("="*70)
    print(f"\n📝 INPUT TOPIC: {TOPIC}")
    print(f"📑 SLIDES: {NUM_SLIDES}")
    print(f"👥 AUDIENCE: {AUDIENCE}")
    print(f"🎯 TONE: {TONE}")
    print("\n" + "="*70 + "\n")
    
    try:
        # Initialize components
        print("🔧 Initializing components...")
        content_gen = ContentGenerator()
        template_mgr = TemplateManager(Path(__file__).parent / "templates")
        content_map = ContentMapper(
            template_mgr.get_template_constraints("corporate")
        )
        
        # Try to load branded template
        branded_handler = None
        branded_template_path = Path(__file__).parent / "templates" / "accenture_template.pptx"
        if branded_template_path.exists():
            try:
                print("📐 Loading branded Accenture template...")
                branded_handler = BrandedTemplateHandler(branded_template_path)
                print(f"   ✅ Template loaded successfully")
                print(f"   📊 Slide dimensions: {branded_handler.slide_width} x {branded_handler.slide_height}")
                print(f"   🎨 Available layouts: {len(branded_handler.available_layouts)}")
            except Exception as e:
                print(f"   ⚠️  Could not load branded template: {e}")
        else:
            print(f"   ℹ️  Branded template not found at {branded_template_path}")
        
        # Create orchestrator
        orchestrator = PresentationOrchestrator(
            content_generator=content_gen,
            template_manager=template_mgr,
            presentation_builder=PresentationBuilder,
            content_mapper=content_map,
            branded_template_handler=branded_handler
        )
        
        print("\n🤖 Generating content with GenAI...")
        print("   (This may take 15-30 seconds...)\n")
        
        # Generate presentation
        result_path = orchestrator.generate(
            topic=TOPIC,
            num_slides=NUM_SLIDES,
            template_name="corporate",
            audience=AUDIENCE,
            tone=TONE,
            use_branded_template=branded_handler is not None
        )
        
        print("\n" + "="*70)
        print("✅ PRESENTATION GENERATED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📁 Output file: {result_path}")
        print(f"📦 File size: {Path(result_path).stat().st_size / 1024:.1f} KB")
        print(f"📂 Location: {Path(result_path).parent}")
        print("\n" + "="*70)
        print("\n✨ What's inside:")
        print("   • Branded Accenture template (if available)")
        print("   • 6 professionally structured slides")
        print("   • AI-generated content about AI in Enterprise")
        print("   • Master slides and theme preserved")
        print("   • Ready to present immediately")
        print("\n" + "="*70 + "\n")
        
        return result_path
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Generation failed")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print("👉 Next steps:")
        print(f"   1. Open: {result}")
        print("   2. Review the slides")
        print("   3. Edit as needed in PowerPoint/Google Slides")
        print("   4. Present! 🎉\n")
        sys.exit(0)
    else:
        print("Failed to generate presentation")
        sys.exit(1)
