import os

import pytest

from app.core.config import Settings, get_settings


def test_settings_from_env():
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL"] = "gpt-4o-mini"
    
    settings = Settings()
    
    assert settings.openai_api_key == "test-openai-key"
    assert settings.llm_provider == "openai"
    assert settings.llm_model == "gpt-4o-mini"


def test_settings_defaults():
    settings = Settings()
    
    assert settings.app_name == "github-repo-lens"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.log_level == "INFO"


def test_get_settings_cached():
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2


def test_settings_provider_validation():
    settings = Settings(llm_provider="openai")
    assert settings.llm_provider == "openai"
    
    settings = Settings(llm_provider="gemini")
    assert settings.llm_provider == "gemini"
    
    settings = Settings(llm_provider="openrouter")
    assert settings.llm_provider == "openrouter"

