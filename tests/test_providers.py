import pytest

from app.core.config import Settings
from app.providers.llm import get_llm


def test_get_llm_openai():
    settings = Settings(
        openai_api_key="test-key",
        llm_provider="openai",
        llm_model="gpt-4o-mini"
    )
    llm = get_llm(settings)
    assert llm is not None
    assert llm.model_name == "gpt-4o-mini"


def test_get_llm_openai_missing_key():
    settings = Settings(llm_provider="openai", openai_api_key=None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        get_llm(settings)


def test_get_llm_gemini():
    settings = Settings(
        gemini_api_key="test-key",
        llm_provider="gemini",
        llm_model="gemini-1.5-pro-latest"
    )
    llm = get_llm(settings)
    assert llm is not None


def test_get_llm_gemini_missing_key():
    settings = Settings(llm_provider="gemini", gemini_api_key=None)
    with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
        get_llm(settings)


def test_get_llm_openrouter():
    settings = Settings(
        openrouter_api_key="test-key",
        llm_provider="openrouter",
        llm_model="openrouter/auto"
    )
    llm = get_llm(settings)
    assert llm is not None


def test_get_llm_openrouter_missing_key():
    settings = Settings(llm_provider="openrouter", openrouter_api_key=None)
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY is required"):
        get_llm(settings)


def test_get_llm_unsupported_provider():
    settings = Settings(llm_provider="openai", openai_api_key="test")
    settings.llm_provider = "unsupported"  # type: ignore
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm(settings)

