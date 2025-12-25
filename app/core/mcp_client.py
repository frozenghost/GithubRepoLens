"""MCP client setup for github-repo-mcp integration."""

import sys
from typing import Any

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from loguru import logger

from app.config import Settings


class MCPClientManager:
    """Manager for MCP client connections."""

    def __init__(self, settings: Settings):
        """Initialize MCP client manager.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._client: MultiServerMCPClient | None = None
        self._tools: list[BaseTool] | None = None

    async def initialize(self) -> None:
        """Initialize MCP client and load tools."""
        if self._client is not None:
            logger.warning("MCP client already initialized")
            return

        logger.info("Initializing MCP client for github-repo-mcp")

        # Prepare environment variables for github-repo-mcp
        server_config_base = {
            "transport": "stdio",
        }
        if self.settings.github_token:
            server_config_base["env"] = {"GITHUB_TOKEN": self.settings.github_token}

        # Configure github-repo-mcp server based on platform
        if sys.platform == "win32":
            server_config = {
                "command": "cmd",
                "args": ["/c", "npx", "-y", "github-repo-mcp"],
                **server_config_base,
            }
        else:
            server_config = {
                "command": "npx",
                "args": ["-y", "github-repo-mcp"],
                **server_config_base,
            }

        logger.debug(f"MCP server config: {server_config}")

        # Create MultiServerMCPClient
        self._client = MultiServerMCPClient(
            {self.settings.mcp_server: server_config}
        )

        # Load tools from MCP server
        try:
            self._tools = await self._client.get_tools()
            logger.info(f"Loaded {len(self._tools)} tools from MCP server")
            for tool in self._tools:
                logger.debug(f"  - {tool.name}: {tool.description}")
        except Exception as e:
            logger.error(f"Failed to load MCP tools: {e}")
            raise

    async def get_tools(self) -> list[BaseTool]:
        """Get loaded MCP tools.

        Returns:
            List of MCP tools

        Raises:
            RuntimeError: If client is not initialized
        """
        if self._tools is None:
            raise RuntimeError("MCP client not initialized. Call initialize() first.")
        return self._tools

    async def close(self) -> None:
        """Close MCP client connections."""
        if self._client is not None:
            logger.info("Closing MCP client")
            # Note: MultiServerMCPClient doesn't have explicit close method
            # but we can set references to None for cleanup
            self._tools = None
            self._client = None

    async def __aenter__(self) -> "MCPClientManager":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()


async def create_mcp_client(settings: Settings) -> MCPClientManager:
    """Create and initialize MCP client manager.

    Args:
        settings: Application settings

    Returns:
        Initialized MCP client manager
    """
    manager = MCPClientManager(settings)
    await manager.initialize()
    return manager
