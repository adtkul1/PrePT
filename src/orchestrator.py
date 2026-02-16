import logging
from typing import Optional, List

from .content_mapper import ContentMapper, ValidationIssue
from .content_generator import ContentGenerator
from .template_manager import TemplateManager
from .presentation_builder import PresentationBuilder

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
        max_regen_attempts: int = 3,
    ):
        self.content_generator = content_generator or ContentGenerator()
        self.template_manager = template_manager or TemplateManager()
        self.presentation_builder_class = presentation_builder or PresentationBuilder
        self.content_mapper = content_mapper  # created per-run when constraints known
        self.branded_template_handler = branded_template_handler
        self.max_regen_attempts = max(1, int(max_regen_attempts))

    def generate(
        self,
        topic: str,
        num_slides: int,
        template_name: str = "corporate",
        audience: Optional[str] = None,
        tone: str = "professional",
        use_branded_template: bool = True,
    ) -> str:
        logger.info(f"Generating presentation: '{topic}' ({num_slides} slides)")

        # Load template (TemplateManager may ignore name depending on your implementation)
        template_config = self.template_manager.load_template(template_name)
        logger.info(f"Loaded template: {template_name}")

        # Template constraints (may be {} for pptx-only templates)
        constraints = self.template_manager.get_template_constraints(template_name)

        # Create validator/normalizer with constraints
        mapper = self.content_mapper or ContentMapper(template_constraints=constraints)

        feedback: Optional[str] = None
        outline = None

        # --- Regeneration loop ---
        for attempt in range(1, self.max_regen_attempts + 1):
            outline = self._generate_outline(topic, num_slides, audience, tone, constraints, feedback, attempt)

            normalized_slides = []
            all_issues: List[ValidationIssue] = []
            needs_regen = False

            for slide in outline.slides:
                normalized, issues, slide_needs_regen = mapper.assess_slide(slide)
                normalized_slides.append(normalized)
                all_issues.extend(issues)
                if slide_needs_regen:
                    needs_regen = True

            # Write back normalized slides (deterministic safety)
            outline.slides = normalized_slides

            if not needs_regen:
                logger.info(f"Validation passed (attempt {attempt}/{self.max_regen_attempts}).")
                break

            # Build feedback for next regen attempt
            feedback = self._format_feedback(all_issues, attempt)
            logger.warning(
                f"Validation failed; regenerating (attempt {attempt}/{self.max_regen_attempts}). "
                f"Issues: {len(all_issues)}"
            )

            # If last attempt, proceed with normalized slides anyway (robust output)
            if attempt == self.max_regen_attempts:
                logger.warning("Max regeneration attempts reached; proceeding with best-effort normalized content.")

        # Optional overall validation
        if outline is None:
            raise RuntimeError("Failed to generate outline (unexpected).")
        if not mapper.validate_presentation(outline):
            logger.warning("Presentation outline did not meet minimum validation criteria.")

        # Build presentation
        if use_branded_template and self.branded_template_handler is not None:
            from .branded_template import TemplateContentInjector
            prs = self.branded_template_handler.create_presentation_from_template()
            injector = TemplateContentInjector(self.branded_template_handler)
            prs = injector.inject_content(prs, outline.slides)
        else:
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

    # ----------------------------
    # Generation + feedback-aware regeneration
    # ----------------------------
    def _generate_outline(
        self,
        topic: str,
        num_slides: int,
        audience: Optional[str],
        tone: str,
        constraints: dict,
        feedback: Optional[str],
        attempt: int,
    ):
        """
        Generate outline.
        - If feedback is present and generator supports feedback-aware regeneration, use it.
        - Else call the generator's public API.
        """
        if feedback and self._supports_feedback_regen(self.content_generator):
            return self._regen_with_feedback(topic, num_slides, audience, tone, constraints, feedback, attempt)

        return self.content_generator.generate_presentation_outline(
            topic=topic,
            num_slides=num_slides,
            audience=audience,
            tone=tone,
            template_constraints=constraints,
        )

    def _supports_feedback_regen(self, gen: ContentGenerator) -> bool:
        """
        Feature detection: we don't assume internals exist, we check for common helpers.
        This keeps things future-proof even if you swap generator implementations.
        """
        return all(
            hasattr(gen, attr)
            for attr in ("_build_system_prompt", "_build_user_prompt", "_call_api", "_parse_outline_response")
        )

    def _regen_with_feedback(
        self,
        topic: str,
        num_slides: int,
        audience: Optional[str],
        tone: str,
        constraints: dict,
        feedback: str,
        attempt: int,
    ):
        """
        Feedback-aware regeneration:
        - Reuses generator's system/user prompts
        - Injects validator feedback and asks for corrected JSON
        """
        gen = self.content_generator

        system_prompt = gen._build_system_prompt(tone, constraints)

        user_prompt = gen._build_user_prompt(topic, num_slides, audience)
        user_prompt += (
            "\n\nREGENERATION REQUEST:\n"
            "Your previous JSON output violated constraints and/or structure.\n"
            "Fix the issues listed below and return ONLY valid JSON.\n"
            "Do not include any extra commentary.\n\n"
            f"Validation feedback (attempt {attempt}):\n{feedback}\n"
        )

        raw = gen._call_api(system_prompt, user_prompt)
        # generator already handles JSON extraction in its public method,
        # but here we want to keep it consistent:
        import json
        try:
            data = json.loads(raw)
        except Exception:
            data = gen._extract_json_from_response(raw) if hasattr(gen, "_extract_json_from_response") else json.loads(
                raw[raw.find("{"): raw.rfind("}") + 1]
            )
        return gen._parse_outline_response(data)

    def _format_feedback(self, issues: List[ValidationIssue], attempt: int) -> str:
        """
        Convert issues into a compact instruction set for the model.
        """
        # Deduplicate messages to avoid prompt bloat
        seen = set()
        lines = []
        for iss in issues:
            key = (iss.severity, iss.code, iss.message)
            if key in seen:
                continue
            seen.add(key)
            prefix = "MUST FIX" if iss.severity == "hard" else "SHOULD FIX"
            lines.append(f"- {prefix} [{iss.code}] {iss.message}")
        # Add a reminder of the core contract
        lines.append("- MUST RETURN: valid JSON only (no markdown, no prose).")
        lines.append("- MUST RESPECT: title/subtitle/bullet length limits and bullet count constraints.")
        return "\n".join(lines)