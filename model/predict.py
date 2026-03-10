"""
Inference helper for the NeuralSketch CNN.
Returns top-k (label, confidence) pairs given a PIL Image or numpy array.
"""

import io
import base64
import numpy as np
from PIL import Image, ImageOps
import torch
import torch.nn.functional as F

from model import get_model
from categories import CATEGORIES, CATEGORY_EMOJIS, NUM_CLASSES

IMG_SIZE = 28

def preprocess_image(image_input) -> torch.Tensor:
    """
    Convert various input types to a (1,1,28,28) float32 tensor.
    Accepts: PIL.Image, numpy array (HxW), base64 string (PNG), or bytes.
    The sketch is expected to be dark strokes on a white background.
    """
    if isinstance(image_input, str):

        image_input = image_input.split(",")[-1]  # strip data URI prefix if present
        image_bytes = base64.b64decode(image_input)
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input)).convert("L")
    elif isinstance(image_input, np.ndarray):
        img = Image.fromarray(image_input.astype(np.uint8)).convert("L")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("L")
    else:
        raise TypeError(f"Unsupported input type: {type(image_input)}")

    img = ImageOps.invert(img)
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)

    arr = np.array(img, dtype=np.float32) / 255.0
    tensor = torch.tensor(arr).unsqueeze(0).unsqueeze(0)  # (1,1,28,28)
    return tensor

def predict(
    image_input,
    model_path: str = None,
    top_k: int = 5,
    model=None,
) -> list[dict]:
    """
    Run inference on a sketch image.

    Returns:
        List of dicts: [{"label": str, "emoji": str, "confidence": float}, ...]
        Sorted by confidence descending.
    """
    if model is None:
        if model_path is None:
            import os
            model_path = os.path.join(
                os.path.dirname(__file__), "weights", "best_model.pth"
            )
        model = get_model(num_classes=NUM_CLASSES, pretrained_path=model_path)

    tensor = preprocess_image(image_input)
    with torch.no_grad():
        logits = model(tensor)
        probs = F.softmax(logits, dim=1)[0]

    top_k = min(top_k, NUM_CLASSES)
    values, indices = torch.topk(probs, top_k)

    results = []
    for val, idx in zip(values.tolist(), indices.tolist()):
        label = CATEGORIES[idx]
        results.append({
            "label": label,
            "emoji": CATEGORY_EMOJIS.get(label, "🎨"),
            "confidence": round(val, 4),
        })
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        sys.exit(1)
    img = Image.open(sys.argv[1])
    results = predict(img)
    print("\nTop-5 Predictions:")
    for r in results:
        bar = "█" * int(r["confidence"] * 30)
        print(f"  {r['emoji']} {r['label']:<15} {bar} {r['confidence']:.1%}")
