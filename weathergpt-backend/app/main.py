from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, chat, weather
from app.config.settings import settings

app = FastAPI(title="WeatherGPT", description="Agentic weather chatbot with a compulsory tool-selection trace")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(alerts.router)


@app.get("/")
async def root() -> dict:
    return {"status": "ok", "service": "WeatherGPT backend"}
