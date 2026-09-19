import AlertCard from "./AlertCard.jsx";

// The `weather` field of /api/chat comes back in one of three shapes,
// depending on which tool the agent picked:
//   current_weather              -> { location, temperature_c, condition, ... }
//   forecast / historical        -> { location, days: [...] }
//   weather_alerts               -> { alerts: [...] }

function placeName(location) {
  if (!location) return "";
  return location.country ? `${location.name}, ${location.country}` : location.name;
}

// "2026-09-19" -> "Sat 19 Sep". Parsed by hand so the browser's timezone
// can't shift the date by a day.
function formatDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return iso;
  const dt = new Date(y, m - 1, d);
  const weekday = dt.toLocaleDateString("en-US", { weekday: "short" });
  const month = dt.toLocaleDateString("en-US", { month: "short" });
  return `${weekday} ${d} ${month}`;
}

function round(n) {
  return Math.round(n);
}

function Current({ w }) {
  return (
    <section className="wx wx-current" aria-label={`Current weather in ${w.location?.name}`}>
      <div className="wx-place">{placeName(w.location)}</div>
      <div className="wx-now">
        <span className="wx-temp">{round(w.temperature_c)}°</span>
        <span className="wx-cond">{w.condition}</span>
      </div>
      <dl className="wx-facts">
        {typeof w.feels_like_c === "number" && (
          <div>
            <dt>Feels like</dt>
            <dd>{round(w.feels_like_c)}°C</dd>
          </div>
        )}
        {typeof w.humidity_pct === "number" && (
          <div>
            <dt>Humidity</dt>
            <dd>{round(w.humidity_pct)}%</dd>
          </div>
        )}
        {typeof w.wind_speed_kmh === "number" && (
          <div>
            <dt>Wind</dt>
            <dd>{round(w.wind_speed_kmh)} km/h</dd>
          </div>
        )}
      </dl>
      {w.observed_at && <div className="wx-time">Observed {w.observed_at.replace("T", " ")}</div>}
    </section>
  );
}

function Days({ w, tool }) {
  const days = w.days || [];
  if (!days.length) return null;

  // Each day's bar is positioned on one shared scale so days compare at a glance.
  const lo = Math.min(...days.map((d) => d.temp_min_c));
  const hi = Math.max(...days.map((d) => d.temp_max_c));
  const span = hi - lo || 1;
  const title = tool === "historical_weather" ? "Historical" : "Forecast";

  return (
    <section className="wx wx-days" aria-label={`${title} for ${w.location?.name}`}>
      <div className="wx-place">
        {title} · {placeName(w.location)}
      </div>
      <ul className="days">
        {days.map((d) => {
          const left = ((d.temp_min_c - lo) / span) * 100;
          const width = Math.max(((d.temp_max_c - d.temp_min_c) / span) * 100, 4);
          return (
            <li className="day" key={d.date}>
              <span className="day-date">{formatDate(d.date)}</span>
              <span className="day-cond">{d.condition}</span>
              <span className="day-range" aria-hidden="true">
                <span className="day-bar" style={{ left: `${left}%`, width: `${width}%` }} />
              </span>
              <span className="day-temps">
                {round(d.temp_min_c)}° / {round(d.temp_max_c)}°
              </span>
              <span className="day-rain">
                {typeof d.precipitation_probability_pct === "number"
                  ? `${round(d.precipitation_probability_pct)}% rain`
                  : ""}
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

export default function WeatherCard({ weather, tool }) {
  if (!weather) return null;

  if (Array.isArray(weather.alerts)) {
    if (weather.alerts.length === 0) {
      return <p className="wx-empty">No severe weather in the forecast window.</p>;
    }
    return (
      <div className="alerts">
        {weather.alerts.map((a, i) => (
          <AlertCard alert={a} key={`${a.headline}-${i}`} />
        ))}
      </div>
    );
  }
  if (typeof weather.temperature_c === "number") return <Current w={weather} />;
  if (Array.isArray(weather.days)) return <Days w={weather} tool={tool} />;
  return null;
}
