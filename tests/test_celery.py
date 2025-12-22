import pytest
from pathlib import Path
from unittest.mock import patch

from app.tasks.pdf import generate_pdf


@patch("app.tasks.pdf.get_settings")
def test_generate_pdf_task(mock_get_settings, tmp_path):
    mock_settings = type('Settings', (), {
        'report_output_dir': tmp_path
    })()
    mock_get_settings.return_value = mock_settings
    
    report = {
        "repo_url": "https://github.com/test/repo",
        "modules": [
            {"name": "Module1", "description": "Test module", "files": ["file1.py"]}
        ],
        "highlights": [
            {"title": "Highlight1", "description": "Test highlight", "reference": None}
        ],
        "principles": [
            {"topic": "Principle1", "summary": "Test principle"}
        ],
        "summary": "Test summary"
    }
    
    result = generate_pdf(report)
    
    assert result is not None
    assert str(tmp_path) in result
    assert Path(result).exists()


def test_celery_app_config():
    from app.tasks.celery_app import celery_app
    
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.result_serializer == "json"

