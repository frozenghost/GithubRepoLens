import pytest
from unittest.mock import AsyncMock, MagicMock

from app.graph.research_graph import ResearchState, build_research_graph


@pytest.mark.asyncio
async def test_build_research_graph():
    llm = MagicMock()
    mcp_client = MagicMock()
    
    graph = build_research_graph(llm, mcp_client)
    
    assert graph is not None
    assert "fetch_files" in graph.nodes
    assert "analyze" in graph.nodes


@pytest.mark.asyncio
async def test_research_state_structure():
    state: ResearchState = {
        "repo_url": "https://github.com/test/repo",
        "files": ["file1.py", "file2.py"],
        "report": None
    }
    
    assert state["repo_url"] == "https://github.com/test/repo"
    assert len(state["files"]) == 2
    assert state["report"] is None

