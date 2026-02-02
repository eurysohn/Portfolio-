from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RetrievalHit(BaseModel):
    source_id: str
    chunk_id: str
    score: float
    snippet: Optional[str] = None


class WorkflowTrace(BaseModel):
    input: str
    normalized_input: str
    route_taken: List[str] = Field(default_factory=list)
    dictionary_hits: List[str] = Field(default_factory=list)
    retrieval_hits: List[RetrievalHit] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    decisions: List[str] = Field(default_factory=list)
    output: Optional[str] = None
    citations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_route(self, name: str) -> None:
        if name not in self.route_taken:
            self.route_taken.append(name)

    def add_tool(self, name: str) -> None:
        if name not in self.tools_used:
            self.tools_used.append(name)

    def summary(self) -> str:
        routes = ", ".join(self.route_taken) if self.route_taken else "none"
        tools = ", ".join(self.tools_used) if self.tools_used else "none"
        decisions = " | ".join(self.decisions) if self.decisions else "none"
        sources = ", ".join(self.citations) if self.citations else "none"
        return (
            "Workflow Trace:\n"
            f"- route: {routes}\n"
            f"- tools: {tools}\n"
            f"- sources: {sources}\n"
            f"- decisions: {decisions}"
        )
