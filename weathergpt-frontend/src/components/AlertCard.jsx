// One weather alert. Severity is shown as text as well as colour so it
// doesn't rely on colour alone.
const SEVERITY_LABELS = {
  minor: "Minor",
  moderate: "Moderate",
  severe: "Severe",
  extreme: "Extreme",
};

export default function AlertCard({ alert }) {
  const level = alert.severity in SEVERITY_LABELS ? alert.severity : "moderate";
  return (
    <article className={`alert alert-${level}`}>
      <div className="alert-top">
        <span className="alert-badge">{SEVERITY_LABELS[level]}</span>
        <span className="alert-place">
          {alert.location?.name}
          {alert.location?.country ? `, ${alert.location.country}` : ""}
        </span>
      </div>
      <h3 className="alert-headline">{alert.headline}</h3>
      <p className="alert-desc">{alert.description}</p>
    </article>
  );
}
