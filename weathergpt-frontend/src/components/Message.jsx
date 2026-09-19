import ToolTrace from "./ToolTrace.jsx";
import WeatherCard from "./WeatherCard.jsx";

export default function Message({ message }) {
  if (message.role === "user") {
    return (
      <div className="msg msg-user">
        <p>{message.text}</p>
      </div>
    );
  }

  if (message.error) {
    return (
      <div className="msg msg-error" role="alert">
        <p>{message.text}</p>
      </div>
    );
  }

  return (
    <div className="msg msg-assistant">
      <p className="answer">{message.text}</p>
      <WeatherCard weather={message.weather} tool={message.trace?.tool} />
      <ToolTrace trace={message.trace} />
    </div>
  );
}
