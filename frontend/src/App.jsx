import { useState, useEffect } from "react";
import { checkHealth } from "./api";
import Header from "./components/Header";
import Canvas from "./components/Canvas";
import PredictionPanel from "./components/PredictionPanel";
import "./App.css";

export default function App() {
  const [predictions, setPredictions] = useState([]);
  const [isPredicting, setIsPredicting] = useState(false);
  const [online, setOnline] = useState(null);

  useEffect(() => {
    checkHealth().then(setOnline);
    const interval = setInterval(() => checkHealth().then(setOnline), 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      <Header />
      <main className="app-main">
        
        <div className="status-bar glass">
          <div className="status-item">
            <span className="status-value highlight">79.6%</span>
            <span className="status-label">Validation Accuracy</span>
          </div>
          <div className="status-divider" />
          <div className="status-item">
            <span className="status-value">50</span>
            <span className="status-label">Trained Categories</span>
          </div>
          <div className="status-divider" />
          <div className="status-item">
            <span className="status-value">1.2M</span>
            <span className="status-label">Parameters</span>
          </div>
          <div className="status-divider" />
          <div className="status-item">
            <div className={`status-indicator ${online === false ? 'offline' : ''}`} />
            <span className="status-label">
              {online === null ? "Connecting..." : online ? "Backend API Online" : "Backend API Offline"}
            </span>
          </div>
        </div>

        <div className="app-layout">
          
          <section className="canvas-section">
            <Canvas
              onPredictions={setPredictions}
              onPredicting={setIsPredicting}
            />
            <div className="hint-card glass">
              <span className="hint-card-icon">💡</span>
              <span className="hint-card-text">
                Hint: Start drawing! The AI will analyze your strokes in real-time. Try drawing a star or a house.
              </span>
            </div>
          </section>

          
          <section className="panel-section">
            <PredictionPanel
              predictions={predictions}
              isPredicting={isPredicting}
            />
          </section>
        </div>

        
        <div className="features-strip">
          {[
            { icon: "⚡", label: "Real-time Inference", desc: "Less than 50ms latency per stroke" },
            { icon: "🧠", label: "PyTorch CNN", desc: "Trained on Quick, Draw! dataset" },
            { icon: "🎨", label: "Auto-Centering", desc: "Smart crop and scale pipeline" },
            { icon: "📱", label: "Responsive", desc: "Fluent drawing on touch devices" },
          ].map((f) => (
             <div key={f.label} className="feature-chip glass">
              <span className="feature-icon">{f.icon}</span>
              <div>
                <div className="feature-label">{f.label}</div>
                <div className="feature-desc">{f.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
