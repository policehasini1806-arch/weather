# WeatherGPT frontend

React + Vite chat UI for the WeatherGPT backend.

## Run

Start the backend first (from the `weathergpt-backend` folder):

    uvicorn app.main:app --reload

Then, in this folder:

    npm install
    npm run dev

Open http://localhost:5173. The port is fixed because the backend's CORS
list (`ALLOWED_ORIGINS` in `app/config/settings.py`) only allows 5173.

If the backend is not on http://localhost:8000, copy `.env.example` to
`.env` and change `VITE_API_URL`.

## What's here

- `ChatBox.jsx` - message thread, example prompts, composer
- `Message.jsx` - one turn: answer, weather card, tool trace
- `ToolTrace.jsx` - the compulsory tool-selection trace (tool, parameters, reason)
- `WeatherCard.jsx` - current / forecast / historical cards
- `AlertCard.jsx` - severity-coded alerts
- `LocationSelector.jsx` - default location and reply language
- `services/api.js` - the only file that talks to the backend
