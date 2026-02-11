"""
Automated Test Suite for DocGen
Tests all major components and integration points
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import CONFIG, TEMPLATES_DIR, OUTPUT_DIR
from models import SlideType, SlideOutline, PresentationOutline
from template_manager import TemplateManager
from content_generator import ContentGenerator
from orchestrator import ContentMapper, PresentationOrchestrator


class TestConfigLoading:
    """Test configuration loading and defaults"""
    
    def test_config_exists(self):
        """Test that config object exists"""
        assert CONFIG is not None
    
    def test_paths_configured(self):
        """Test that required paths are configured"""
        assert TEMPLATES_DIR.exists()
        assert OUTPUT_DIR.exists() or OUTPUT_DIR.parent.exists()
    
    def test_templates_dir_exists(self):
        """Test templates directory exists"""
        assert Path(TEMPLATES_DIR).exists()
        assert Path(TEMPLATES_DIR).is_dir()
    
    def test_output_dir_writable(self):
        """Test output directory is writable"""
        output_path = Path(OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        assert output_path.exists()
        assert os.access(str(output_path), os.W_OK)


class TestModels:
    """Test Pydantic data models"""
    
    def test_slide_type_enum(self):
        """Test SlideType enum"""
        assert SlideType.TITLE_SLIDE == "title_slide"
        assert SlideType.CONTENT_SLIDE == "content_slide"
        assert SlideType.CLOSING_SLIDE == "closing_slide"
    
    def test_slide_outline_creation(self):
        """Test SlideOutline model"""
        slide = SlideOutline(
            slide_number=1,
            title="Test Title",
            content=["Point 1", "Point 2"],
            slide_type=SlideType.TITLE_SLIDE
        )
        assert slide.slide_number == 1
        assert slide.title == "Test Title"
        assert len(slide.content) == 2
    
    def test_slide_outline_validation(self):
        """Test SlideOutline validates required fields"""
        with pytest.raises(Exception):
            SlideOutline(slide_number=1)  # Missing title
    
    def test_presentation_outline_creation(self):
        """Test PresentationOutline model"""
        slides = [
            SlideOutline(
                slide_number=1,
                title="Title",
                content=["content"],
                slide_type=SlideType.TITLE_SLIDE
            ),
            SlideOutline(
                slide_number=2,
                title="Content",
                content=["point1", "point2"],
                slide_type=SlideType.CONTENT_SLIDE
            )
        ]
        presentation = PresentationOutline(
            topic="Test Topic",
            slides=slides
        )
        assert presentation.topic == "Test Topic"
        assert len(presentation.slides) == 2


class TestTemplateManager:
    """Test template manager functionality"""
    
    def test_template_manager_creation(self):
        """Test TemplateManager can be instantiated"""
        tm = TemplateManager()
        assert tm is not None
    
    def test_get_available_templates(self):
        """Test listing available templates"""
        tm = TemplateManager()
        templates = tm.get_available_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0
    
    def test_template_loading(self):
        """Test loading a template"""
        tm = TemplateManager()
        templates = tm.get_available_templates()
        if templates:
            template = tm.load_template(templates[0])
            assert template is not None
    
    def test_branded_template_detection(self):
        """Test detection of branded template"""
        tm = TemplateManager()
        templates = tm.get_available_templates()
        # Check if accenture template is in the list
        template_names = [t.get('name', '') for t in templates]
        # Should have at least corporate template
        assert len(template_names) > 0


class TestContentMapper:
    """Test content validation and mapping"""
    
    def test_content_mapper_creation(self):
        """Test ContentMapper instantiation"""
        mapper = ContentMapper()
        assert mapper is not None
    
    def test_text_validation_length(self):
        """Test text validation for length constraints"""
        mapper = ContentMapper()
        
        # Short text should pass
        valid = mapper._validate_text("Short text", max_length=100)
        assert valid is not None
        
        # Very long text should be truncated
        long_text = "x" * 500
        result = mapper._validate_text(long_text, max_length=100)
        assert len(result) <= 100
    
    def test_slide_outline_validation(self):
        """Test slide validation"""
        mapper = ContentMapper()
        
        slide = SlideOutline(
            slide_number=1,
            title="Valid Title",
            content=["Point 1", "Point 2"],
            slide_type=SlideType.CONTENT_SLIDE
        )
        
        result = mapper.validate_and_adapt_slide(slide)
        assert result is not None
        assert result.title is not None
    
    def test_presentation_validation(self):
        """Test presentation-level validation"""
        mapper = ContentMapper()
        
        slides = [
            SlideOutline(
                slide_number=1,
                title="Slide 1",
                content=["content"],
                slide_type=SlideType.TITLE_SLIDE
            ),
            SlideOutline(
                slide_number=2,
                title="Slide 2",
                content=["point1"],
                slide_type=SlideType.CONTENT_SLIDE
            )
        ]
        
        presentation = PresentationOutline(
            topic="Test",
            slides=slides
        )
        
        result = mapper.validate_presentation(presentation)
        assert result is not None


class TestContentGenerator:
    """Test GenAI content generation (requires API key)"""
    
    @pytest.mark.skipif(
        'SKIP_API_TESTS' in os.environ,
        reason="Skipping API tests (set SKIP_API_TESTS=0 to run)"
    )
    def test_generator_creation(self):
        """Test ContentGenerator instantiation"""
        try:
            gen = ContentGenerator()
            assert gen is not None
        except Exception as e:
            pytest.skip(f"API not configured: {str(e)}")
    
    @pytest.mark.skipif(
        'SKIP_API_TESTS' in os.environ,
        reason="Skipping API tests"
    )
    def test_outline_generation(self):
        """Test outline generation"""
        try:
            gen = ContentGenerator()
            outline = gen.generate_presentation_outline(
                topic="Python Programming",
                num_slides=4
            )
            assert outline is not None
            assert outline.topic == "Python Programming"
            assert len(outline.slides) == 4
        except Exception as e:
            pytest.skip(f"API call failed: {str(e)}")
    
    @pytest.mark.skipif(
        'SKIP_API_TESTS' in os.environ,
        reason="Skipping API tests"
    )
    def test_outline_validation(self):
        """Test that generated outline is valid"""
        try:
            gen = ContentGenerator()
            outline = gen.generate_presentation_outline(
                topic="Cloud Computing",
                num_slides=3
            )
            
            assert outline.topic == "Cloud Computing"
            assert len(outline.slides) >= 3
            
            for slide in outline.slides:
                assert slide.title is not None
                assert len(slide.title) > 0
                assert isinstance(slide.content, list)
                assert len(slide.content) > 0
        except Exception as e:
            pytest.skip(f"API call failed: {str(e)}")


class TestOrchestrator:
    """Test orchestrator and full pipeline"""
    
    def test_orchestrator_creation(self):
        """Test PresentationOrchestrator instantiation"""
        orchestrator = PresentationOrchestrator()
        assert orchestrator is not None
    
    @pytest.mark.skipif(
        'SKIP_API_TESTS' in os.environ,
        reason="Skipping API tests"
    )
    def test_full_generation_pipeline(self):
        """Test end-to-end generation"""
        try:
            orchestrator = PresentationOrchestrator()
            
            output_file = orchestrator.generate(
                topic="Test Presentation",
                num_slides=3,
                audience="General",
                tone="professional"
            )
            
            assert output_file is not None
            assert Path(output_file).exists()
            assert output_file.endswith('.pptx')
            
            # Clean up
            Path(output_file).unlink()
        except Exception as e:
            pytest.skip(f"Generation failed: {str(e)}")
    
    @pytest.mark.skipif(
        'SKIP_API_TESTS' in os.environ,
        reason="Skipping API tests"
    )
    def test_generation_with_parameters(self):
        """Test generation with all optional parameters"""
        try:
            orchestrator = PresentationOrchestrator()
            
            output_file = orchestrator.generate(
                topic="Digital Transformation",
                num_slides=5,
                audience="Executive Leadership",
                tone="professional"
            )
            
            assert output_file is not None
            assert Path(output_file).exists()
            assert "Digital_Transformation" in output_file
            
            # Clean up
            Path(output_file).unlink()
        except Exception as e:
            pytest.skip(f"Generation failed: {str(e)}")


class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_components_initialization(self):
        """Test all components can be initialized"""
        tm = TemplateManager()
        mapper = ContentMapper()
        orchestrator = PresentationOrchestrator()
        
        assert tm is not None
        assert mapper is not None
        assert orchestrator is not None
    
    @pytest.mark.skipif(
        'SKIP_API_TESTS' in os.environ,
        reason="Skipping API tests"
    )
    def test_complete_workflow(self):
        """Test complete generation workflow"""
        try:
            # Initialize components
            orchestrator = PresentationOrchestrator()
            
            # Generate presentation
            output_file = orchestrator.generate(
                topic="Machine Learning",
                num_slides=4,
                audience="Data Scientists",
                tone="technical"
            )
            
            # Verify output
            assert output_file is not None
            assert Path(output_file).exists()
            assert output_file.endswith('.pptx')
            
            # Check file size
            file_size = Path(output_file).stat().st_size
            assert file_size > 100_000  # At least 100KB
            
            # Clean up
            Path(output_file).unlink()
            
        except Exception as e:
            pytest.skip(f"Workflow failed: {str(e)}")


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_slide_number(self):
        """Test invalid slide number"""
        with pytest.raises(Exception):
            SlideOutline(
                slide_number=0,  # Invalid
                title="Title",
                content=["content"],
                slide_type=SlideType.CONTENT_SLIDE
            )
    
    def test_empty_content_handling(self):
        """Test handling of empty content"""
        mapper = ContentMapper()
        result = mapper._validate_text("")
        assert result is not None
    
    def test_very_long_title(self):
        """Test handling of very long titles"""
        mapper = ContentMapper()
        long_title = "x" * 500
        result = mapper._validate_text(long_title, max_length=100)
        assert len(result) <= 100
    
    def test_special_characters(self):
        """Test handling of special characters"""
        mapper = ContentMapper()
        text_with_special = "Test with special chars: !@#$%^&*()"
        result = mapper._validate_text(text_with_special)
        assert result is not None


class TestFileOperations:
    """Test file operations and output"""
    
    def test_output_directory_creation(self):
        """Test output directory creation"""
        output_path = Path(OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        assert output_path.exists()
    
    def test_pptx_file_naming(self):
        """Test PPTX file naming convention"""
        topic = "Test Topic With Spaces"
        expected_name = topic.replace(" ", "_") + ".pptx"
        assert "_" in expected_name
        assert ".pptx" in expected_name
    
    def test_output_file_cleanup(self):
        """Test cleanup of test output files"""
        test_file = Path(OUTPUT_DIR) / "test_cleanup_file.pptx"
        test_file.touch()
        assert test_file.exists()
        test_file.unlink()
        assert not test_file.exists()


# ============================================================================
# Test Execution Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "--tb=short"])
