"""Tests for prompt management."""

import pytest

from app.prompts.base import PromptLoader, PromptTemplate


def test_prompt_template_render():
    """Test prompt template rendering."""
    template = PromptTemplate(
        name="test",
        version="1.0",
        template="Hello {{ name }}!",
        variables=["name"],
    )

    result = template.render(name="World")
    assert result == "Hello World!"


def test_prompt_template_missing_variable():
    """Test prompt template with missing variable raises error."""
    template = PromptTemplate(
        name="test",
        version="1.0",
        template="Hello {{ name }}!",
        variables=["name"],
    )

    with pytest.raises(ValueError, match="Missing required variables"):
        template.render()


def test_prompt_loader_load_system():
    """Test loading system prompt template."""
    loader = PromptLoader()
    template = loader.load("system")

    assert template.name == "system_prompt"
    assert "repo_url" in template.variables


def test_prompt_loader_load_analysis():
    """Test loading analysis prompt template."""
    loader = PromptLoader()
    template = loader.load("analysis")

    assert template.name == "analysis_prompt"
    assert "repo_url" in template.variables


def test_prompt_loader_render():
    """Test prompt loader render method."""
    loader = PromptLoader()
    result = loader.render(
        "system", repo_url="https://github.com/test-user/test-repo"
    )

    assert "https://github.com/test-user/test-repo" in result
    assert "GitHub repository analyst" in result


def test_prompt_loader_cache():
    """Test prompt loader caching."""
    loader = PromptLoader()

    # Load template twice
    template1 = loader.load("system")
    template2 = loader.load("system")

    # Should be the same object (cached)
    assert template1 is template2


def test_prompt_loader_clear_cache():
    """Test clearing prompt loader cache."""
    loader = PromptLoader()

    # Load and cache template
    template1 = loader.load("system")
    loader.clear_cache()

    # Load again after clearing cache
    template2 = loader.load("system")

    # Should be different objects
    assert template1 is not template2


def test_prompt_loader_file_not_found():
    """Test loading non-existent template raises error."""
    loader = PromptLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("nonexistent")
