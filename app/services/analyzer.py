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
        self, repo_url: str
    ) -> AsyncGenerator[AnalysisEvent, None]:
        """Stream analysis progress in real-time.

        Args:
            repo_url: GitHub repository URL

        Yields:
            Analysis events

        Raises:
            RuntimeError: If analyzer is not initialized
        """
        if self._agent is None:
            raise RuntimeError("Analyzer not initialized. Call initialize() first.")

        logger.info(f"Starting streaming analysis for {repo_url}")

        # Send start event
        yield AnalysisEvent(
            event_type="start",
            data={"repo_url": repo_url, "status": "started"},
        )

        try:
            # Stream analysis events
            async for event in self._agent.stream_analysis(repo_url):
                # Process different event types
                for node_name, node_output in event.items():
                    if node_name == "agent":
                        # Agent node output
                        messages = node_output.get("messages", [])
                        if messages:
                            last_message = messages[-1]
                            
                            # Check if agent is making tool calls
                            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                                # Simplify tool call display
                                tool_names = [tc["name"] for tc in last_message.tool_calls]
                                tool_args = [tc.get("args", {}) for tc in last_message.tool_calls]
                                
                                for tool_name, args in zip(tool_names, tool_args):
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
                                            "node": node_name,
                                            "message": message,
                                            "tool": tool_name,
                                        },
                                    )
                            else:
                                # Regular agent response
                                content = last_message.content if hasattr(last_message, "content") else str(last_message)
                                if content and content.strip():
                                    yield AnalysisEvent(
                                        event_type="agent_response",
                                        data={
                                            "node": node_name,
                                            "content": content,
                                        },
                                    )
                    elif node_name == "tools":
                        # Tool execution output - simplified
                        messages = node_output.get("messages", [])
                        for msg in messages:
                            if hasattr(msg, "name"):
                                tool_name = msg.name
                                yield AnalysisEvent(
                                    event_type="tool_result",
                                    data={
                                        "node": node_name,
                                        "message": f"Completed {tool_name}",
                                        "tool": tool_name,
                                    },
                                )
                    else:
                        # Generic node output
                        yield AnalysisEvent(
                            event_type="progress",
                            data={
                                "node": node_name,
                                "output": str(node_output),
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
