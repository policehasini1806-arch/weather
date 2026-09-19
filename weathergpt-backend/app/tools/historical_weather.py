"""
historical_weather tool: "What was the weather in X on <past date>?" /
"How much rain did X get last month?"
"""

import httpx

from app.config.settings import settings
from app.models.schemas import ForecastDay, ForecastWeather, GeocodedLocation
from app.tools._weather_codes import describe_weather_code
from app.tools.geocoding import geocode_location


async def get_historical_weather(location: str, start_date: str, end_date: str) -> ForecastWeather:
    """
    start_date / end_date: "YYYY-MM-DD". Open-Meteo's archive API only
    covers dates in the past, so the agent should route here (not to
    forecast_weather) whenever the user asks about a bygone date range.

    Parameter is named `location` to match the tool schema key in
    tools/tool_registry.py and agent/fallback.py — keep them in sync.
    """
    location: GeocodedLocation = await geocode_location(location)

    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.get(settings.ARCHIVE_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])

    days = [
        ForecastDay(
            date=dates[i],
            temp_min_c=daily["temperature_2m_min"][i],
            temp_max_c=daily["temperature_2m_max"][i],
            condition=describe_weather_code(daily["weather_code"][i]),
            precipitation_probability_pct=None,  # archive gives precipitation_sum, not probability
        )
        for i in range(len(dates))
    ]

    return ForecastWeather(location=location, days=days)
