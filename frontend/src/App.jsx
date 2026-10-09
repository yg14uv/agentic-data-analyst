import { useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [sql, setSql] = useState("");
  const [result, setResult] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [metadata, setMetadata] = useState([]);
  const [attempts, setAttempts] = useState(null);
  const [latency, setLatency] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const sessionId = "frontend-session";

  async function handleSubmit(event) {
    event.preventDefault();

    if (!message.trim()) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed.");
      }

      const data = await response.json();

      setAnswer(data.answer || "");
      setSql(data.sql || "");
      setResult(data.result || null);
      setEvaluation(data.evaluation || null);
      setMetadata(data.metadata || []);
      setAttempts(data.attempts ?? null);
      setLatency(data.latency_ms ?? null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function renderResultTable() {
    if (!result || !result.success) {
      return null;
    }

    const columns = result.columns || [];
    const rows = result.rows || [];

    if (!columns.length) {
      return null;
    }

    return (
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>

          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((value, columnIndex) => (
                  <td key={columnIndex}>
                    {value === null ? "NULL" : String(value)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <div className="app-container">
        <header className="hero">
          <div>
            <p className="eyebrow">AI DATA ANALYST</p>
            <h1>Agentic Data Analyst</h1>
            <p className="subtitle">
              Ask questions in plain English. The agent finds the right metadata,
              generates SQL, queries the database, and evaluates its own answer.
            </p>
          </div>

          <div className="status-badge">
            <span className="status-dot"></span>
            Agent Online
          </div>
        </header>

        <section className="card ask-card">
          <form onSubmit={handleSubmit}>
            <label htmlFor="question">Ask your data</label>

            <textarea
              id="question"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Example: How much money did we make in Canada?"
              rows={4}
            />

            <div className="actions">
              <button type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Ask Agent"}
              </button>

              <span className="hint">
                Session: {sessionId}
              </span>
            </div>
          </form>
        </section>

        {error && (
          <section className="card error-card">
            <strong>Error</strong>
            <p>{error}</p>
          </section>
        )}

        {answer && (
          <>
            <section className="card answer-card">
              <p className="section-label">Answer</p>
              <h2>{answer}</h2>
            </section>

            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-label">Tool attempts</span>
                <strong>{attempts ?? "-"}</strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">Latency</span>
                <strong>
                  {latency !== null
                    ? `${(latency / 1000).toFixed(2)}s`
                    : "-"}
                </strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">Metadata matches</span>
                <strong>{metadata.length}</strong>
              </div>

              <div className="stat-card">
                <span className="stat-label">Judge status</span>
                <strong>
                  {evaluation
                    ? evaluation.passed
                      ? "Passed"
                      : "Failed"
                    : "-"}
                </strong>
              </div>
            </div>
          </>
        )}

        {sql && (
          <section className="card">
            <div className="section-header">
              <div>
                <p className="section-label">Generated SQL</p>
                <h3>Query used by the agent</h3>
              </div>
            </div>

            <pre className="code-block">{sql}</pre>
          </section>
        )}

        {result && (
          <section className="card">
            <div className="section-header">
              <div>
                <p className="section-label">Query result</p>
                <h3>Database output</h3>
              </div>
            </div>

            {renderResultTable()}
          </section>
        )}

        {metadata.length > 0 && (
          <section className="card">
            <div className="section-header">
              <div>
                <p className="section-label">Metadata retrieval</p>
                <h3>Schema selected by vector search</h3>
              </div>
            </div>

            <div className="metadata-list">
              {metadata.map((item) => (
                <div className="metadata-item" key={item.table}>
                  <div>
                    <strong>{item.table}</strong>
                    <p>
                      {item.columns
                        .map((column) => column.name)
                        .join(", ")}
                    </p>
                  </div>

                  <span className="score-pill">
                    score {item.similarity_score}
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}

        {evaluation && (
          <section className="card">
            <div className="section-header">
              <div>
                <p className="section-label">Evaluation</p>
                <h3>LLM-as-a-Judge</h3>
              </div>

              <span
                className={
                  evaluation.passed
                    ? "pass-badge"
                    : "fail-badge"
                }
              >
                {evaluation.passed ? "Passed" : "Failed"}
              </span>
            </div>

            <div className="score-grid">
              <div className="score-card">
                <span>Correctness</span>
                <strong>{evaluation.correctness_score}/5</strong>
              </div>

              <div className="score-card">
                <span>Groundedness</span>
                <strong>{evaluation.groundedness_score}/5</strong>
              </div>

              <div className="score-card">
                <span>SQL relevance</span>
                <strong>{evaluation.sql_relevance_score}/5</strong>
              </div>

              <div className="score-card">
                <span>Overall</span>
                <strong>{evaluation.overall_score}/5</strong>
              </div>
            </div>

            <div className="reason-box">
              <strong>Judge reasoning</strong>
              <p>{evaluation.reason}</p>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

export default App;