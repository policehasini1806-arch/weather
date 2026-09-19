"""
Minimal shared state passed between the router and the answer generator.
Kept as a plain dataclass rather than a full LangGraph StateGraph — for a
hackathon timeline, one explicit router call + one answer call is easier
to debug live than a multi-node graph, and produces the exact same
tool_trace contract. If you later want branching/multi-tool chains, this
is the natural place to grow into a LangGraph StateGraph.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentState:
    message: str
    location_hint: Optional[str]
    language: str

    # Filled in by the router
    tool_name: Optional[str] = None
    tool_arguments: dict[str, Any] = field(default_factory=dict)

    # Filled in after the tool runs
    tool_result: Any = None

    # Filled in by the answer generator
    final_answer: Optional[str] = None
