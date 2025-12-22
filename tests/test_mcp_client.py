"""Tests for MCP client."""

import pytest

from app.config import Settings
from app.core.mcp_client import MCPClientManager


@pytest.mark.asyncio
async def test_mcp_client_initialization(test_settings: Settings):
    """Test MCP client initialization."""
    manager = MCPClientManager(test_settings)

    assert manager._client is None
    assert manager._tools is None


@pytest.mark.asyncio
async def test_mcp_client_get_tools_before_init(test_settings: Settings):
    """Test getting tools before initialization raises error."""
    manager = MCPClientManager(test_settings)

    with pytest.raises(RuntimeError, match="MCP client not initialized"):
        await manager.get_tools()


@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.config.getoption("--run-integration"),
    reason="Integration test - requires github-repo-mcp to be available",
)
async def test_mcp_client_integration(test_settings: Settings):
    """Integration test for MCP client (requires github-repo-mcp)."""
    async with MCPClientManager(test_settings) as manager:
        tools = await manager.get_tools()

        assert len(tools) > 0
        assert all(hasattr(tool, "name") for tool in tools)
        assert all(hasattr(tool, "description") for tool in tools)


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests",
    )
