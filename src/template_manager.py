"""
Template management and loading for presentation generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from .config import TEMPLATES_DIR


class TemplateManager:
    """Manages presentation templates stored as PPTX/PPT/POTX files"""

    SUPPORTED_EXTENSIONS = {".pptx", ".ppt", ".potx"}

    def __init__(self, templates_dir: Optional[Path | str] = None):
        # Must work with no args (tests / CLI)
        self.templates_dir = Path(templates_dir) if templates_dir else Path(TEMPLATES_DIR)
        self._templates_cache: Optional[List[Dict[str, Any]]] = None

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _discover_templates(self) -> List[Dict[str, Any]]:
        """
        Scan templates directory and return metadata for all valid template files.
        """
        if not self.templates_dir.exists():
            return []

        templates: List[Dict[str, Any]] = []

        for item in sorted(self.templates_dir.iterdir()):
            if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                templates.append(
                    {
                        "name": item.stem,
                        "file": item.name,
                        "path": str(item.resolve()),
                        "format": item.suffix.lower().lstrip("."),
                        "type": "pptx_template",
                    }
                )

        return templates

    # ----------------------------
    # Public API
    # ----------------------------
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """
        Return all available templates discovered from the templates directory.
        """
        if self._templates_cache is None:
            self._templates_cache = self._discover_templates()
        return list(self._templates_cache)

    def load_template(self, template: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Load a template.
        For future: we want to support both:
        - User-specified template (by name or file) --> load that specific template
        - No user input --> load a default template (e.g. first in sorted order)
        """
        templates = self.get_available_templates()
        if not templates:
            raise ValueError(
                f"No template files found in templates directory: {self.templates_dir}"
            )

        # If template already is a discovered config dict, just return it
        if isinstance(template, dict) and template.get('path'):
            return template

        # Try to match user-specified template
        requested = str(template).strip() if template is not None else ''
        if requested:
            req_path = Path(requested)
            req_stem = req_path.stem.lower()
            req_name = req_path.name.lower()
            for t in templates:
                try:
                    stem = str(t.get('name', '')).lower()
                    fname = str(t.get('file', '')).lower()
                    path = str(t.get('path', '')).lower()
                    if req_stem and req_stem == stem:
                        return t
                    if req_name and req_name == fname:
                        return t
                    if requested and requested.lower() == path:
                        return t
                except Exception:
                    continue

        # Deterministic fallback: first template (sorted order)
        return templates[0]

    def validate_template(self, template_config: Dict[str, Any]) -> bool:
        """
        Validate that the template file exists on disk.
        """
        path = template_config.get("path")
        return bool(path) and Path(path).exists()

    def get_slide_layout(self, template_name: str, layout_type: str) -> Dict[str, Any]:
        """
        PPTX templates do not expose layout metadata here.
        """
        return {}

    def get_template_constraints(self, template_name: str) -> Dict[str, Any]:
        """
        PPTX templates do not enforce constraints at this layer.
        """
        return {}