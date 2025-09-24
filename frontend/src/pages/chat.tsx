import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/router";
import ReactMarkdown from "react-markdown";

export default function Chat() {
  const router = useRouter();
  const pdf_id = Number(router.query.pdf_id);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user_id = localStorage.getItem("user_id");
    if (!token || !user_id) router.push("/login");
    fetchHistory(token, user_id);
  }, [pdf_id]);

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [history]);

  async function fetchHistory(token: string | null, user_id: string | null) {
    if (!token || !user_id || !pdf_id) return;
    const res = await fetch(`https://ask-your-pdf-lslp.onrender.com/chats?user_id=${user_id}&pdf_id=${pdf_id}`, {
      headers: { Authorization: `Bearer ${token}`, "ngrok-skip-browser-warning": "true" },
    });
    const data = await res.json();
    setHistory(data);
  }

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    setAnswer("");
    setError("");
    setLoading(true);
    const token = localStorage.getItem("token");
    const user_id = localStorage.getItem("user_id");
    try {
      const res = await fetch("https://ask-your-pdf-lslp.onrender.com/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          "ngrok-skip-browser-warning": "true"
        },
        body: JSON.stringify({ pdf_id, question, user_id }),
      });
      const text = await res.text();
      let data: any = {};
      try { data = text ? JSON.parse(text) : {}; } catch {}
      if (res.ok) {
        // Clear input and refresh history; rely on history to show latest answer
        setQuestion("");
        setAnswer("");
        fetchHistory(token, user_id);
      } else {
        setError(data?.detail || `Request failed (${res.status})`);
      }
    } catch (err: any) {
      setError("Network error. Please try again.");
    }
    setLoading(false);
  }

  return (
    <div className="container chat-container" style={{ display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
      <div className="chat-history-list" ref={chatHistoryRef} style={{ overflowY: "auto", flexGrow: 1, display: "flex", flexDirection: "column-reverse" }}>
        {[...history].map((chat, i) => (
          <div key={i} className="chat-history-item">
            <div className="chat-bubble chat-bubble-user">
              <div className="chat-avatar chat-avatar-user">🧑</div>
              <div className="chat-bubble-content">
                <span className="chat-question"><b>Q:</b> {chat.question}</span>
              </div>
            </div>
            <div className="chat-bubble chat-bubble-answer">
              <div className="chat-avatar chat-avatar-bot">🤖</div>
              <div className="chat-bubble-content">
                <span className="chat-answer"><b>A:</b> <ReactMarkdown>{chat.answer}</ReactMarkdown></span>
              </div>
            </div>
            <small className="chat-timestamp">{chat.timestamp}</small>
          </div>
        ))}
      </div>
      <form className="chat-form" onSubmit={handleAsk} style={{ marginTop: "auto" }}>
        <div className="chat-input-row">
          <input
            type="text"
            className="chat-input"
            placeholder="Ask a question about your PDF..."
            value={question}
            onChange={e => setQuestion(e.target.value)}
            required
            disabled={loading}
          />
          <button type="submit" className="chat-send-btn" disabled={loading} style={{ opacity: loading ? 0.7 : 1 }}>
            {loading ? "Processing..." : "Ask"}
          </button>
        </div>
      </form>
      {loading && (
        <div className="loader">
          <div className="loader-dot"></div>
          <div className="loader-dot"></div>
          <div className="loader-dot"></div>
        </div>
      )}
      {error && !loading && (
        <div className="chat-error" style={{ color: '#b91c1c', background: '#fee2e2', border: '1px solid #fecaca', padding: 12, borderRadius: 8, marginTop: 12 }}>
          {error}
        </div>
      )}
    </div>
  );
}
