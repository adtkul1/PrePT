"""
Template management and loading
- Supports PPTX/POTX templates stored directly under the templates directory
- Backward compatible with folder-based templates containing config.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional, List, Union

import yaml

from config import TEMPLATES_DIR


class TemplateManager:
    """Manages presentation templates"""

    def __init__(self, templates_dir: Optional[Path | str] = None):
        # Tests expect TemplateManager() to work with no args
        self.templates_dir = Path(templates_dir) if templates_dir else Path(TEMPLATES_DIR)
        self._templates_cache: Dict[str, Dict[str, Any]] = {}

    # ----------------------------
    # Helpers
    # ----------------------------
    def _is_branded_name(self, name: str) -> bool:
        """
        Heuristic detection of "branded" templates from name.
        Keeps it simple and future-friendly.
        """
        n = name.lower()
        return any(token in n for token in ("brand", "branded", "accenture", "acn", "corporate"))

    def _resolve_pptx_path(self, template_name: str) -> Optional[Path]:
        """
        Resolve a PPTX/POTX path from:
          - exact filename (e.g., 'corporate.pptx')
          - stem name (e.g., 'corporate' -> 'corporate.pptx' if exists)
        """
        # If user passed a filename with suffix
        direct = self.templates_dir / template_name
        if direct.is_file() and direct.suffix.lower() in {".pptx", ".potx"}:
            return direct

        # If user passed just the stem, try .pptx and .potx
        for ext in (".pptx", ".potx"):
            candidate = self.templates_dir / f"{template_name}{ext}"
            if candidate.exists() and candidate.is_file():
                return candidate

        return None

    # ----------------------------
    # Public API
    # ----------------------------
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """
        Get list of available templates.

        IMPORTANT: returns a list of dicts (not strings) because tests expect:
            [t.get('name', '') for t in templates]
        """
        if not self.templates_dir.exists():
            return []

        templates: List[Dict[str, Any]] = []

        # 1) Preferred format: pptx/potx templates directly in templates dir
        for item in self.templates_dir.iterdir():
            if item.is_file() and item.suffix.lower() in {".pptx", ".potx"}:
                branded = self._is_branded_name(item.name)
                templates.append(
                    {
                        "name": item.stem,
                        "file": item.name,
                        "path": str(item.resolve()),
                        "format": item.suffix.lower().lstrip("."),
                        "type": "pptx_template",
                        "branded": branded,
                        "is_branded": branded,  # include both keys for test robustness
                    }
                )

        # 2) Backward compatible: folder templates with config.yaml
        for item in self.templates_dir.iterdir():
            if item.is_dir() and (item / "config.yaml").exists():
                branded = self._is_branded_name(item.name)
                templates.append(
                    {
                        "name": item.name,
                        "path": str(item.resolve()),
                        "format": "folder",
                        "type": "folder_template",
                        "branded": branded,
                        "is_branded": branded,
                    }
                )

        return templates

    def load_template(self, template: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Accepts either:
        - template name string (e.g. "accenture_template")
        - template dict returned by get_available_templates()
        """
        # --- normalize BEFORE using as cache key ---
        if isinstance(template, dict):
            name = template.get("name") or ""
            if not name:
                # fallback from file/path if name missing
                if template.get("file"):
                    name = Path(template["file"]).stem
                elif template.get("path"):
                    name = Path(template["path"]).stem
            if not name:
                raise ValueError("Invalid template dict passed to load_template()")
        else:
            name = template

        if name in self._templates_cache:
            return self._templates_cache[name]

        # Try pptx first
        pptx_path = self._resolve_pptx_path(name)
        if pptx_path:
            branded = self._is_branded_name(pptx_path.name)
            template_config = {
                "name": pptx_path.stem,
                "file": pptx_path.name,
                "path": str(pptx_path.resolve()),
                "format": pptx_path.suffix.lower().lstrip("."),
                "type": "pptx_template",
                "branded": branded,
                "is_branded": branded,
            }
            self._templates_cache[name] = template_config
            return template_config

        # if required to use folder-based template, load config.yaml for future use
        template_path = self.templates_dir / name
        if not template_path.exists():
            raise ValueError(f"Template '{name}' not found")

        config_file = template_path / "config.yaml"
        if not config_file.exists():
            raise ValueError(f"Template config not found: {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            template_config = yaml.safe_load(f) or {}

        branded = self._is_branded_name(name)
        template_config["name"] = template_config.get("name", name)
        template_config["type"] = "folder_template"
        template_config["branded"] = branded
        template_config["is_branded"] = branded

        self._templates_cache[name] = template_config
        return template_config    
       

    def validate_template(self, template_config: Dict[str, Any]) -> bool:
        """
        Validate template structure.
        - pptx templates are valid if the file path exists
        - folder templates are valid if required keys exist (legacy)
        """
        ttype = template_config.get("type")

        if ttype == "pptx_template":
            p = template_config.get("path")
            return bool(p) and Path(p).exists()

        # legacy folder template validation
        required_keys = ["template", "theme", "slide_layouts", "constraints"]
        return all(key in template_config for key in required_keys)

    def get_slide_layout(self, template_name: str, layout_type: str) -> Dict[str, Any]:
        """
        Get specific slide layout.
        For PPTX templates (file-based), layout metadata isn't available here,
        so return {}.
        """
        config = self.load_template(template_name)
        if config.get("type") == "pptx_template":
            return {}
        return (config.get("slide_layouts") or {}).get(layout_type, {})

    def get_template_constraints(self, template_name: str) -> Dict[str, Any]:
        """
        Get template constraints.
        For PPTX templates (file-based), return {} by default.
        """
        config = self.load_template(template_name)
        if config.get("type") == "pptx_template":
            return {}
        return config.get("constraints", {})