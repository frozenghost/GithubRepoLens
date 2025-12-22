from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "github-repo-lens"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    llm_provider: Literal["openai", "gemini", "openrouter"] = "openai"
    llm_model: Optional[str] = None

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: Optional[HttpUrl] = Field(default=None, alias="OPENAI_BASE_URL")
    openrouter_api_key: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    openrouter_base_url: Optional[HttpUrl] = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")

    github_repo_url: Optional[HttpUrl] = Field(default=None, alias="GITHUB_REPO_URL")
    mcp_server: str = "github-repo-mcp"

    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    report_output_dir: Path = Path("/tmp/reports")

    class Config:
        env_prefix = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()

