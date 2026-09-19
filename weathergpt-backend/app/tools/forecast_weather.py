"""
forecast_weather tool: "Will it rain in X tomorrow?" / "What's the weather
like this week in X?"
"""

import httpx

from app.config.settings import settings
from app.models.schemas import ForecastDay, ForecastWeather, GeocodedLocation
from app.tools._weather_codes import describe_weather_code
from app.tools.geocoding import geocode_location


async def get_forecast_weather(location: str, days: int = 3) -> ForecastWeather:
    """
    days: how many days ahead to return (1-16). The agent decides this based
    on the user's phrasing (e.g. "tomorrow" -> 1, "this week" -> 7).

    Parameter is named `location` to match the tool schema key in
    tools/tool_registry.py and agent/fallback.py — keep them in sync.
    """
    days = max(1, min(days, 16))
    location: GeocodedLocation = await geocode_location(location)

    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": days,
    }

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.get(settings.WEATHER_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])

    forecast_days = [
        ForecastDay(
            date=dates[i],
            temp_min_c=daily["temperature_2m_min"][i],
            temp_max_c=daily["temperature_2m_max"][i],
            condition=describe_weather_code(daily["weather_code"][i]),
            precipitation_probability_pct=daily.get("precipitation_probability_max", [None] * len(dates))[i],
        )
        for i in range(len(dates))
    ]

    return ForecastWeather(location=location, days=forecast_days)
