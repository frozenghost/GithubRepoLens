from typing import Awaitable, Callable, Optional

from loguru import logger

from app.core.config import Settings
from app.graph.research_graph import ReportSchema, ResearchState, build_research_graph
from app.mcp.client import MCPRepoClient
from app.models import ResearchReport
from app.providers.llm import get_llm

EventCallback = Optional[Callable[[dict], Awaitable[None]]]


def _to_response(report: ReportSchema) -> ResearchReport:
    return ResearchReport(
        repo_url=str(report.repo_url),
        modules=[m.model_dump() for m in report.modules],
        highlights=[h.model_dump() for h in report.highlights],
        principles=[p.model_dump() for p in report.principles],
        summary=report.summary,
    )


async def run_research(repo_url: str, settings: Settings, on_event: EventCallback = None) -> ResearchReport:
    llm = get_llm(settings)
    mcp_client = MCPRepoClient(settings.mcp_server)
    graph = build_research_graph(llm, mcp_client).compile()

    initial_state: ResearchState = {"repo_url": repo_url, "files": [], "report": None}
    final_state: Optional[ResearchState] = None

    async for event in graph.astream_events(initial_state, version="v1"):
        if on_event:
            await on_event(event)
        if event.get("type") == "end":
            final_state = event.get("state")

    if final_state is None:
        logger.warning("Graph events did not yield final state; invoking directly")
        final_state = await graph.ainvoke(initial_state)

    report = final_state["report"]
    if report is None:
        raise RuntimeError("Research graph produced no report")
    return _to_response(report)

