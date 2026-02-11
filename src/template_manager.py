"""
Template management and loading
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.models import TemplateConfig


class TemplateManager:
    """Manages presentation templates"""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self._templates_cache: Dict[str, Dict[str, Any]] = {}
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load template configuration and assets"""
        if template_name in self._templates_cache:
            return self._templates_cache[template_name]
        
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise ValueError(f"Template '{template_name}' not found")
        
        config_file = template_path / "config.yaml"
        
        if not config_file.exists():
            raise ValueError(f"Template config not found: {config_file}")
        
        with open(config_file, 'r') as f:
            template_config = yaml.safe_load(f)
        
        # Load additional assets paths
        template_config['assets_dir'] = template_path / "theme" / "assets"
        template_config['layouts_dir'] = template_path / "slide_layouts"
        
        self._templates_cache[template_name] = template_config
        return template_config
    
    def get_available_templates(self) -> list:
        """Get list of available templates"""
        templates = []
        for item in self.templates_dir.iterdir():
            if item.is_dir() and (item / "config.yaml").exists():
                templates.append(item.name)
        return templates
    
    def validate_template(self, template_config: Dict[str, Any]) -> bool:
        """Validate template structure"""
        required_keys = ['template', 'theme', 'slide_layouts', 'constraints']
        return all(key in template_config for key in required_keys)
    
    def get_slide_layout(self, template_name: str, layout_type: str) -> Dict[str, Any]:
        """Get specific slide layout"""
        config = self.load_template(template_name)
        return config['slide_layouts'].get(layout_type, {})
    
    def get_template_constraints(self, template_name: str) -> Dict[str, Any]:
        """Get template constraints"""
        config = self.load_template(template_name)
        return config.get('constraints', {})
