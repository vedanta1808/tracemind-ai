
import { useEffect, useState } from "react";
import "./App.css";

type HealthResponse = {
  status: string;
  project: string;
};

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/v1/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend request failed");
        }
        return response.json() as Promise<HealthResponse>;
      })
      .then(setHealth)
      .catch(() => {
        setError("Cannot connect to the TraceMind backend.");
      });
  }, []);

  return (
    <main className="app">
      <section className="panel">
        <p className="eyebrow">YOUR AI KNOWLEDGE SPACE</p>
        <h1>TraceMind</h1>
        <p className="subtitle">
          Your personal second brain. Ask questions, discover connections,
          and find answers grounded in your documents.
        </p>

        <div className="status">
          <span className={`dot ${health ? "online" : ""}`} />
          <span>
            {health
              ? `${health.project} backend connected`
              : error || "Connecting to backend..."}
          </span>
        </div>

        <div className="feature">
          <h2>Ask your knowledge base</h2>
          <p>
            PDF upload and evidence-backed answers will be added next.
          </p>
          <button disabled>Coming soon</button>
        </div>
      </section>
    </main>
  );
}

export default App;
