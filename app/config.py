"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="github-repo-lens", description="Application name")
    host: str = Field(default="0.0.0.0", description="Host to bind")
    port: int = Field(default=8000, description="Port to bind")
    log_level: str = Field(default="INFO", description="Logging level")

    # LLM Provider
    llm_provider: Literal["openai", "gemini", "openrouter"] = Field(
        default="openai", description="LLM provider to use"
    )
    llm_model: str = Field(default="gpt-4o-mini", description="LLM model name")

    # OpenAI
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_base_url: str | None = Field(
        default=None, description="OpenAI base URL (optional)"
    )

    # Gemini
    gemini_api_key: str | None = Field(default=None, description="Gemini API key")

    # OpenRouter
    openrouter_api_key: str | None = Field(
        default=None, description="OpenRouter API key"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", description="OpenRouter base URL"
    )

    # GitHub Repository
    github_repo_url: str | None = Field(
        default=None, description="Default GitHub repository URL"
    )

    # MCP Server
    mcp_server: str = Field(default="github-repo-mcp", description="MCP server name")

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0", description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1", description="Celery result backend URL"
    )

    # Report Output
    report_output_dir: Path = Field(
        default=Path("/tmp/reports"), description="Report output directory"
    )

    @field_validator("report_output_dir", mode="before")
    @classmethod
    def ensure_path(cls, v: str | Path) -> Path:
        """Ensure report output directory is a Path."""
        path = Path(v) if isinstance(v, str) else v
        path.mkdir(parents=True, exist_ok=True)
        return path

    def validate_provider_config(self) -> None:
        """Validate that required API keys are set for the selected provider."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using openai provider")
        elif self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when using gemini provider")
        elif self.llm_provider == "openrouter" and not self.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when using openrouter provider"
            )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.validate_provider_config()
    return settings
