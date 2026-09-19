"""
The core "agent" decision step: given the user's message, ask Groq to pick
exactly one tool and fill in its arguments (including `reason`). Falls back
to a deterministic rule-based router (agent/fallback.py) if the Groq call
fails for any reason — network error, rate limit, bad key, malformed
response — so a live demo never just crashes.
"""

import json
import logging

import httpx

from app.agent.fallback import rule_based_route
from app.agent.prompts import ROUTER_SYSTEM_PROMPT
from app.agent.state import AgentState
from app.config.settings import settings
from app.models.schemas import ToolTrace
from app.tools.tool_registry import TOOL_SPECS

logger = logging.getLogger(__name__)


def route(state: AgentState) -> ToolTrace:
    try:
        return _route_with_groq(state)
    except Exception as e:  # noqa: BLE001 - deliberately broad: any failure should fall back, not crash the demo
        logger.warning("Groq routing failed (%s) - falling back to rule-based router", e)
        trace = rule_based_route(state)
        state.tool_name = trace.tool
        state.tool_arguments = {k: v for k, v in trace.parameters.items()}
        return trace


def _route_with_groq(state: AgentState) -> ToolTrace:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set")

    user_content = (
        f"User message: {state.message}\n"
        f"Default location if none is mentioned: {state.location_hint or 'Hyderabad'}\n"
        f"Response language: {state.language}"
    )

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "tools": TOOL_SPECS,
        "tool_choice": "required",  # forces the model to call one of the tools, never plain text
        "temperature": 0,
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        resp = client.post(settings.GROQ_API_URL, json=payload, headers=headers)
        if resp.status_code >= 400:
            # Surface Groq's actual error body (e.g. "model decommissioned")
            # instead of a bare status code, so future issues are diagnosable
            # straight from the log instead of requiring a websearch.
            raise RuntimeError(f"Groq API error {resp.status_code}: {resp.text}")
        data = resp.json()

    message = data["choices"][0]["message"]
    tool_calls = message.get("tool_calls") or []
    if not tool_calls:
        raise RuntimeError("Groq did not return a tool call despite tool_choice='required'")

    call = tool_calls[0]["function"]
    arguments = json.loads(call["arguments"])
    reason = arguments.pop("reason", "No reason provided by the model.")
    tool_name = call["name"]

    state.tool_name = tool_name
    state.tool_arguments = arguments

    return ToolTrace(tool=tool_name, parameters=arguments, reason=reason)
