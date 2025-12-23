"""Repository analyzer service with SSE streaming support."""

import json
from datetime import datetime
from typing import AsyncGenerator

from loguru import logger

from app.config import Settings, get_settings
from app.core.agent import create_analysis_agent
from app.core.llm_factory import create_llm_from_settings
from app.core.mcp_client import create_mcp_client


class AnalysisEvent:
    """Analysis event for SSE streaming."""

    def __init__(
        self,
        event_type: str,
        data: dict,
        timestamp: datetime | None = None,
    ):
        """Initialize analysis event.

        Args:
            event_type: Type of event (e.g., 'progress', 'tool_call', 'result')
            data: Event data
            timestamp: Event timestamp (defaults to now)
        """
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()

    def to_sse_format(self) -> str:
        """Convert event to SSE format.

        Returns:
            SSE-formatted string
        """
        event_data = {
            "type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }
        return f"data: {json.dumps(event_data)}\n\n"


class RepositoryAnalyzer:
    """Service for analyzing GitHub repositories."""

    def __init__(self, settings: Settings | None = None):
        """Initialize repository analyzer.

        Args:
            settings: Application settings (defaults to global settings)
        """
        self.settings = settings or get_settings()
        self._mcp_client = None
        self._agent = None

    async def initialize(self) -> None:
        """Initialize analyzer components."""
        if self._agent is not None:
            logger.warning("Analyzer already initialized")
            return

        logger.info("Initializing repository analyzer")

        # Create LLM
        llm = create_llm_from_settings(self.settings)
        logger.info(f"LLM created: {self.settings.llm_provider}/{self.settings.llm_model}")

        # Create and initialize MCP client
        self._mcp_client = await create_mcp_client(self.settings)
        tools = await self._mcp_client.get_tools()
        logger.info(f"MCP client initialized with {len(tools)} tools")

        # Create analysis agent
        self._agent = create_analysis_agent(llm=llm, tools=tools)
        logger.info("Analysis agent created")

    async def analyze(self, repo_url: str) -> dict:
        """Analyze a GitHub repository.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Analysis results

        Raises:
            RuntimeError: If analyzer is not initialized
        """
        if self._agent is None:
            raise RuntimeError("Analyzer not initialized. Call initialize() first.")

        logger.info(f"Starting analysis for {repo_url}")
        result = await self._agent.analyze_async(repo_url)
        logger.info(f"Analysis completed for {repo_url}")

        return result

    async def stream_analysis(
        self, repo_url: str, language: str = "en"
    ) -> AsyncGenerator[AnalysisEvent, None]:
        """Stream analysis progress in real-time.

        Args:
            repo_url: GitHub repository URL
            language: Analysis report language (en, zh, ja, etc.)

        Yields:
            Analysis events

        Raises:
            RuntimeError: If analyzer is not initialized
        """
        if self._agent is None:
            raise RuntimeError("Analyzer not initialized. Call initialize() first.")

        logger.info(f"Starting streaming analysis for {repo_url} (language: {language})")

        # Send start event
        yield AnalysisEvent(
            event_type="start",
            data={"repo_url": repo_url, "status": "started"},
        )

        try:
            # Stream analysis events
            async for event in self._agent.stream_analysis(repo_url, language=language):
                event_type = event.get("type")
                
                # Token-level streaming from LLM
                if event_type == "token":
                    content = event.get("content", "")
                    if content:
                        yield AnalysisEvent(
                            event_type="token",
                            data={"content": content},
                        )
                
                # Tool calls
                elif event_type == "tool_calls":
                    tool_calls = event.get("tool_calls", [])
                    for tool_call in tool_calls:
                        tool_name = tool_call.get("name")
                        args = tool_call.get("args", {})
                        
                        if tool_name == "read_file" and "path" in args:
                            message = f"IsAnalyzingFile {args['path']}"
                        elif tool_name == "list_directory" and "path" in args:
                            message = f"IsListingDirectory {args['path']}"
                        elif tool_name == "get_repo_structure":
                            message = f"IsGettingRepoStructure"
                        else:
                            message = f"IsExecuting {tool_name}"
                        
                        yield AnalysisEvent(
                            event_type="tool_call",
                            data={
                                "message": message,
                                "tool": tool_name,
                            },
                        )
                
                # Tool execution results
                elif event_type == "tool_result":
                    tool_name = event.get("name")
                    if tool_name:
                        yield AnalysisEvent(
                            event_type="tool_result",
                            data={
                                "message": f"Completed {tool_name}",
                                "tool": tool_name,
                            },
                        )

            # Send completion event
            yield AnalysisEvent(
                event_type="complete",
                data={"repo_url": repo_url, "status": "completed"},
            )

            logger.info(f"Streaming analysis completed for {repo_url}")

        except Exception as e:
            logger.error(f"Error during streaming analysis: {e}")
            yield AnalysisEvent(
                event_type="error",
                data={"repo_url": repo_url, "error": str(e)},
            )
            raise

    async def close(self) -> None:
        """Close analyzer and cleanup resources."""
        logger.info("Closing repository analyzer")
        if self._mcp_client:
            await self._mcp_client.close()
        self._agent = None
        self._mcp_client = None

    async def __aenter__(self) -> "RepositoryAnalyzer":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


def create_analyzer(settings: Settings | None = None) -> RepositoryAnalyzer:
    """Create a repository analyzer (use with async context manager).

    Args:
        settings: Application settings (defaults to global settings)

    Returns:
        Repository analyzer instance (call initialize() or use async with)
    """
    return RepositoryAnalyzer(settings)
