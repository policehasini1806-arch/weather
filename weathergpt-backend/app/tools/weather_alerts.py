"""
weather_alerts tool: "Is there any extreme weather coming to X?"

Open-Meteo doesn't provide an official alerts feed, so for the hackathon
demo we derive alerts by scanning the next few days' forecast for severe
WMO codes (heavy rain, thunderstorms, hail). Swap this for a real
government alerts API (e.g. IMD, NWS) post-hackathon without touching the
router or the response schema.
"""

import httpx

from app.config.settings import settings
from app.models.schemas import GeocodedLocation, WeatherAlert
from app.tools._weather_codes import SEVERE_CODES, describe_weather_code
from app.tools.geocoding import geocode_location

_SEVERITY_BY_CODE = {
    65: "moderate", 67: "severe",
    75: "moderate", 82: "severe", 86: "severe",
    95: "severe", 96: "extreme", 99: "extreme",
}


async def get_weather_alerts(location: str, lookahead_days: int = 3) -> list[WeatherAlert]:
    # Parameter is named `location` to match the tool schema key in
    # tools/tool_registry.py and agent/fallback.py — keep them in sync.
    location: GeocodedLocation = await geocode_location(location)

    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "daily": "weather_code",
        "timezone": "auto",
        "forecast_days": max(1, min(lookahead_days, 16)),
    }

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.get(settings.WEATHER_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    codes = daily.get("weather_code", [])

    alerts: list[WeatherAlert] = []
    for date, code in zip(dates, codes):
        if code in SEVERE_CODES:
            condition = describe_weather_code(code)
            alerts.append(
                WeatherAlert(
                    location=location,
                    severity=_SEVERITY_BY_CODE.get(code, "moderate"),
                    headline=f"{condition} expected on {date}",
                    description=(
                        f"Forecast models indicate {condition.lower()} in {location.name} on {date}. "
                        "Take precautions appropriate to the conditions."
                    ),
                )
            )
    return alerts
