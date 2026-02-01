import { useMemo, useState } from "react";

type ToolResult = {
  name: string;
  ok: boolean;
  error?: string | null;
  latency_ms?: number;
};

type AgentResult = {
  run_id: string;
  route: string;
  confidence: number;
  escalate: boolean;
  tool_results: ToolResult[];
  session_state?: {
    history?: Array<{ route: string; timestamp: number }>;
  };
};

type TraceEvent = {
  event_type: string;
  message: string;
  timestamp: number;
  data: Record<string, unknown>;
};

type HistoryItem = {
  runId: string;
  ticket: string;
  route: string;
  createdAt: string;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

const pretty = (value: unknown) => JSON.stringify(value, null, 2);

function formatTime(ts: number) {
  return new Date(ts * 1000).toLocaleTimeString();
}

export default function App() {
  const [ticket, setTicket] = useState("");
  const [correlationId, setCorrelationId] = useState("");
  const [idempotencyKey, setIdempotencyKey] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [result, setResult] = useState<AgentResult | null>(null);
  const [trace, setTrace] = useState<TraceEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const historyEmpty = history.length === 0;

  const toolSummary = useMemo(() => {
    if (!result?.tool_results) return "No tool results yet.";
    const failed = result.tool_results.filter((tool) => !tool.ok);
    if (failed.length === 0) return "All tools succeeded.";
    return `${failed.length} tool(s) failed.`;
  }, [result]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setTrace([]);

    try {
      const response = await fetch(`${API_BASE}/api/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticket,
          correlation_id: correlationId || undefined,
          idempotency_key: idempotencyKey || undefined,
        }),
      });
      const raw = await response.text();
      if (!raw) {
        throw new Error("API returned empty response. Is the server running?");
      }
      const payload = JSON.parse(raw) as AgentResult;
      if (!response.ok) {
        throw new Error((payload as unknown as { error?: string }).error ?? response.statusText);
      }
      setResult(payload);
      setHistory((prev) => [
        {
          runId: payload.run_id,
          ticket,
          route: payload.route,
          createdAt: new Date().toLocaleTimeString(),
        },
        ...prev,
      ]);
      const traceResp = await fetch(`${API_BASE}/api/trace?run_id=${payload.run_id}`);
      const traceRaw = await traceResp.text();
      if (!traceRaw) {
        throw new Error("Trace API returned empty response.");
      }
      const tracePayload = JSON.parse(traceRaw) as { events?: TraceEvent[] };
      setTrace(tracePayload.events ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const selectHistory = async (item: HistoryItem) => {
    setLoading(true);
    setError(null);
    try {
      const traceResp = await fetch(`${API_BASE}/api/trace?run_id=${item.runId}`);
      const traceRaw = await traceResp.text();
      if (!traceRaw) {
        throw new Error("Trace API returned empty response.");
      }
      const tracePayload = JSON.parse(traceRaw) as { events?: TraceEvent[] };
      setTrace(tracePayload.events ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>Mini Agent Runtime</h1>
          <p>History</p>
        </div>
        {historyEmpty ? (
          <div className="sidebar-empty">Run a ticket to populate history.</div>
        ) : (
          <ul className="history-list">
            {history.map((item) => (
              <li key={item.runId}>
                <button
                  type="button"
                  className="history-item"
                  onClick={() => selectHistory(item)}
                >
                  <div className="history-title">{item.route}</div>
                  <div className="history-meta">{item.createdAt}</div>
                  <div className="history-ticket">{item.ticket}</div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>

      <main className="content">
        <header className="content-header">
          <h2>Runtime Console</h2>
          <p>Route tickets, call tools, and inspect traces.</p>
        </header>

        <section className="card">
          <form onSubmit={handleSubmit} className="form">
            <label>
              Ticket
              <textarea
                rows={4}
                value={ticket}
                onChange={(event) => setTicket(event.target.value)}
                placeholder="Example: API latency spike on payments service, check DB incidents"
                required
              />
            </label>
            <div className="row">
              <label>
                Correlation ID
                <input
                  value={correlationId}
                  onChange={(event) => setCorrelationId(event.target.value)}
                  placeholder="optional"
                />
              </label>
              <label>
                Idempotency Key
                <input
                  value={idempotencyKey}
                  onChange={(event) => setIdempotencyKey(event.target.value)}
                  placeholder="optional"
                />
              </label>
            </div>
            <button type="submit" disabled={loading}>
              {loading ? "Running..." : "Run ticket"}
            </button>
          </form>
          {error ? <p className="error">{error}</p> : null}
        </section>

        <section className="grid">
          <div className="card">
            <h3>Result</h3>
            <div className="badge-row">
              <span className="badge">{result?.route ?? "no route"}</span>
              <span className="badge">
                confidence {result ? result.confidence.toFixed(2) : "--"}
              </span>
              <span className={`badge ${result?.escalate ? "badge-warn" : ""}`}>
                {result?.escalate ? "escalate" : "no escalation"}
              </span>
            </div>
            <p className="muted">{toolSummary}</p>
            <pre>{result ? pretty(result) : "Run a ticket to see output."}</pre>
          </div>
          <div className="card">
            <h3>Trace events</h3>
            {trace.length === 0 ? (
              <p className="muted">Trace events will appear here.</p>
            ) : (
              <ul className="trace-list">
                {trace.map((event, idx) => (
                  <li key={`${event.event_type}-${idx}`} className="trace-item">
                    <div className="trace-head">
                      <span className="trace-type">{event.event_type}</span>
                      <span className="trace-time">{formatTime(event.timestamp)}</span>
                    </div>
                    <div className="trace-message">{event.message}</div>
                    <pre>{pretty(event.data)}</pre>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
