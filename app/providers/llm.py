from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from loguru import logger

from app.core.config import Settings


def get_llm(settings: Settings) -> Any:
    provider = settings.llm_provider.lower()
    model_name = settings.llm_model

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for provider 'openai'")
        logger.info("Using OpenAI provider with model {}", model_name or "gpt-4o-mini")
        return ChatOpenAI(
            model=model_name or "gpt-4o-mini",
            api_key=settings.openai_api_key,
            base_url=str(settings.openai_base_url) if settings.openai_base_url else None,
        )

    if provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required for provider 'openrouter'")
        logger.info("Using OpenRouter provider with model {}", model_name or "openrouter/auto")
        return ChatOpenAI(
            model=model_name or "openrouter/auto",
            api_key=settings.openrouter_api_key,
            base_url=str(settings.openrouter_base_url),
        )

    if provider == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required for provider 'gemini'")
        logger.info("Using Gemini provider with model {}", model_name or "gemini-1.5-pro-latest")
        return ChatGoogleGenerativeAI(
            model=model_name or "gemini-1.5-pro-latest",
            google_api_key=settings.gemini_api_key,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")

