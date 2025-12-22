"""Prompt loading and management utilities."""

from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template
from pydantic import BaseModel, Field


class PromptTemplate(BaseModel):
    """Prompt template model."""

    name: str = Field(..., description="Prompt name")
    version: str = Field(..., description="Prompt version")
    description: str | None = Field(None, description="Prompt description")
    template: str = Field(..., description="Jinja2 template string")
    variables: list[str] = Field(default_factory=list, description="Required variables")

    def render(self, **kwargs: Any) -> str:
        """Render the template with provided variables."""
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        jinja_template = Template(self.template)
        return jinja_template.render(**kwargs)


class PromptLoader:
    """Load and manage prompt templates from YAML files."""

    def __init__(self, templates_dir: Path | str | None = None):
        """Initialize prompt loader.

        Args:
            templates_dir: Directory containing prompt template YAML files.
                          Defaults to app/prompts/templates.
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        self.templates_dir = Path(templates_dir)
        self._cache: dict[str, PromptTemplate] = {}

    def load(self, template_name: str) -> PromptTemplate:
        """Load a prompt template by name.

        Args:
            template_name: Name of the template file (without .yaml extension)

        Returns:
            Loaded prompt template

        Raises:
            FileNotFoundError: If template file doesn't exist
            ValueError: If template YAML is invalid
        """
        if template_name in self._cache:
            return self._cache[template_name]

        template_path = self.templates_dir / f"{template_name}.yaml"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        template = PromptTemplate(**data)
        self._cache[template_name] = template
        return template

    def render(self, template_name: str, **kwargs: Any) -> str:
        """Load and render a template in one step.

        Args:
            template_name: Name of the template file (without .yaml extension)
            **kwargs: Variables to pass to the template

        Returns:
            Rendered prompt string
        """
        template = self.load(template_name)
        return template.render(**kwargs)

    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._cache.clear()


# Global prompt loader instance
_prompt_loader: PromptLoader | None = None


def get_prompt_loader() -> PromptLoader:
    """Get the global prompt loader instance."""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader()
    return _prompt_loader
