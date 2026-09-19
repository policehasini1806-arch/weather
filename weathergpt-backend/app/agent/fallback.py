"""
Zero-dependency fallback path. Used only when the Groq call fails (network
blip, rate limit, bad key) so a live demo never just dies. Keeps the exact
same ToolTrace / answer contract as the LLM path — the frontend can't tell
the difference except for the (honest) `reason` text.
"""

import re
from datetime import date, timedelta

from app.agent.state import AgentState
from app.models.schemas import ToolTrace

_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

_ALERT_WORDS = ("storm", "alert", "warning", "extreme", "dangerous", "cyclone", "hurricane", "severe")
_NOW_WORDS = ("now", "right now", "currently", "at the moment", "outside right now")
_PAST_WORDS = ("was", "yesterday", "last week", "last month", "on " )  # "on <date>" often means a past lookup


def rule_based_route(state: AgentState) -> ToolTrace:
    """
    Simple keyword/pattern matching. Deliberately conservative: when unsure,
    default to forecast_weather (the safest general-purpose answer), same
    policy the LLM router is instructed to follow.
    """
    message = state.message.lower()
    location = state.location_hint or "Hyderabad"  # last-resort default so the demo never dead-ends
    dates_found = _DATE_RE.findall(message)

    if any(word in message for word in _ALERT_WORDS):
        return ToolTrace(
            tool="weather_alerts",
            parameters={"location": location, "lookahead_days": 3},
            reason="Matched storm/alert/warning keywords (fallback routing — LLM router unavailable).",
        )

    if dates_found and any(word in message for word in _PAST_WORDS):
        start = dates_found[0]
        end = dates_found[1] if len(dates_found) > 1 else dates_found[0]
        return ToolTrace(
            tool="historical_weather",
            parameters={"location": location, "start_date": start, "end_date": end},
            reason="Found an explicit past date in the message (fallback routing — LLM router unavailable).",
        )

    if any(word in message for word in _NOW_WORDS):
        return ToolTrace(
            tool="current_weather",
            parameters={"location": location},
            reason="Matched 'now/currently' keywords (fallback routing — LLM router unavailable).",
        )

    # Default: forecast. Try to guess how many days out.
    days = 3
    if "tomorrow" in message:
        days = 1
    elif "week" in message:
        days = 7

    return ToolTrace(
        tool="forecast_weather",
        parameters={"location": location, "days": days},
        reason="No specific time-frame keyword matched strongly; defaulting to a short-range forecast (fallback routing — LLM router unavailable).",
    )


def template_answer(tool: str, weather_payload) -> str:
    """
    Very plain, deterministic answer text used only when Groq's answer-
    generation call also fails. Not pretty, but always correct and never
    leaves the user with an empty response.
    """
    if tool == "current_weather":
        w = weather_payload
        return (
            f"Right now in {w['location']['name']}: {w['condition']}, "
            f"{w['temperature_c']}°C (feels like {w.get('feels_like_c', w['temperature_c'])}°C)."
        )

    if tool == "forecast_weather" or tool == "historical_weather":
        days = weather_payload["days"]
        loc = weather_payload["location"]["name"]
        lines = [f"{d['date']}: {d['condition']}, {d['temp_min_c']}–{d['temp_max_c']}°C" for d in days]
        return f"Weather for {loc}:\n" + "\n".join(lines)

    if tool == "weather_alerts":
        alerts = weather_payload
        if not alerts:
            return "No severe weather alerts found for the requested period."
        lines = [f"[{a['severity'].upper()}] {a['headline']}" for a in alerts]
        return "Weather alerts:\n" + "\n".join(lines)

    return "Here is the requested weather data."
