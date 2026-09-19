import { useEffect, useRef, useState } from "react";
import { sendChat } from "../services/api.js";
import Message from "./Message.jsx";

const EXAMPLES = [
  "Will it rain tomorrow?",
  "How hot is it right now?",
  "Any extreme weather coming this week?",
  "How was the weather last week?",
];

let nextId = 0;
const newId = () => ++nextId;

export default function ChatBox({ location, language }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  async function submit(text) {
    const message = text.trim();
    if (!message || loading) return;

    setMessages((m) => [...m, { id: newId(), role: "user", text: message }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChat({ message, location, language });
      setMessages((m) => [
        ...m,
        {
          id: newId(),
          role: "assistant",
          text: data.answer,
          weather: data.weather,
          trace: data.tool_trace,
        },
      ]);
    } catch (err) {
      setMessages((m) => [...m, { id: newId(), role: "assistant", error: true, text: err.message }]);
    } finally {
      setLoading(false);
    }
  }

  function onSubmit(e) {
    e.preventDefault();
    submit(input);
  }

  return (
    <div className="chat">
      <div className="thread" role="log" aria-live="polite">
        {messages.length === 0 && !loading && (
          <div className="empty">
            <h2>Ask about the weather</h2>
            <p>Every answer shows which tool the agent picked and why.</p>
            <div className="examples">
              {EXAMPLES.map((q) => (
                <button type="button" key={q} className="example" onClick={() => submit(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) => (
          <Message key={m.id} message={m} />
        ))}

        {loading && (
          <div className="msg msg-assistant pending" aria-label="Working on your answer">
            <span className="pending-text">Choosing a tool</span>
            <span className="dots" aria-hidden="true">
              <i />
              <i />
              <i />
            </span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form className="composer" onSubmit={onSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about current weather, forecasts, past weather or alerts"
          aria-label="Your question"
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
