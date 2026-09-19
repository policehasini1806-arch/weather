"""
WeatherGPT - Streamlit version.

Runs the same agent as the FastAPI backend (route -> tool -> answer), but
calls it directly, so there is no separate API server to host.

Run locally (from the weathergpt-backend folder):
    streamlit run streamlit_app.py
"""

import asyncio
import os
import sys
from pathlib import Path

import httpx
import pandas as pd
import streamlit as st

# Make `import app...` work wherever Streamlit is started from. On Streamlit
# Cloud the working directory is the repo root, not this folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))

st.set_page_config(page_title="WeatherGPT", page_icon="🌦️", layout="wide")

# On Streamlit Cloud the Groq key comes from the app's Secrets. Copy it into
# the environment BEFORE the backend's settings module is imported, because
# settings.py reads GROQ_API_KEY once, at import time. Locally, the .env file
# in this folder is still picked up as before.
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = str(st.secrets["GROQ_API_KEY"])
except Exception:  # no secrets configured (normal when running locally)
    pass

from app.agent.graph import run_agent  # noqa: E402
from app.config.settings import settings  # noqa: E402
from app.tools.geocoding import GeocodingError  # noqa: E402

LANGUAGES = {
    "English": "English",
    "Hindi (हिन्दी)": "Hindi",
    "Telugu (తెలుగు)": "Telugu",
    "Tamil (தமிழ்)": "Tamil",
    "Spanish (Español)": "Spanish",
    "French (Français)": "French",
}

EXAMPLES = [
    "Will it rain tomorrow?",
    "How hot is it right now?",
    "Any extreme weather coming this week?",
    "What was the weather from 2026-09-01 to 2026-09-05?",
]

TOOL_LABELS = {
    "current_weather": "Current weather",
    "forecast_weather": "Forecast",
    "historical_weather": "Historical weather",
    "weather_alerts": "Weather alerts",
}


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def place_name(location: dict) -> str:
    if not location:
        return ""
    country = location.get("country")
    return f"{location['name']}, {country}" if country else location["name"]


def render_current(w: dict) -> None:
    st.markdown(f"**{place_name(w.get('location'))}** · {w['condition']}")
    cols = st.columns(4)
    cols[0].metric("Temperature", f"{w['temperature_c']:.0f}°C")
    if w.get("feels_like_c") is not None:
        cols[1].metric("Feels like", f"{w['feels_like_c']:.0f}°C")
    if w.get("humidity_pct") is not None:
        cols[2].metric("Humidity", f"{w['humidity_pct']:.0f}%")
    if w.get("wind_speed_kmh") is not None:
        cols[3].metric("Wind", f"{w['wind_speed_kmh']:.0f} km/h")
    if w.get("observed_at"):
        st.caption(f"Observed {w['observed_at'].replace('T', ' ')}")


def render_days(w: dict, tool: str) -> None:
    days = w.get("days") or []
    if not days:
        return
    title = "Historical" if tool == "historical_weather" else "Forecast"
    st.markdown(f"**{title}** · {place_name(w.get('location'))}")
    df = pd.DataFrame(
        [
            {
                "Date": d["date"],
                "Condition": d["condition"],
                "Min °C": d["temp_min_c"],
                "Max °C": d["temp_max_c"],
                "Rain chance %": d.get("precipitation_probability_pct"),
            }
            for d in days
        ]
    )
    st.dataframe(df, hide_index=True)
    if len(df) > 1:
        st.line_chart(df.set_index("Date")[["Min °C", "Max °C"]])


def render_alerts(alerts: list) -> None:
    if not alerts:
        st.success("No severe weather in the forecast window.")
        return
    for a in alerts:
        text = f"**{a['severity'].title()}: {a['headline']}**\n\n{a['description']}"
        if a["severity"] in ("severe", "extreme"):
            st.error(text)
        elif a["severity"] == "moderate":
            st.warning(text)
        else:
            st.info(text)


def render_weather(weather: dict | None, tool: str) -> None:
    if not weather:
        return
    if "alerts" in weather:
        render_alerts(weather["alerts"])
    elif "temperature_c" in weather:
        render_current(weather)
    elif "days" in weather:
        render_days(weather, tool)


def render_trace(trace: dict) -> None:
    """The compulsory tool-selection trace: tool, parameters, reason."""
    label = TOOL_LABELS.get(trace["tool"], trace["tool"])
    with st.expander(f"Tool selected: {label}", expanded=True):
        st.markdown(f"**tool:** `{trace['tool']}`")
        for key, value in trace["parameters"].items():
            st.markdown(f"**{key}:** `{value}`")
        st.markdown(f"**Why:** {trace['reason']}")


def render_message(msg: dict) -> None:
    with st.chat_message(msg["role"]):
        if msg.get("error"):
            st.error(msg["text"])
            return
        st.markdown(msg["text"])
        if msg["role"] == "assistant":
            render_weather(msg.get("weather"), msg["trace"]["tool"])
            render_trace(msg["trace"])


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("WeatherGPT")
    location = st.text_input(
        "Default location",
        value="Hyderabad",
        help="Used when your question doesn't name a place.",
    )
    language = LANGUAGES[st.selectbox("Reply language", list(LANGUAGES))]
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
    if not settings.GROQ_API_KEY:
        st.warning(
            "No GROQ_API_KEY found. The app will fall back to simple keyword "
            "routing and template answers."
        )

st.title("WeatherGPT")
st.caption("Every answer shows which tool the agent picked and why.")

# A question comes either from the chat box or from an example button.
prompt = st.chat_input("Ask about current weather, forecasts, past weather or alerts")
if not prompt:
    prompt = st.session_state.pop("queued", None)

if not st.session_state.messages and not prompt:
    st.subheader("Ask about the weather")
    cols = st.columns(2)
    for i, question in enumerate(EXAMPLES):
        if cols[i % 2].button(question, key=f"example-{i}"):
            st.session_state.queued = question
            st.rerun()

for message in st.session_state.messages:
    render_message(message)

if prompt:
    user_message = {"role": "user", "text": prompt}
    st.session_state.messages.append(user_message)
    render_message(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Choosing a tool…"):
            try:
                result = asyncio.run(
                    run_agent(
                        message=prompt,
                        location_hint=location.strip() or None,
                        language=language,
                    )
                )
                reply = {
                    "role": "assistant",
                    "text": result.answer,
                    "weather": result.weather,
                    "trace": result.tool_trace.model_dump(),
                }
            except GeocodingError as e:
                reply = {"role": "assistant", "error": True, "text": str(e)}
            except httpx.HTTPError:
                reply = {
                    "role": "assistant",
                    "error": True,
                    "text": "A weather service request failed. Please try again in a moment.",
                }
            except Exception as e:  # noqa: BLE001 - show the problem instead of a blank page
                reply = {"role": "assistant", "error": True, "text": f"Something went wrong: {e}"}

    st.session_state.messages.append(reply)
    st.rerun()
