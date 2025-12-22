"""Tests for LLM factory."""

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.core.llm_factory import LLMFactory, create_llm_from_settings


def test_create_openai_llm(test_settings: Settings):
    """Test creating OpenAI LLM."""
    test_settings.llm_provider = "openai"
    test_settings.openai_api_key = "test-key"

    llm = LLMFactory.create("openai", "gpt-4o-mini", test_settings)

    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "gpt-4o-mini"


def test_create_gemini_llm(test_settings: Settings):
    """Test creating Gemini LLM."""
    test_settings.llm_provider = "gemini"
    test_settings.gemini_api_key = "test-key"

    llm = LLMFactory.create("gemini", "gemini-pro", test_settings)

    assert isinstance(llm, ChatGoogleGenerativeAI)
    assert llm.model == "gemini-pro"


def test_create_openrouter_llm(test_settings: Settings):
    """Test creating OpenRouter LLM."""
    test_settings.llm_provider = "openrouter"
    test_settings.openrouter_api_key = "test-key"

    llm = LLMFactory.create("openrouter", "openai/gpt-4", test_settings)

    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "openai/gpt-4"


def test_create_llm_missing_api_key(test_settings: Settings):
    """Test creating LLM with missing API key raises error."""
    test_settings.openai_api_key = None

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        LLMFactory.create("openai", "gpt-4o-mini", test_settings)


def test_create_llm_unsupported_provider(test_settings: Settings):
    """Test creating LLM with unsupported provider raises error."""
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        LLMFactory.create("unsupported", "model", test_settings)


def test_create_llm_from_settings(test_settings: Settings):
    """Test creating LLM from settings."""
    test_settings.llm_provider = "openai"
    test_settings.llm_model = "gpt-4o-mini"
    test_settings.openai_api_key = "test-key"

    llm = create_llm_from_settings(test_settings)

    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "gpt-4o-mini"
