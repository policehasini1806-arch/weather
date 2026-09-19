"""
Single source of truth for "what tools exist". agent/router.py uses
TOOL_SPECS to tell Groq what it can call (OpenAI-compatible function-calling
format); api/chat.py / agent/graph.py use TOOL_FUNCTIONS to actually invoke
whichever one was picked. Add a new tool by adding one entry to each dict
here — nothing else needs to change.
"""

from app.tools.current_weather import get_current_weather
from app.tools.forecast_weather import get_forecast_weather
from app.tools.historical_weather import get_historical_weather
from app.tools.weather_alerts import get_weather_alerts

# --- OpenAI-compatible function schemas (Groq speaks this format) ---
#
# Every tool requires a `reason` argument. This forces the model to state
# its justification as part of the SAME structured call that picks the tool
# and its parameters — so the tool_trace we show the user is the model's
# actual decision, not a caption we write for it afterwards.
_REASON_PROPERTY = {"reason": {"type": "string", "description": "One short sentence explaining why this tool fits the user's question"}}


def _tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {**properties, **_REASON_PROPERTY},
                "required": [*required, "reason"],
            },
        },
    }


TOOL_SPECS = [
    _tool(
        "current_weather",
        "Get the current weather right now for a location. Use for 'what's it like now' style questions.",
        {"location": {"type": "string", "description": "City or place name, e.g. 'Hyderabad'"}},
        ["location"],
    ),
    _tool(
        "forecast_weather",
        "Get a future weather forecast (today through the next 16 days) for a location. Use for 'tomorrow', 'this weekend', 'next week' style questions.",
        {
            "location": {"type": "string", "description": "City or place name"},
            "days": {"type": "integer", "description": "How many days ahead to forecast, 1-16", "default": 3},
        },
        ["location"],
    ),
    _tool(
        "historical_weather",
        "Get past weather for a location between two dates. Use when the user asks about a date or period that has already happened.",
        {
            "location": {"type": "string", "description": "City or place name"},
            "start_date": {"type": "string", "description": "YYYY-MM-DD"},
            "end_date": {"type": "string", "description": "YYYY-MM-DD"},
        },
        ["location", "start_date", "end_date"],
    ),
    _tool(
        "weather_alerts",
        "Check for severe/extreme weather alerts in the near future for a location. Use for 'is there a storm coming', 'any warnings' style questions.",
        {
            "location": {"type": "string", "description": "City or place name"},
            "lookahead_days": {"type": "integer", "description": "How many days ahead to scan, 1-16", "default": 3},
        },
        ["location"],
    ),
]

# --- Actual callables, keyed by the same tool name ---
TOOL_FUNCTIONS = {
    "current_weather": get_current_weather,
    "forecast_weather": get_forecast_weather,
    "historical_weather": get_historical_weather,
    "weather_alerts": get_weather_alerts,
}
