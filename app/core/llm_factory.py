"""LLM factory for multi-provider support."""

from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from loguru import logger

from app.config import Settings


class LLMFactory:
    """Factory for creating LLM instances based on provider."""

    @staticmethod
    def create(
        provider: Literal["openai", "gemini", "openrouter"],
        model: str,
        settings: Settings,
        **kwargs,
    ) -> BaseChatModel:
        """Create an LLM instance based on provider.

        Args:
            provider: LLM provider name
            model: Model name/identifier
            settings: Application settings
            **kwargs: Additional arguments to pass to the LLM constructor

        Returns:
            Configured LLM instance

        Raises:
            ValueError: If provider is not supported or configuration is invalid
        """
        logger.info(f"Creating LLM instance: provider={provider}, model={model}")

        match provider:
            case "openai":
                return LLMFactory._create_openai(model, settings, **kwargs)
            case "gemini":
                return LLMFactory._create_gemini(model, settings, **kwargs)
            case "openrouter":
                return LLMFactory._create_openrouter(model, settings, **kwargs)
            case _:
                raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def _create_openai(model: str, settings: Settings, **kwargs) -> ChatOpenAI:
        """Create OpenAI LLM instance."""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")

        config = {
            "model": model,
            "api_key": settings.openai_api_key,
            "temperature": kwargs.get("temperature", 0.7),
            "streaming": kwargs.get("streaming", True),
        }

        if settings.openai_base_url:
            config["base_url"] = settings.openai_base_url

        logger.debug(f"OpenAI config: {config}")
        return ChatOpenAI(**config)

    @staticmethod
    def _create_gemini(
        model: str, settings: Settings, **kwargs
    ) -> ChatGoogleGenerativeAI:
        """Create Gemini LLM instance."""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini provider")

        config = {
            "model": model,
            "google_api_key": settings.gemini_api_key,
            "temperature": kwargs.get("temperature", 0.7),
            "streaming": kwargs.get("streaming", True),
        }

        logger.debug(f"Gemini config: {config}")
        return ChatGoogleGenerativeAI(**config)

    @staticmethod
    def _create_openrouter(model: str, settings: Settings, **kwargs) -> ChatOpenAI:
        """Create OpenRouter LLM instance (uses OpenAI-compatible API)."""
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required for OpenRouter provider")

        config = {
            "model": model,
            "api_key": settings.openrouter_api_key,
            "base_url": settings.openrouter_base_url,
            "temperature": kwargs.get("temperature", 0.7),
            "streaming": kwargs.get("streaming", True),
        }

        logger.debug(f"OpenRouter config: {config}")
        return ChatOpenAI(**config)


def create_llm_from_settings(settings: Settings, **kwargs) -> BaseChatModel:
    """Create LLM instance from application settings.

    Args:
        settings: Application settings
        **kwargs: Additional arguments to pass to the LLM constructor

    Returns:
        Configured LLM instance
    """
    return LLMFactory.create(
        provider=settings.llm_provider,
        model=settings.llm_model,
        settings=settings,
        **kwargs,
    )
