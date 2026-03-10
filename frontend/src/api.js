/**
 * NeuralSketch API client
 * Converts canvas to base64 PNG and POSTs to the FastAPI backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Predict sketch categories from a canvas element.
 * @param {HTMLCanvasElement} canvas
 * @param {number} topK - how many predictions to return
 * @returns {Promise<Array<{label: string, emoji: string, confidence: number, rank: number}>>}
 */
export async function predictSketch(canvas, topK = 5) {
  const imageData = canvas.toDataURL("image/png");

  const response = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageData, top_k: topK }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${response.status}`);
  }

  const data = await response.json();
  return data.predictions;
}

/**
 * Fetch all supported categories.
 * @returns {Promise<Array<{name: string, emoji: string}>>}
 */
export async function fetchCategories() {
  const response = await fetch(`${API_BASE}/categories`);
  if (!response.ok) throw new Error("Failed to fetch categories");
  const data = await response.json();
  return data.categories;
}

/**
 * Health check.
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const r = await fetch(`${API_BASE}/health`);
    if (!r.ok) return false;
    const j = await r.json();
    return j.status === "ok";
  } catch {
    return false;
  }
}
