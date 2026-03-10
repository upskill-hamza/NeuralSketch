import { useState } from "react";
import styles from "./PredictionPanel.module.css";

const ALL_CATEGORIES = [
  "airplane", "apple", "bicycle", "bird", "book", "bridge", "butterfly", "car", "cat", "chair",
  "circle", "clock", "cloud", "crown", "diamond", "dog", "door", "eye", "fish", "flower",
  "guitar", "hammer", "hat", "bear", "house", "key", "knife", "lightning", "lion", "moon",
  "mountain", "mushroom", "palm tree", "pencil", "pizza", "rabbit", "rainbow", "shark", "shoe", "frog",
  "snake", "snowflake", "star", "sun", "sword", "tree", "triangle", "umbrella", "whale", "windmill"
];

const SAMPLE_CATEGORIES = ALL_CATEGORIES.slice(0, 8);

const BAR_COLORS = [
  "linear-gradient(90deg, #7c5bff, #a78bfa)",
  "linear-gradient(90deg, #22d3ee, #67e8f9)",
  "linear-gradient(90deg, #f472b6, #fb7185)",
  "linear-gradient(90deg, #34d399, #6ee7b7)",
  "linear-gradient(90deg, #fbbf24, #fcd34d)",
];

export default function PredictionPanel({ predictions, isPredicting }) {
  const [expanded, setExpanded] = useState(false);
  const top = predictions?.[0];

  return (
    <div className={styles.panel}>
      <div className={styles.panelHeader}>
        <span className={styles.panelTitle}>🧠 AI Predictions</span>
      </div>

      {/* Winner Card */}
      <div className={styles.topPrediction}>
        {isPredicting ? (
          <div className={styles.loadingState}>
            <div className={styles.pulse} />
            <div className={styles.pulse} />
            <div className={styles.pulse} />
          </div>
        ) : top ? (
          <>
            <span key={top.label + "-emoji"} className={styles.topEmoji}>
              {top.emoji}
            </span>
            <span key={top.label + "-label"} className={styles.topLabel}>
              {top.label}
            </span>
            <span className={styles.topConf}>
              {(top.confidence * 100).toFixed(1)}% confidence
            </span>
          </>
        ) : (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>🎯</span>
            <span className={styles.emptyText}>Draw something to classify</span>
          </div>
        )}
      </div>

      {/* Top-5 bars */}
      <div className={styles.predictions}>
        {isPredicting
          ? Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className={styles.predictionItem} style={{ opacity: 0.3 }}>
                <span className={styles.rank}>#{i + 1}</span>
                <span className={styles.predEmoji}>…</span>
                <div className={styles.predInfo}>
                  <div className={styles.predMeta}>
                    <span className={styles.predLabel}>Classifying…</span>
                  </div>
                  <div className={styles.barTrack}>
                    <div
                      className={styles.barFill}
                      style={{
                        width: `${Math.max(5, 60 - i * 12)}%`,
                        background: BAR_COLORS[i],
                        opacity: 0.4,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))
          : predictions?.length > 0
          ? predictions.map((pred, i) => (
              <div key={pred.label + i} className={styles.predictionItem}>
                <span className={styles.rank}>#{pred.rank}</span>
                <span className={styles.predEmoji}>{pred.emoji}</span>
                <div className={styles.predInfo}>
                  <div className={styles.predMeta}>
                    <span className={styles.predLabel}>{pred.label}</span>
                    <span className={styles.predConf}>
                      {(pred.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className={styles.barTrack}>
                    <div
                      className={styles.barFill}
                      style={{
                        width: `${pred.confidence * 100}%`,
                        background: BAR_COLORS[i % BAR_COLORS.length],
                      }}
                    />
                  </div>
                </div>
              </div>
            ))
          : null}
      </div>

      {/* Footer tags */}
      <div className={styles.panelFooter}>
        {(expanded ? ALL_CATEGORIES : SAMPLE_CATEGORIES).map((cat) => (
          <span key={cat} className={styles.tag}>
            {cat}
          </span>
        ))}
        {!expanded ? (
          <span 
            className={styles.tag} 
            style={{ cursor: "pointer", background: "rgba(255,255,255,0.1)", fontWeight: "500" }}
            onClick={() => setExpanded(true)}
          >
            +42 more
          </span>
        ) : (
          <span 
            className={styles.tag} 
            style={{ cursor: "pointer", background: "rgba(255,255,255,0.1)", fontWeight: "500" }}
            onClick={() => setExpanded(false)}
          >
            Show less
          </span>
        )}
      </div>
    </div>
  );
}
