from pathlib import Path
from typing import Dict

from fpdf import FPDF
from loguru import logger

from app.core.config import get_settings
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.pdf.generate_pdf")
def generate_pdf(report: Dict) -> str:
    settings = get_settings()
    output_dir = Path(settings.report_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "report.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Repository: {report.get('repo_url', '')}")

    pdf.ln()
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(0, 10, "Modules", ln=True)
    pdf.set_font("Arial", size=11)
    for module in report.get("modules", []):
        pdf.multi_cell(0, 8, txt=f"- {module.get('name')}: {module.get('description')}")

    pdf.ln()
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(0, 10, "Highlights", ln=True)
    pdf.set_font("Arial", size=11)
    for highlight in report.get("highlights", []):
        pdf.multi_cell(0, 8, txt=f"- {highlight.get('title')}: {highlight.get('description')}")

    pdf.ln()
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(0, 10, "Principles", ln=True)
    pdf.set_font("Arial", size=11)
    for principle in report.get("principles", []):
        pdf.multi_cell(0, 8, txt=f"- {principle.get('topic')}: {principle.get('summary')}")

    pdf.ln()
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(0, 10, "Summary", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=report.get("summary", ""))

    pdf.output(str(pdf_path))
    logger.info("Generated PDF at {}", pdf_path)
    return str(pdf_path)

