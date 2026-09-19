"""
current_weather tool: "What's the weather like right now in X?"
"""

from datetime import datetime, timezone

import httpx

from app.config.settings import settings
from app.models.schemas import CurrentWeather, GeocodedLocation
from app.tools._weather_codes import describe_weather_code
from app.tools.geocoding import geocode_location


async def get_current_weather(location: str) -> CurrentWeather:
    # Parameter is named `location` to match the tool schema key in
    # tools/tool_registry.py and agent/fallback.py — keep them in sync.
    location: GeocodedLocation = await geocode_location(location)

    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,relative_humidity_2m",
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.get(settings.WEATHER_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    current = data.get("current", {})

    return CurrentWeather(
        location=location,
        temperature_c=current.get("temperature_2m"),
        feels_like_c=current.get("apparent_temperature"),
        condition=describe_weather_code(current.get("weather_code", -1)),
        wind_speed_kmh=current.get("wind_speed_10m"),
        humidity_pct=current.get("relative_humidity_2m"),
        observed_at=current.get("time", datetime.now(timezone.utc).isoformat()),
    )
