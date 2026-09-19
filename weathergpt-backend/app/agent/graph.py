"""
Orchestrates one full turn: route -> call tool -> generate natural-language
answer. Called "graph.py" to match the folder's intent (this is where a
real LangGraph StateGraph would live if you grow into one), but for the
hackathon it's a straight-line pipeline — simplest thing that gives you a
reliable demo.
"""

import logging

import httpx

from app.agent.fallback import template_answer
from app.agent.prompts import ANSWER_SYSTEM_PROMPT
from app.agent.router import route
from app.agent.state import AgentState
from app.config.settings import settings
from app.models.schemas import ChatResponse, ToolTrace
from app.tools.tool_registry import TOOL_FUNCTIONS

logger = logging.getLogger(__name__)


async def run_agent(message: str, location_hint: str | None, language: str) -> ChatResponse:
    state = AgentState(message=message, location_hint=location_hint, language=language or settings.DEFAULT_LANGUAGE)

    # 1. Decide which tool to use (this also produces the compulsory trace).
    #    route() already falls back to rule-based routing internally if Groq fails.
    tool_trace: ToolTrace = route(state)

    # 2. Actually call that tool
    tool_fn = TOOL_FUNCTIONS[state.tool_name]
    tool_result = await tool_fn(**state.tool_arguments)
    state.tool_result = tool_result

    # tool_result is a Pydantic model (or list of them, for alerts) — make
    # it JSON-serialisable for both the LLM prompt and the API response.
    if isinstance(tool_result, list):
        weather_payload = [item.model_dump() for item in tool_result]
    else:
        weather_payload = tool_result.model_dump()

    # 3. Turn the raw data into a natural-language answer via Groq, with a
    #    deterministic template as a fallback if that call also fails.
    final_answer = _generate_answer(message, state.language, tool_trace.tool, weather_payload)

    return ChatResponse(
        answer=final_answer,
        language=state.language,
        weather=weather_payload if isinstance(weather_payload, dict) else {"alerts": weather_payload},
        tool_trace=tool_trace,
    )


def _generate_answer(message: str, language: str, tool: str, weather_payload) -> str:
    try:
        return _generate_answer_with_groq(message, language, tool, weather_payload)
    except Exception as e:  # noqa: BLE001 - any failure here should degrade gracefully, not crash the response
        logger.warning("Groq answer generation failed (%s) - falling back to template answer", e)
        return template_answer(tool, weather_payload)


def _generate_answer_with_groq(message: str, language: str, tool: str, weather_payload) -> str:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set")

    prompt = (
        f"User's question: {message}\n"
        f"Language to respond in: {language}\n"
        f"Tool used: {tool}\n"
        f"Raw weather data (JSON): {weather_payload}"
    )
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        resp = client.post(settings.GROQ_API_URL, json=payload, headers=headers)
        if resp.status_code >= 400:
            raise RuntimeError(f"Groq API error {resp.status_code}: {resp.text}")
        data = resp.json()

    text = data["choices"][0]["message"]["content"]
    return text.strip() or template_answer(tool, weather_payload)
