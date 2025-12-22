"""API request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRequest(BaseModel):
    """Request schema for repository analysis."""

    repo_url: HttpUrl = Field(..., description="GitHub repository URL")
    llm_provider: Literal["openai", "gemini", "openrouter"] | None = Field(
        None, description="Override default LLM provider"
    )
    llm_model: str | None = Field(None, description="Override default LLM model")


class AnalyzeResponse(BaseModel):
    """Response schema for analysis initiation."""

    task_id: str = Field(..., description="Analysis task ID for SSE streaming")
    repo_url: str = Field(..., description="Repository URL being analyzed")
    status: str = Field(..., description="Initial status")
    stream_url: str = Field(..., description="SSE stream endpoint URL")


class PDFReportRequest(BaseModel):
    """Request schema for PDF report generation."""

    analysis_result: dict = Field(..., description="Analysis result data")
    repo_url: HttpUrl = Field(..., description="GitHub repository URL")
    project_name: str | None = Field(None, description="Project name for report")


class PDFReportResponse(BaseModel):
    """Response schema for PDF report generation."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status")
    status_url: str = Field(..., description="URL to check task status")


class PDFReportStatus(BaseModel):
    """Response schema for PDF report status."""

    task_id: str = Field(..., description="Celery task ID")
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        ..., description="Task status"
    )
    progress: int | None = Field(None, description="Progress percentage (0-100)")
    download_url: str | None = Field(None, description="PDF download URL if completed")
    error: str | None = Field(None, description="Error message if failed")
    created_at: datetime | None = Field(None, description="Task creation timestamp")
    completed_at: datetime | None = Field(None, description="Task completion timestamp")


class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    llm_provider: str = Field(..., description="Configured LLM provider")
    llm_model: str = Field(..., description="Configured LLM model")
