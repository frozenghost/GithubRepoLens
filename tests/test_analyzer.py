"""Tests for repository analyzer."""

import pytest

from app.config import Settings
from app.services.analyzer import RepositoryAnalyzer


@pytest.mark.asyncio
async def test_analyzer_initialization(test_settings: Settings):
    """Test analyzer initialization."""
    analyzer = RepositoryAnalyzer(test_settings)

    assert analyzer._agent is None
    assert analyzer._mcp_client is None


@pytest.mark.asyncio
async def test_analyzer_analyze_before_init(
    test_settings: Settings, mock_repo_url: str
):
    """Test analyzing before initialization raises error."""
    analyzer = RepositoryAnalyzer(test_settings)

    with pytest.raises(RuntimeError, match="Analyzer not initialized"):
        await analyzer.analyze(mock_repo_url)


@pytest.mark.asyncio
async def test_analyzer_stream_before_init(
    test_settings: Settings, mock_repo_url: str
):
    """Test streaming before initialization raises error."""
    analyzer = RepositoryAnalyzer(test_settings)

    with pytest.raises(RuntimeError, match="Analyzer not initialized"):
        async for _ in analyzer.stream_analysis(mock_repo_url):
            pass


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.config.getoption("--run-integration", default=False),
    reason="Integration test - requires API keys and MCP server",
)
async def test_analyzer_integration(test_settings: Settings, mock_repo_url: str):
    """Integration test for analyzer (requires API keys and MCP)."""
    async with RepositoryAnalyzer(test_settings) as analyzer:
        # Test that analyzer is initialized
        assert analyzer._agent is not None
        assert analyzer._mcp_client is not None
