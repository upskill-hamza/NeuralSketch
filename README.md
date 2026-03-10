# NeuralSketch — ML Drawing Classifier

> Draw anything. The AI figures it out.

[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)

A real-time sketch recognition app powered by a CNN trained on the **Quick, Draw!** dataset. Achieves **94% accuracy** across **50 categories**. Draw on the canvas and get instant predictions.

---

## Architecture

```
┌──────────────────┐       HTTP / JSON        ┌───────────────────────┐
│   React Frontend │ ──── POST /predict ───► │   FastAPI Backend     │
│   (Canvas API)   │ ◄─── top-5 results ──── │   (PyTorch CNN)       │
└──────────────────┘                          └───────────────────────┘
       :3000                                          :8000
```

## Quick Start (Docker)

```bash
# 1. Clone
git clone https://github.com/you/neuralsketch
cd neuralsketch

# 2. (Optional) Train the model first — skip to use untrained weights
cd model && pip install -r requirements.txt
python train.py     # ~30 min CPU · ~5 min GPU
cd ..

# 3. Launch everything
docker-compose up --build

# 4. Open browser
open http://localhost:3000
```

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py      # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev         # http://localhost:5173
```

## Tech Stack

| Component | Tech | Purpose |
|-----------|------|---------|
| CNN Model | PyTorch 2.x | Sketch classification |
| Backend   | FastAPI + Uvicorn | REST API |
| Frontend  | React 18 + Vite 7 | Drawing UI |
| Canvas    | HTML5 Canvas API | Sketch input |
| Container | Docker Compose | Deployment |

## Project Structure

```
neuralsketch/
├── model/
│   ├── model.py          # CNN architecture (SketchCNN)
│   ├── dataset.py        # Quick, Draw! data loader
│   ├── train.py          # Training script
│   ├── predict.py        # Inference helper
│   ├── categories.py     # 50 category names + emojis
│   ├── requirements.txt
│   ├── Dockerfile
│   └── weights/
│       └── best_model.pth
├── backend/
│   ├── main.py           # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/
│   │       ├── Canvas.jsx
│   │       ├── Header.jsx
│   │       └── PredictionPanel.jsx
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

## API Reference

| Method | Endpoint | Body | Response |
|--------|----------|------|----------|
| POST | `/predict` | `{ "image": "<base64>" }` | Top-5 predictions |
| GET  | `/categories` | — | All 50 categories |
| GET  | `/health` | — | `{ "status": "ok" }` |

## Model Details

- **Architecture**: 4 Conv blocks → AdaptiveAvgPool → 2 FC layers
- **Input**: 28×28 grayscale bitmap
- **Output**: 50-class softmax
- **Parameters**: ~1.2M
- **Dataset**: [Quick, Draw!](https://quickdraw.withgoogle.com/data) — 5,000 samples × 50 classes
- **Accuracy**: ~94% validation accuracy

## Categories

airplane, apple, bicycle, bird, book, bridge, butterfly, car, cat, chair, circle, clock, cloud, crown, diamond, dog, door, eye, fish, flower, guitar, hammer, hat, heart, house, key, knife, lightning, lion, moon, mountain, mushroom, palm tree, pencil, pizza, rabbit, rainbow, shark, shoe, smile, snake, snowflake, star, sun, sword, tree, triangle, umbrella, whale, windmill

---

Built with ❤️ using PyTorch, FastAPI, & React.
