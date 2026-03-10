"""
NeuralSketch FastAPI Backend
Endpoints:
  POST /predict       — Returns top-5 sketch predictions
  GET  /categories    — Lists all 50 category names
  GET  /health        — Health check
"""

import os
import sys
import io
import base64
import logging
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
from PIL import Image, ImageOps
import torch
import torch.nn.functional as F
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
sys.path.insert(0, MODEL_DIR)

from model import get_model  # noqa: E402
from categories import CATEGORIES, CATEGORY_EMOJIS, NUM_CLASSES  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neuralsketch")

IMG_SIZE = 28
WEIGHTS_PATH = os.path.join(MODEL_DIR, "weights", "best_model.pth")

_model: Optional[torch.nn.Module] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    if os.path.exists(WEIGHTS_PATH):
        logger.info(f"Loading model weights from {WEIGHTS_PATH}")
        _model = get_model(num_classes=NUM_CLASSES, pretrained_path=WEIGHTS_PATH)
    else:
        logger.warning(
            "No pretrained weights found — using untrained model. "
            "Run model/train.py to train the model."
        )
        _model = get_model(num_classes=NUM_CLASSES)
    _model.eval()
    logger.info("Model ready.")
    yield
    logger.info("Shutting down.")

app = FastAPI(
    title="NeuralSketch API",
    description="Real-time sketch recognition powered by a CNN trained on Quick, Draw!",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    image: str  # base64-encoded PNG (data URI or raw base64)
    top_k: int = 5

class Prediction(BaseModel):
    label: str
    emoji: str
    confidence: float
    rank: int

class PredictResponse(BaseModel):
    predictions: list[Prediction]
    model_loaded: bool

def decode_image(b64: str) -> torch.Tensor:
    """Decode base64 image → (1,1,28,28) float32 tensor."""

    if "," in b64:
        b64 = b64.split(",", 1)[1]
    img_bytes = base64.b64decode(b64)

    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

    bg = Image.new("RGBA", img.size, "WHITE")
    bg.paste(img, (0, 0), img)

    img_gray = bg.convert("L")

    img_inverted = ImageOps.invert(img_gray)

    bbox = img_inverted.getbbox()
    if bbox:

        img_cropped = img_inverted.crop(bbox)

        max_dim = max(img_cropped.size)
        pad_size = int(max_dim * 1.2)

        img_square = Image.new("L", (pad_size, pad_size), 0)
        offset = ((pad_size - img_cropped.width) // 2, (pad_size - img_cropped.height) // 2)
        img_square.paste(img_cropped, offset)

        img_resized = img_square.resize((IMG_SIZE, IMG_SIZE), Image.Resampling.LANCZOS)
    else:

        img_resized = Image.new("L", (IMG_SIZE, IMG_SIZE), 0)
    
    arr = np.array(img_resized, dtype=np.float32) / 255.0
    tensor = torch.tensor(arr).unsqueeze(0).unsqueeze(0)  # (1,1,28,28)
    return tensor

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model is not None}

@app.get("/categories")
def categories():
    return {
        "categories": [
            {"name": cat, "emoji": CATEGORY_EMOJIS.get(cat, "🎨")}
            for cat in CATEGORIES
        ]
    }

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not req.image:
        raise HTTPException(status_code=400, detail="No image provided")

    try:
        tensor = decode_image(req.image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    top_k = max(1, min(req.top_k, NUM_CLASSES))

    with torch.no_grad():
        logits = _model(tensor)
        probs = F.softmax(logits, dim=1)[0]

    values, indices = torch.topk(probs, top_k)

    predictions = []
    for rank, (val, idx) in enumerate(zip(values.tolist(), indices.tolist()), start=1):
        label = CATEGORIES[idx]
        predictions.append(
            Prediction(
                label=label,
                emoji=CATEGORY_EMOJIS.get(label, "🎨"),
                confidence=round(val, 4),
                rank=rank,
            )
        )

    return PredictResponse(
        predictions=predictions,
        model_loaded=os.path.exists(WEIGHTS_PATH),
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
