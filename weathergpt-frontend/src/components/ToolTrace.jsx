// Renders the compulsory tool-selection trace returned by POST /api/chat:
//   { tool, parameters, reason }
// Open by default so it is visible in a demo; the user can collapse it.

const TOOL_LABELS = {
  current_weather: "Current weather",
  forecast_weather: "Forecast",
  historical_weather: "Historical weather",
  weather_alerts: "Weather alerts",
};

function formatValue(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export default function ToolTrace({ trace }) {
  if (!trace) return null;
  const params = Object.entries(trace.parameters || {});

  return (
    <details className="trace" open>
      <summary className="trace-summary">
        <span className="trace-label">Tool selected</span>
        <span className="trace-name">{TOOL_LABELS[trace.tool] || trace.tool}</span>
      </summary>

      <div className="trace-body">
        <dl className="trace-params">
          <dt>tool</dt>
          <dd>{trace.tool}</dd>
          {params.map(([key, value]) => (
            <div className="trace-row" key={key}>
              <dt>{key}</dt>
              <dd>{formatValue(value)}</dd>
            </div>
          ))}
        </dl>
        <p className="trace-reason">
          <span>Why</span> {trace.reason}
        </p>
      </div>
    </details>
  );
}
