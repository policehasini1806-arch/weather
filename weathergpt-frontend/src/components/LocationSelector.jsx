// Sidebar controls: the default location sent as `location` and the
// reply language sent as `language` with every /api/chat request.
// The backend uses `location` as a fallback when the question itself
// doesn't name a place.

const QUICK_LOCATIONS = ["Hyderabad", "Mumbai", "Delhi", "Bengaluru", "Chennai"];

// `value` is what the backend receives (it goes straight into the LLM prompt).
const LANGUAGES = [
  { value: "English", label: "English" },
  { value: "Hindi", label: "Hindi (हिन्दी)" },
  { value: "Telugu", label: "Telugu (తెలుగు)" },
  { value: "Tamil", label: "Tamil (தமிழ்)" },
  { value: "Spanish", label: "Spanish (Español)" },
  { value: "French", label: "French (Français)" },
];

export default function LocationSelector({ location, setLocation, language, setLanguage }) {
  return (
    <div className="controls">
      <div className="field">
        <label htmlFor="location">Default location</label>
        <input
          id="location"
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="e.g. Hyderabad"
          autoComplete="off"
        />
        <p className="hint">Used when your question doesn't name a place.</p>
        <div className="chips">
          {QUICK_LOCATIONS.map((city) => (
            <button
              type="button"
              key={city}
              className={`chip ${location === city ? "chip-on" : ""}`}
              aria-pressed={location === city}
              onClick={() => setLocation(city)}
            >
              {city}
            </button>
          ))}
        </div>
      </div>

      <div className="field">
        <label htmlFor="language">Reply language</label>
        <select id="language" value={language} onChange={(e) => setLanguage(e.target.value)}>
          {LANGUAGES.map((l) => (
            <option key={l.value} value={l.value}>
              {l.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
