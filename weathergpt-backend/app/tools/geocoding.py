"""
Resolves a free-text location string ("Hyderabad", "hyd", "Hyderabad, IN")
into coordinates. Every other tool depends on this running first, since
Open-Meteo's weather endpoints take lat/lon, not place names.
"""

import httpx

from app.config.settings import settings
from app.models.schemas import GeocodedLocation


class GeocodingError(Exception):
    pass


async def geocode_location(location_name: str) -> GeocodedLocation:
    """
    Look up a place name and return its best-match coordinates.

    Raises GeocodingError if nothing matches, so callers can turn that into
    a clean 404 / chat message instead of an unhandled exception.
    """
    params = {"name": location_name, "count": 1, "language": "en", "format": "json"}

    async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.get(settings.GEOCODING_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results") or []
    if not results:
        raise GeocodingError(f"Could not find a location matching '{location_name}'")

    top = results[0]
    return GeocodedLocation(
        name=top.get("name", location_name),
        latitude=top["latitude"],
        longitude=top["longitude"],
        country=top.get("country"),
        timezone=top.get("timezone"),
    )
