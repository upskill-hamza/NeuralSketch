import { useRef, useEffect, useCallback, useState } from "react";
import { predictSketch } from "../api";
import styles from "./Canvas.module.css";

const CANVAS_SIZE = 420;
const BRUSH_SIZES = [
  { size: 3, label: "S" },
  { size: 6, label: "M" },
  { size: 12, label: "L" },
];
const DEBOUNCE_MS = 500;

export default function Canvas({ onPredictions, onPredicting }) {
  const canvasRef = useRef(null);
  const isDrawing = useRef(false);
  const lastPos = useRef(null);
  const historyRef = useRef([]);
  const debounceTimer = useRef(null);

  const [hasStrokes, setHasStrokes] = useState(false);
  const [activeDrawing, setActiveDrawing] = useState(false);
  const [brushIndex, setBrushIndex] = useState(1); // M default
  const [status, setStatus] = useState("idle");

  const getPos = (e, canvas) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const src = e.touches ? e.touches[0] : e;
    return {
      x: (src.clientX - rect.left) * scaleX,
      y: (src.clientY - rect.top) * scaleY,
    };
  };

  const getCtx = () => {
    const canvas = canvasRef.current;
    return canvas ? canvas.getContext("2d") : null;
  };

  const saveSnapshot = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    historyRef.current.push(canvas.toDataURL());
    if (historyRef.current.length > 30) historyRef.current.shift();
  };

  const triggerPrediction = useCallback(() => {
    clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(async () => {
      const canvas = canvasRef.current;
      if (!canvas || !hasStrokes) return;
      setStatus("predicting");
      onPredicting?.(true);
      try {
        const preds = await predictSketch(canvas);
        onPredictions?.(preds);
        setStatus("done");
      } catch (err) {
        console.error("Prediction error:", err);
        setStatus("error");
      } finally {
        onPredicting?.(false);
      }
    }, DEBOUNCE_MS);
  }, [hasStrokes, onPredictions, onPredicting]);

  const startDraw = useCallback((e) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!ctx || !canvas) return;
    saveSnapshot();
    isDrawing.current = true;
    setActiveDrawing(true);
    lastPos.current = getPos(e, canvas);

    ctx.beginPath();
    ctx.arc(lastPos.current.x, lastPos.current.y, BRUSH_SIZES[brushIndex].size / 2, 0, Math.PI * 2);
    ctx.fillStyle = "#111111";
    ctx.fill();
    setHasStrokes(true);
  }, [brushIndex]);

  const draw = useCallback((e) => {
    e.preventDefault();
    if (!isDrawing.current) return;
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!ctx || !canvas) return;

    const pos = getPos(e, canvas);
    const last = lastPos.current;

    ctx.beginPath();
    ctx.moveTo(last.x, last.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.strokeStyle = "#111111";
    ctx.lineWidth = BRUSH_SIZES[brushIndex].size;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke();

    lastPos.current = pos;
  }, [brushIndex]);

  const stopDraw = useCallback(() => {
    if (!isDrawing.current) return;
    isDrawing.current = false;
    setActiveDrawing(false);
    triggerPrediction();
  }, [triggerPrediction]);

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!ctx || !canvas) return;
    historyRef.current = [];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    setHasStrokes(false);
    setStatus("idle");
    onPredictions?.([]);
    clearTimeout(debounceTimer.current);
  };

  const undo = () => {
    const canvas = canvasRef.current;
    const ctx = getCtx();
    if (!ctx || !canvas || historyRef.current.length === 0) return;
    const prev = historyRef.current.pop();
    const img = new Image();
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
    };
    img.src = prev;
    if (historyRef.current.length === 0) {
      setHasStrokes(false);
      onPredictions?.([]);
    }
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    canvas.addEventListener("mousedown", startDraw);
    canvas.addEventListener("mousemove", draw);
    canvas.addEventListener("mouseup", stopDraw);
    canvas.addEventListener("mouseleave", stopDraw);
    canvas.addEventListener("touchstart", startDraw, { passive: false });
    canvas.addEventListener("touchmove", draw, { passive: false });
    canvas.addEventListener("touchend", stopDraw);
    return () => {
      canvas.removeEventListener("mousedown", startDraw);
      canvas.removeEventListener("mousemove", draw);
      canvas.removeEventListener("mouseup", stopDraw);
      canvas.removeEventListener("mouseleave", stopDraw);
      canvas.removeEventListener("touchstart", startDraw);
      canvas.removeEventListener("touchmove", draw);
      canvas.removeEventListener("touchend", stopDraw);
    };
  }, [startDraw, draw, stopDraw]);

  return (
    <div className={styles.canvasWrapper}>
      <div className={styles.canvasCard}>
        <span className={styles.canvasTitle}>🎨 Drawing Canvas</span>

        <div className={`${styles.canvasContainer} ${activeDrawing ? styles.drawing : styles.idle}`}>
          <canvas
            ref={canvasRef}
            width={CANVAS_SIZE}
            height={CANVAS_SIZE}
            id="sketch-canvas"
          />
          <div className={`${styles.canvasHint} ${hasStrokes ? styles.hidden : ""}`}>
            <span className={styles.hintIcon}>✏️</span>
            <span className={styles.hintText}>Draw anything here…</span>
          </div>
        </div>

        
        <div className={styles.brushControls}>
          <span className={styles.brushLabel}>Brush:</span>
          <div className={styles.brushSizes}>
            {BRUSH_SIZES.map((b, i) => (
              <button
                key={i}
                className={`${styles.brushBtn} ${brushIndex === i ? styles.active : ""}`}
                style={{ width: 28 + i * 8, height: 28 + i * 8 }}
                onClick={() => setBrushIndex(i)}
                title={`${b.label} brush`}
              >
                <span
                  className={styles.brushDot}
                  style={{ width: b.size, height: b.size }}
                />
              </button>
            ))}
          </div>
          <span className={`${styles.statusText} ${status === "predicting" ? styles.predicting : ""}`}>
            {status === "predicting"
              ? "⚡ Classifying…"
              : status === "done"
              ? "✓ Done"
              : status === "error"
              ? "⚠ Server error"
              : hasStrokes
              ? "Release to classify"
              : ""}
          </span>
        </div>

        
        <div className={styles.canvasControls}>
          <button
            className={`${styles.btn} ${styles.btnUndo}`}
            onClick={undo}
            disabled={!hasStrokes}
            id="btn-undo"
          >
            ↩ Undo
          </button>
          <button
            className={`${styles.btn} ${styles.btnClear}`}
            onClick={clearCanvas}
            disabled={!hasStrokes}
            id="btn-clear"
          >
            🗑 Clear
          </button>
        </div>
      </div>
    </div>
  );
}
