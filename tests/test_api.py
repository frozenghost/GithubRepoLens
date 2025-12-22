import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import create_app
from app.models import ResearchReport


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 404


@patch("app.api.research.run_research")
def test_run_analysis_endpoint(mock_run_research, client):
    mock_report = ResearchReport(
        repo_url="https://github.com/test/repo",
        modules=[],
        highlights=[],
        principles=[],
        summary="Test summary"
    )
    mock_run_research.return_value = mock_report
    
    response = client.post(
        "/research/run",
        json={"repo_url": "https://github.com/test/repo"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "report" in data


def test_run_analysis_missing_repo_url(client):
    response = client.post("/research/run", json={})
    assert response.status_code == 400


@patch("app.api.research.generate_pdf")
def test_enqueue_pdf_endpoint(mock_generate_pdf, client):
    mock_task = AsyncMock()
    mock_task.id = "test-task-id"
    mock_generate_pdf.delay.return_value = mock_task
    
    response = client.post(
        "/research/pdf",
        json={
            "report": {
                "repo_url": "https://github.com/test/repo",
                "modules": [],
                "highlights": [],
                "principles": [],
                "summary": "Test"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-task-id"

