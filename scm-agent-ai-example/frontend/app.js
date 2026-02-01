const { useEffect, useMemo, useState } = React;

const STORAGE_KEY = "scm_chat_sessions";
const ACTIVE_KEY = "scm_chat_active";
const SIDEBAR_KEY = "scm_chat_sidebar_open";

const createSession = () => ({
  id: `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
  title: "New chat",
  messages: [],
  updatedAt: Date.now(),
});

const saveSessions = (sessions) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
};

const loadSessions = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

const toDomain = (value) => {
  if (!value) return "";
  try {
    const url = value.startsWith("http") ? new URL(value) : new URL(`https://${value}`);
    return url.hostname.replace(/^www\./, "");
  } catch {
    return value;
  }
};

const renderMarkdown = (text) => {
  if (!text) return "";
  if (!window.marked) return text.replaceAll("\n", "<br />");
  return window.marked.parse(text, { breaks: true });
};

function App() {
  const [sessions, setSessions] = useState(() => {
    const saved = loadSessions();
    return saved.length ? saved : [createSession()];
  });
  const [activeId, setActiveId] = useState(() => {
    const saved = loadSessions();
    const stored = localStorage.getItem(ACTIVE_KEY);
    if (stored && saved.find((s) => s.id === stored)) return stored;
    return saved.length ? saved[0].id : null;
  });
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    const stored = localStorage.getItem(SIDEBAR_KEY);
    return stored ? stored === "true" : true;
  });
  const [input, setInput] = useState("");
  const [topK, setTopK] = useState(3);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState("checking");

  const suggestedPrompts = [
    "What is OTIF and how is it measured?",
    "Explain safety stock with a simple formula.",
    "What is the difference between S&OP and demand forecasting?",
    "How do you calculate reorder point?",
    "Give 5 key logistics KPIs.",
  ];

  const activeSession = useMemo(
    () => sessions.find((s) => s.id === activeId) || sessions[0],
    [sessions, activeId]
  );

  useEffect(() => {
    saveSessions(sessions);
  }, [sessions]);

  useEffect(() => {
    if (activeId) {
      localStorage.setItem(ACTIVE_KEY, activeId);
    }
  }, [activeId]);

  useEffect(() => {
    localStorage.setItem(SIDEBAR_KEY, String(sidebarOpen));
  }, [sidebarOpen]);

  useEffect(() => {
    fetch("/health")
      .then((res) => res.json())
      .then((data) => {
        setHealth(
          `ok | supply=${data.indexes.supply} demand=${data.indexes.demand}`
        );
      })
      .catch(() => setHealth("unavailable"));
  }, []);

  const createNewChat = () => {
    const fresh = createSession();
    setSessions((prev) => [fresh, ...prev]);
    setActiveId(fresh.id);
    setInput("");
  };

  const clearAllHistory = () => {
    const ok = window.confirm("Delete all chat history?");
    if (!ok) return;
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(ACTIVE_KEY);
    const fresh = createSession();
    setSessions([fresh]);
    setActiveId(fresh.id);
    setInput("");
  };

  const updateSession = (sessionId, updater) => {
    setSessions((prev) =>
      prev.map((session) =>
        session.id === sessionId ? updater(session) : session
      )
    );
  };

  const handleSend = async () => {
    const question = input.trim();
    if (!question || loading || !activeSession) return;

    const userMessage = { role: "user", text: question };
    const updatedTitle =
      activeSession.messages.length === 0 ? question.slice(0, 20) : activeSession.title;

    updateSession(activeSession.id, (session) => ({
      ...session,
      title: updatedTitle || session.title,
      messages: [...session.messages, userMessage],
      updatedAt: Date.now(),
    }));

    setInput("");
    setLoading(true);

    try {
      const response = await fetch("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question, top_k: topK }),
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const data = await response.json();
      const assistantMessage = {
        role: "assistant",
        text: data.answer || "",
        sources: data.sources || [],
      };

      updateSession(activeSession.id, (session) => ({
        ...session,
        messages: [...session.messages, assistantMessage],
        updatedAt: Date.now(),
      }));
    } catch (error) {
      updateSession(activeSession.id, (session) => ({
        ...session,
        messages: [
          ...session.messages,
          { role: "assistant", text: "요청에 실패했어요. 다시 시도해 주세요." },
        ],
        updatedAt: Date.now(),
      }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`app-shell ${sidebarOpen ? "sidebar-open" : ""}`}>
      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-header">
          <button className="new-chat" onClick={createNewChat}>
            + New chat
          </button>
        </div>
        <div className="sidebar-section">
          <div className="section-title">Today</div>
          <button className="clear-chat" onClick={clearAllHistory}>
            Clear all
          </button>
          <div className="session-list">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${
                  session.id === activeId ? "active" : ""
                }`}
                onClick={() => setActiveId(session.id)}
              >
                {session.title || "New chat"}
              </div>
            ))}
          </div>
        </div>
      </aside>
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      <main className="main">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="menu-button"
              aria-label="menu"
              onClick={() => setSidebarOpen((prev) => !prev)}
            >
              ☰
            </button>
          </div>
          <div className="topbar-title">SCM Assistant</div>
          <div className="topbar-right">
            <button className="clear-chat" onClick={clearAllHistory}>
              Clear all
            </button>
            <div className="status">Health: {health}</div>
          </div>
        </header>

        <section className="chat-scroll">
          {activeSession?.messages.map((msg, index) => (
            <div
              key={`${msg.role}-${index}`}
              className={`message-row ${msg.role}`}
            >
              {msg.role === "assistant" && <div className="avatar" />}
              <div className={`card ${msg.role}`}>
                {msg.role === "assistant" ? (
                  <div
                    className="markdown"
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.text) }}
                  />
                ) : (
                  msg.text
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    Sources
                    <ul>
                      {msg.sources.map((src, idx) => (
                        <li key={`${src.source}-${idx}`}>
                          <a
                            href={src.source}
                            target="_blank"
                            rel="noreferrer"
                            title={src.source}
                          >
                            {toDomain(src.source)}
                          </a>{" "}
                          (score={src.score?.toFixed?.(3) ?? src.score})
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message-row assistant">
              <div className="avatar" />
              <div className="card assistant">응답 생성 중...</div>
            </div>
          )}
        </section>

        <section className="composer">
          <div className="suggested-prompts">
            {suggestedPrompts.map((prompt) => (
              <button
                key={prompt}
                className="prompt-chip"
                type="button"
                onClick={() => {
                  setInput(prompt);
                }}
              >
                {prompt}
              </button>
            ))}
          </div>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask about inventory, logistics, demand planning, and more."
          />
          <div className="composer-actions">
            <div className="controls">
              Top K
              <input
                type="number"
                min="1"
                max="10"
                value={topK}
                onChange={(event) =>
                  setTopK(parseInt(event.target.value, 10) || 3)
                }
              />
            </div>
            <div className="icon-row">
              <button className="icon-button" aria-label="image">
                🖼️
              </button>
              <button className="send" onClick={handleSend} disabled={loading}>
                {loading ? "Thinking..." : "Send"}
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
