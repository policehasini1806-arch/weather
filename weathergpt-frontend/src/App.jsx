import { useState } from "react";
import ChatBox from "./components/ChatBox.jsx";
import LocationSelector from "./components/LocationSelector.jsx";

export default function App() {
  const [location, setLocation] = useState("Hyderabad");
  const [language, setLanguage] = useState("English");

  return (
    <div className="app">
      <aside className="rail">
        <h1 className="brand">WeatherGPT</h1>
        <LocationSelector
          location={location}
          setLocation={setLocation}
          language={language}
          setLanguage={setLanguage}
        />
      </aside>
      <main className="main">
        <ChatBox location={location} language={language} />
      </main>
    </div>
  );
}
