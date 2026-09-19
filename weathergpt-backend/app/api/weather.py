"""
Plain REST endpoints that hit the tools directly, bypassing the LLM
router. Useful for the frontend's WeatherCard to fetch data without
going through /api/chat, and for testing tools in isolation (see
tests/test_weather_tools.py).
"""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import CurrentWeather, ForecastWeather
from app.tools.current_weather import get_current_weather
from app.tools.forecast_weather import get_forecast_weather
from app.tools.geocoding import GeocodingError
from app.tools.historical_weather import get_historical_weather

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current", response_model=CurrentWeather)
async def current(location: str = Query(...)) -> CurrentWeather:
    try:
        return await get_current_weather(location)
    except GeocodingError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/forecast", response_model=ForecastWeather)
async def forecast(location: str = Query(...), days: int = Query(3, ge=1, le=16)) -> ForecastWeather:
    try:
        return await get_forecast_weather(location, days)
    except GeocodingError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/historical", response_model=ForecastWeather)
async def historical(
    location: str = Query(...),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
) -> ForecastWeather:
    try:
        return await get_historical_weather(location, start_date, end_date)
    except GeocodingError as e:
        raise HTTPException(status_code=404, detail=str(e))
