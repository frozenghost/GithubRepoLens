"""Celery tasks for asynchronous processing."""

from datetime import datetime
from pathlib import Path

from celery import Celery, Task
from loguru import logger

from app.config import get_settings
from app.services.pdf_generator import create_pdf_generator

# Initialize Celery
settings = get_settings()
celery_app = Celery(
    "githubrepolens",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
)


class CallbackTask(Task):
    """Base task with callbacks for progress tracking."""

    def on_success(self, retval, task_id, args, kwargs):
        """Success callback."""
        logger.info(f"Task {task_id} completed successfully")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback."""
        logger.error(f"Task {task_id} failed: {exc}")


@celery_app.task(bind=True, base=CallbackTask, name="generate_pdf_report")
def generate_pdf_report_task(
    self,
    analysis_result: dict,
    repo_url: str,
    project_name: str,
) -> dict:
    """Generate PDF report from analysis results.

    Args:
        self: Task instance (bound)
        analysis_result: Analysis result data
        repo_url: GitHub repository URL
        project_name: Project name

    Returns:
        Task result with download URL and metadata
    """
    task_id = self.request.id
    logger.info(f"Starting PDF generation task {task_id} for {repo_url}")

    try:
        # Update task state to PROGRESS
        self.update_state(
            state="PROGRESS",
            meta={"progress": 10, "status": "Initializing PDF generator"},
        )

        # Create PDF generator
        pdf_generator = create_pdf_generator(settings.report_output_dir)

        self.update_state(
            state="PROGRESS",
            meta={"progress": 30, "status": "Generating report content"},
        )

        # Generate PDF
        output_filename = f"{project_name}_{task_id}.pdf"
        pdf_path = pdf_generator.generate(
            analysis_result=analysis_result,
            repo_url=repo_url,
            project_name=project_name,
            output_filename=output_filename,
        )

        self.update_state(
            state="PROGRESS",
            meta={"progress": 90, "status": "Finalizing PDF"},
        )

        # Prepare result
        result = {
            "task_id": task_id,
            "repo_url": repo_url,
            "project_name": project_name,
            "pdf_path": str(pdf_path),
            "download_url": f"/api/v1/report/download/{output_filename}",
            "completed_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"PDF generation task {task_id} completed: {pdf_path}")
        return result

    except Exception as e:
        logger.error(f"PDF generation task {task_id} failed: {e}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)},
        )
        raise


@celery_app.task(name="cleanup_old_reports")
def cleanup_old_reports_task(days: int = 7) -> dict:
    """Clean up old PDF reports.

    Args:
        days: Delete reports older than this many days

    Returns:
        Cleanup statistics
    """
    logger.info(f"Starting cleanup of reports older than {days} days")

    try:
        report_dir = Path(settings.report_output_dir)
        if not report_dir.exists():
            return {"deleted": 0, "error": "Report directory does not exist"}

        cutoff_time = datetime.now().timestamp() - (days * 86400)
        deleted_count = 0

        for pdf_file in report_dir.glob("*.pdf"):
            if pdf_file.stat().st_mtime < cutoff_time:
                pdf_file.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old report: {pdf_file}")

        logger.info(f"Cleanup completed: {deleted_count} reports deleted")
        return {"deleted": deleted_count, "days": days}

    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        return {"deleted": 0, "error": str(e)}
