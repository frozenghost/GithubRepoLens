"""API routes for GitHub repository analysis."""

import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from loguru import logger

from app import __version__
from app.api.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    HealthResponse,
    PDFReportRequest,
    PDFReportResponse,
    PDFReportStatus,
)
from app.config import get_settings
from app.services.analyzer import create_analyzer
from app.tasks.celery_tasks import generate_pdf_report_task

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=__version__,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
    )


@router.post("/analyze")
async def analyze_repository(request: AnalyzeRequest) -> StreamingResponse:
    """Analyze repository and stream progress via SSE.

    Args:
        request: Analysis request with repository URL and language

    Returns:
        SSE streaming response with real-time analysis progress
    """
    repo_url = str(request.repo_url)
    language = request.language
    logger.info(f"Starting analysis for {repo_url} (language: {language})")

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events from analysis stream."""
        try:
            async with create_analyzer() as analyzer:
                async for event in analyzer.stream_analysis(repo_url, language=language):
                    yield event.to_sse_format()
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            error_event = {
                "type": "error",
                "data": {"error": str(e)},
            }
            yield f"data: {error_event}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering for nginx
        },
    )


@router.post("/report/pdf", response_model=PDFReportResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_pdf_report(request: PDFReportRequest) -> PDFReportResponse:
    """Generate PDF report from analysis results (async via Celery).

    Args:
        request: PDF report generation request

    Returns:
        PDF report response with task ID
    """
    repo_url = str(request.repo_url)
    project_name = request.project_name or repo_url.split("/")[-1]

    logger.info(f"Submitting PDF generation task for {repo_url}")

    # Submit Celery task
    task = generate_pdf_report_task.delay(
        analysis_result=request.analysis_result,
        repo_url=repo_url,
        project_name=project_name,
    )

    logger.info(f"PDF generation task submitted: {task.id}")

    return PDFReportResponse(
        task_id=task.id,
        status="pending",
        status_url=f"/api/report/pdf/{task.id}",
    )


@router.get("/report/pdf/{task_id}", response_model=PDFReportStatus)
async def get_pdf_report_status(task_id: str) -> PDFReportStatus:
    """Get PDF report generation status.

    Args:
        task_id: Celery task ID

    Returns:
        PDF report status

    Raises:
        HTTPException: If task not found
    """
    from celery.result import AsyncResult

    task = AsyncResult(task_id)

    if task.state == "PENDING":
        return PDFReportStatus(
            task_id=task_id,
            status="pending",
            progress=0,
        )
    elif task.state == "PROGRESS":
        return PDFReportStatus(
            task_id=task_id,
            status="processing",
            progress=task.info.get("progress", 0) if task.info else 0,
        )
    elif task.state == "SUCCESS":
        result = task.result
        return PDFReportStatus(
            task_id=task_id,
            status="completed",
            progress=100,
            download_url=result.get("download_url"),
            completed_at=result.get("completed_at"),
        )
    elif task.state == "FAILURE":
        return PDFReportStatus(
            task_id=task_id,
            status="failed",
            error=str(task.info),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
