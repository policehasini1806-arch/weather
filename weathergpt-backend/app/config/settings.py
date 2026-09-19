"""
Central app configuration.

Uses Open-Meteo (https://open-meteo.com) for weather + geocoding because it
requires NO API key — ideal for a hackathon where you don't want to burn
time on key provisioning. If you later want a paid provider (OpenWeather,
Tomorrow.io, etc.) just swap the base URLs here and adjust the response
parsing in tools/current_weather.py and tools/forecast_weather.py.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Loads variables from a .env file (in the `backend/` folder, next to
# requirements.txt) into the environment, if one exists. This runs once,
# at import time, before any os.getenv() calls below — so a .env file is
# picked up automatically without needing $env:... every terminal session.
# If no .env file exists, this is a harmless no-op and normal $env:... /
# export still works exactly as before.
load_dotenv()


@dataclass
class Settings:
    # --- Weather data source (Open-Meteo, free, no key) ---
    GEOCODING_API_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_API_URL: str = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_API_URL: str = "https://archive-api.open-meteo.com/v1/archive"

    # --- LLM provider for the agent / tool router ---
    # Groq (https://console.groq.com) is free-tier, fast, and OpenAI-compatible
    # tool-calling — no card required. Set GROQ_API_KEY in your environment.
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    # llama-3.3-70b-versatile was deprecated/shut down by Groq on 2026-08-16.
    # openai/gpt-oss-120b is Groq's recommended replacement (see
    # https://console.groq.com/docs/deprecations). If Groq deprecates this
    # one too in the future, check that page and update this one line.
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # --- App behaviour ---
    DEFAULT_LANGUAGE: str = "English"
    REQUEST_TIMEOUT_SECONDS: float = 8.0

    # --- CORS (adjust for your deployed frontend origin) ---
    ALLOWED_ORIGINS: tuple = ("http://localhost:5173", "http://127.0.0.1:5173")


settings = Settings()
