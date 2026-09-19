"""
Pydantic models shared by the API layer, the agent, and the tools.

Keeping these in one place means api/chat.py, agent/router.py, and every
tool in tools/ all speak the same shapes — which matters most for
ToolTrace, since the frontend renders it directly.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

ToolName = Literal[
    "current_weather",
    "forecast_weather",
    "historical_weather",
    "weather_alerts",
]


# ---------------------------------------------------------------------------
# Tool Trace — the compulsory, first-class "why did the agent do this" record
# ---------------------------------------------------------------------------

class ToolTrace(BaseModel):
    tool: ToolName
    parameters: dict[str, Any]
    reason: str = Field(..., description="Plain-language justification the LLM gave for picking this tool")


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    location: Optional[str] = None
    language: Optional[str] = "English"


class ChatResponse(BaseModel):
    answer: str
    language: str
    weather: Optional[dict[str, Any]] = None
    tool_trace: ToolTrace


# ---------------------------------------------------------------------------
# Weather data shapes
# ---------------------------------------------------------------------------

class GeocodedLocation(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    timezone: Optional[str] = None


class CurrentWeather(BaseModel):
    location: GeocodedLocation
    temperature_c: float
    feels_like_c: Optional[float] = None
    condition: str
    wind_speed_kmh: Optional[float] = None
    humidity_pct: Optional[float] = None
    observed_at: str


class ForecastDay(BaseModel):
    date: str
    temp_min_c: float
    temp_max_c: float
    condition: str
    precipitation_probability_pct: Optional[float] = None


class ForecastWeather(BaseModel):
    location: GeocodedLocation
    days: list[ForecastDay]


class WeatherAlert(BaseModel):
    location: GeocodedLocation
    severity: Literal["minor", "moderate", "severe", "extreme"]
    headline: str
    description: str
