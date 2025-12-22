from typing import Dict, List, Optional

from pydantic import BaseModel, HttpUrl


class ResearchRequest(BaseModel):
    repo_url: Optional[HttpUrl] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class ResearchModule(BaseModel):
    name: str
    description: str
    files: List[str]


class ResearchHighlight(BaseModel):
    title: str
    description: str
    reference: Optional[str] = None


class ResearchPrinciple(BaseModel):
    topic: str
    summary: str


class ResearchReport(BaseModel):
    repo_url: str
    modules: List[ResearchModule]
    highlights: List[ResearchHighlight]
    principles: List[ResearchPrinciple]
    summary: str


class ResearchResponse(BaseModel):
    report: ResearchReport


class PdfRequest(BaseModel):
    report: ResearchReport


class PdfResponse(BaseModel):
    task_id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict] = None

