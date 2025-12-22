"""PDF report generation service using ReportLab."""

from datetime import datetime
from pathlib import Path

import markdown
from loguru import logger
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFReportGenerator:
    """Generate PDF reports from analysis results."""

    def __init__(self, output_dir: Path):
        """Initialize PDF report generator.

        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(
            ParagraphStyle(
                "CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=20,
                textColor=colors.HexColor("#2c3e50"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                "CustomHeading2",
                parent=self.styles["Heading2"],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.HexColor("#34495e"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                "CustomBody",
                parent=self.styles["Normal"],
                fontSize=11,
                leading=16,
                spaceAfter=8,
            )
        )
        self.styles.add(
            ParagraphStyle(
                "CodeBlock",
                parent=self.styles["Code"],
                fontSize=9,
                leading=12,
                backColor=colors.HexColor("#f4f4f4"),
                leftIndent=10,
                rightIndent=10,
                spaceBefore=8,
                spaceAfter=8,
            )
        )

    def generate(
        self,
        analysis_result: dict,
        repo_url: str,
        project_name: str,
        output_filename: str | None = None,
    ) -> Path:
        """Generate PDF report from analysis results.

        Args:
            analysis_result: Analysis result data
            repo_url: GitHub repository URL
            project_name: Project name for the report
            output_filename: Optional custom output filename

        Returns:
            Path to generated PDF file
        """
        logger.info(f"Generating PDF report for {repo_url}")

        messages = analysis_result.get("messages", [])
        analysis_content = self._extract_analysis_content(messages)

        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{project_name}_{timestamp}.pdf"

        output_path = self.output_dir / output_filename

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = self._build_story(repo_url, project_name, analysis_content)
        doc.build(story)

        logger.info(f"PDF report generated successfully: {output_path}")
        return output_path

    def _extract_analysis_content(self, messages: list) -> str:
        """Extract analysis content from messages."""
        content_parts = []
        for message in messages:
            if hasattr(message, "content"):
                content = message.content
                if isinstance(content, str) and content.strip():
                    content_parts.append(content)
        return "\n\n".join(content_parts)

    def _build_story(
        self, repo_url: str, project_name: str, analysis_content: str
    ) -> list:
        """Build PDF story (content elements)."""
        story = []

        # Title
        story.append(
            Paragraph(f"{project_name} - Repository Analysis", self.styles["CustomTitle"])
        )
        story.append(Spacer(1, 10))

        # Metadata table
        meta_data = [
            ["Repository URL", repo_url],
            ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Analyzer", "GitHub Repository Lens"],
        ]
        meta_table = Table(meta_data, colWidths=[4 * cm, 12 * cm])
        meta_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#555555")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(meta_table)
        story.append(Spacer(1, 20))

        # Analysis content
        story.extend(self._parse_markdown_content(analysis_content))

        return story

    def _parse_markdown_content(self, content: str) -> list:
        """Parse markdown content into PDF elements."""
        elements = []

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 6))
                continue

            # Handle headers
            if line.startswith("### "):
                elements.append(
                    Paragraph(line[4:], self.styles["Heading3"])
                )
            elif line.startswith("## "):
                elements.append(
                    Paragraph(line[3:], self.styles["CustomHeading2"])
                )
            elif line.startswith("# "):
                elements.append(
                    Paragraph(line[2:], self.styles["Heading1"])
                )
            elif line.startswith("```"):
                continue
            elif line.startswith("- ") or line.startswith("* "):
                bullet_text = f"• {self._escape_html(line[2:])}"
                elements.append(Paragraph(bullet_text, self.styles["CustomBody"]))
            else:
                # Regular paragraph - escape HTML special chars
                safe_text = self._escape_html(line)
                # Handle inline code
                safe_text = self._format_inline_code(safe_text)
                # Handle bold
                safe_text = self._format_bold(safe_text)
                elements.append(Paragraph(safe_text, self.styles["CustomBody"]))

        return elements

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters for ReportLab."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def _format_inline_code(self, text: str) -> str:
        """Format inline code with monospace font."""
        import re
        return re.sub(
            r"`([^`]+)`",
            r'<font face="Courier" size="9" color="#c0392b">\1</font>',
            text,
        )

    def _format_bold(self, text: str) -> str:
        """Format bold text."""
        import re
        return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)


def create_pdf_generator(output_dir: Path) -> PDFReportGenerator:
    """Create a PDF report generator.

    Args:
        output_dir: Directory to save generated PDFs

    Returns:
        PDF report generator instance
    """
    return PDFReportGenerator(output_dir)
