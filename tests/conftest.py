"""Pytest configuration and fixtures."""

import os
from pathlib import Path

import pytest

from app.config import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with mock values."""
    return Settings(
        app_name="test-github-repo-lens",
        host="127.0.0.1",
        port=8001,
        log_level="DEBUG",
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY", "test-api-key"),
        celery_broker_url="redis://localhost:6379/0",
        celery_result_backend="redis://localhost:6379/1",
        report_output_dir=Path("/tmp/test_reports"),
    )


@pytest.fixture
def mock_repo_url() -> str:
    """Mock GitHub repository URL."""
    return "https://github.com/test-user/test-repo"


@pytest.fixture
def mock_analysis_result() -> dict:
    """Mock analysis result."""
    return {
        "messages": [
            {"role": "user", "content": "Analyze repository"},
            {
                "role": "assistant",
                "content": "# Analysis Result\n\nThis is a test analysis.",
            },
        ],
        "repo_url": "https://github.com/test-user/test-repo",
        "analysis_stage": "completed",
    }
