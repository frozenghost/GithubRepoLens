"""LangGraph agent for repository analysis."""

import json
from typing import Annotated, Literal, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from loguru import logger

from app.prompts.base import get_prompt_loader


class AgentState(TypedDict):
    """State for the analysis agent."""

    messages: Annotated[list[BaseMessage], add_messages]
    repo_url: str
    analysis_stage: Literal[
        "init", "exploring", "analyzing", "reporting", "completed"
    ]


class RepositoryAnalysisAgent:
    """LangGraph agent for deep repository analysis."""

    def __init__(self, llm: BaseChatModel, tools: list[BaseTool]):
        """Initialize the analysis agent.

        Args:
            llm: Language model instance
            tools: List of MCP tools for repository interaction
        """
        self.llm = llm
        self.tools = tools
        self.prompt_loader = get_prompt_loader()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph for analysis workflow."""
        logger.info("Building LangGraph agent")

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes - use async versions for proper streaming support
        workflow.add_node("agent", self._agent_node_async)
        workflow.add_node("tools", self._custom_tool_node_async)

        # Define edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "tools": "tools",
                END: END,
            },
        )
        workflow.add_edge("tools", "agent")

        # Compile the graph
        compiled = workflow.compile()
        logger.info("LangGraph agent compiled successfully")
        return compiled

    def _custom_tool_node(self, state: AgentState) -> dict:
        """Custom tool node that properly formats tool results.

        Args:
            state: Current agent state

        Returns:
            Updated state with tool results
        """
        messages = state["messages"]
        if not messages:
            return {"messages": []}

        last_message = messages[-1]
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {"messages": []}

        tools_by_name = {tool.name: tool for tool in self.tools}
        tool_messages = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            logger.debug(f"Executing tool: {tool_name} with args: {tool_args}")

            try:
                tool = tools_by_name.get(tool_name)
                if not tool:
                    error_msg = f"Tool {tool_name} not found"
                    logger.error(error_msg)
                    tool_messages.append(
                        ToolMessage(
                            content=error_msg,
                            name=tool_name,
                            tool_call_id=tool_call_id,
                            status="error",
                        )
                    )
                    continue

                result = tool.invoke(tool_args)

                # Format result as string to ensure compatibility
                if isinstance(result, str):
                    content = result
                elif isinstance(result, dict):
                    content = json.dumps(result, indent=2)
                elif isinstance(result, list):
                    # Handle list of content blocks from MCP
                    if result and isinstance(result[0], dict) and "text" in result[0]:
                        content = "\n".join(item["text"] for item in result if "text" in item)
                    else:
                        content = json.dumps(result, indent=2)
                else:
                    content = str(result)

                tool_messages.append(
                    ToolMessage(
                        content=content,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                    )
                )
                logger.debug(f"Tool {tool_name} executed successfully")

            except Exception as e:
                error_msg = f"Error executing tool {tool_name}: {str(e)}"
                logger.error(error_msg)
                tool_messages.append(
                    ToolMessage(
                        content=error_msg,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="error",
                    )
                )

        return {"messages": tool_messages}

    async def _custom_tool_node_async(self, state: AgentState) -> dict:
        """Async custom tool node that properly formats tool results.

        Args:
            state: Current agent state

        Returns:
            Updated state with tool results
        """
        messages = state["messages"]
        if not messages:
            return {"messages": []}

        last_message = messages[-1]
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            return {"messages": []}

        tools_by_name = {tool.name: tool for tool in self.tools}
        tool_messages = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            logger.debug(f"Executing tool: {tool_name} with args: {tool_args}")

            try:
                tool = tools_by_name.get(tool_name)
                if not tool:
                    error_msg = f"Tool {tool_name} not found"
                    logger.error(error_msg)
                    tool_messages.append(
                        ToolMessage(
                            content=error_msg,
                            name=tool_name,
                            tool_call_id=tool_call_id,
                            status="error",
                        )
                    )
                    continue

                result = await tool.ainvoke(tool_args)

                # Format result as string to ensure compatibility
                if isinstance(result, str):
                    content = result
                elif isinstance(result, dict):
                    content = json.dumps(result, indent=2)
                elif isinstance(result, list):
                    # Handle list of content blocks from MCP
                    if result and isinstance(result[0], dict) and "text" in result[0]:
                        content = "\n".join(item["text"] for item in result if "text" in item)
                    else:
                        content = json.dumps(result, indent=2)
                else:
                    content = str(result)

                tool_messages.append(
                    ToolMessage(
                        content=content,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                    )
                )
                logger.debug(f"Tool {tool_name} executed successfully")

            except Exception as e:
                error_msg = f"Error executing tool {tool_name}: {str(e)}"
                logger.error(error_msg)
                tool_messages.append(
                    ToolMessage(
                        content=error_msg,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="error",
                    )
                )

        return {"messages": tool_messages}

    def _agent_node(self, state: AgentState) -> dict:
        """Agent node that processes messages and decides next action.

        Args:
            state: Current agent state

        Returns:
            Updated state with new messages
        """
        messages = state["messages"]

        logger.debug(f"Agent node processing {len(messages)} messages")

        # Bind tools to LLM
        llm_with_tools = self.llm.bind_tools(self.tools)

        # Invoke LLM
        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}

    async def _agent_node_async(self, state: AgentState) -> dict:
        """Async version of agent node.

        Args:
            state: Current agent state

        Returns:
            Updated state with new messages
        """
        messages = state["messages"]

        logger.debug(f"Agent node processing {len(messages)} messages")

        # Bind tools to LLM
        llm_with_tools = self.llm.bind_tools(self.tools)

        # Invoke LLM asynchronously
        response = await llm_with_tools.ainvoke(messages)

        return {"messages": [response]}

    def analyze(self, repo_url: str) -> dict:
        """Perform synchronous repository analysis.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Final state with analysis results
        """
        logger.info(f"Starting synchronous analysis for {repo_url}")

        # Load system and analysis prompts
        system_prompt = self.prompt_loader.render("system", repo_url=repo_url)
        analysis_prompt = self.prompt_loader.render("analysis", repo_url=repo_url)

        # Combine prompts
        full_prompt = f"{system_prompt}\n\n{analysis_prompt}"

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=full_prompt)],
            "repo_url": repo_url,
            "analysis_stage": "init",
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        logger.info("Synchronous analysis completed")
        return final_state

    async def analyze_async(self, repo_url: str) -> dict:
        """Perform asynchronous repository analysis.

        Args:
            repo_url: GitHub repository URL

        Returns:
            Final state with analysis results
        """
        logger.info(f"Starting asynchronous analysis for {repo_url}")

        # Load system and analysis prompts
        system_prompt = self.prompt_loader.render("system", repo_url=repo_url)
        analysis_prompt = self.prompt_loader.render("analysis", repo_url=repo_url)

        # Combine prompts
        full_prompt = f"{system_prompt}\n\n{analysis_prompt}"

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=full_prompt)],
            "repo_url": repo_url,
            "analysis_stage": "init",
        }

        # Run the graph asynchronously
        final_state = await self.graph.ainvoke(initial_state)

        logger.info("Asynchronous analysis completed")
        return final_state

    async def stream_analysis(self, repo_url: str, language: str = "en"):
        """Stream analysis progress in real-time with token-level streaming.

        Args:
            repo_url: GitHub repository URL
            language: Analysis report language (en, zh, ja, etc.)

        Yields:
            State updates and token chunks as they occur
        """
        logger.info(f"Starting streaming analysis for {repo_url} (language: {language})")

        # Load system and analysis prompts
        system_prompt = self.prompt_loader.render("system", repo_url=repo_url, language=language)
        analysis_prompt = self.prompt_loader.render("analysis", repo_url=repo_url, language=language)

        # Combine prompts
        full_prompt = f"{system_prompt}\n\n{analysis_prompt}"

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=full_prompt)],
            "repo_url": repo_url,
            "analysis_stage": "init",
        }

        # Stream the graph execution with messages mode for token streaming
        async for event in self.graph.astream_events(initial_state, version="v2"):
            kind = event.get("event")
            
            # Token streaming from LLM
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield {
                        "type": "token",
                        "content": chunk.content,
                    }
            
            # Tool calls
            elif kind == "on_chat_model_end":
                output = event.get("data", {}).get("output")
                if output and hasattr(output, "tool_calls") and output.tool_calls:
                    yield {
                        "type": "tool_calls",
                        "tool_calls": output.tool_calls,
                    }
            
            # Tool execution results
            elif kind == "on_tool_end":
                yield {
                    "type": "tool_result",
                    "name": event.get("name"),
                    "output": event.get("data", {}).get("output"),
                }

        logger.info("Streaming analysis completed")


def create_analysis_agent(
    llm: BaseChatModel, tools: list[BaseTool]
) -> RepositoryAnalysisAgent:
    """Create a repository analysis agent.

    Args:
        llm: Language model instance
        tools: List of MCP tools

    Returns:
        Configured analysis agent
    """
    return RepositoryAnalysisAgent(llm=llm, tools=tools)
