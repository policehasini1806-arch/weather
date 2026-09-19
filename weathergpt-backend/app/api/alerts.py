"""
Alerts endpoints.

GET /api/alerts pulls live from the weather_alerts tool.
POST/DELETE /api/alerts/subscribe use a plain in-memory set for now — swap
this for database/crud.py once the scheduler (scheduler/alert_scheduler.py)
needs durable subscriptions across restarts. Fine for a hackathon demo.
"""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import WeatherAlert
from app.tools.geocoding import GeocodingError
from app.tools.weather_alerts import get_weather_alerts

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# location name (lowercased) -> subscribed  (placeholder, resets on restart)
_SUBSCRIPTIONS: set[str] = set()


@router.get("", response_model=list[WeatherAlert])
async def alerts(location: str = Query(...), lookahead_days: int = Query(3, ge=1, le=16)) -> list[WeatherAlert]:
    try:
        return await get_weather_alerts(location, lookahead_days)
    except GeocodingError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/subscribe")
async def subscribe(location: str = Query(...)) -> dict:
    _SUBSCRIPTIONS.add(location.strip().lower())
    return {"subscribed": True, "location": location}


@router.delete("/subscribe")
async def unsubscribe(location: str = Query(...)) -> dict:
    _SUBSCRIPTIONS.discard(location.strip().lower())
    return {"subscribed": False, "location": location}
