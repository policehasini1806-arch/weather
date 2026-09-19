// All backend calls live here so components never build URLs themselves.
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, options);
  } catch {
    throw new ApiError(
      `Can't reach the backend at ${BASE}. Start it from the backend folder with: uvicorn app.main:app --reload`,
      0
    );
  }

  if (!res.ok) {
    // FastAPI puts the human-readable reason in `detail`
    // (e.g. the GeocodingError message on a 404).
    let message = `The backend returned an error (${res.status}).`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      /* keep the generic message */
    }
    throw new ApiError(message, res.status);
  }
  return res.json();
}

/**
 * POST /api/chat
 * Returns { answer, language, weather, tool_trace: { tool, parameters, reason } }
 */
export function sendChat({ message, location, language }) {
  return request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      location: location?.trim() || null,
      language,
    }),
  });
}
