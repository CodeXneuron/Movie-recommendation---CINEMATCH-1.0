# app.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from pathlib import Path
import os
import shutil
import kagglehub  # pip install kagglehub

# ===== Kaggle Model Configuration =====
# Full Kaggle Model ID (from "Use this model" snippet)
KAGGLE_MODEL_ID = "kosaladeshapriya/movie-recommender-system1-0/keras/default"
MODEL_FILENAME = "movie_recommender_model.h5"

def ensure_kaggle_model(h5_path: Path):
    """
    Download the model from Kaggle Models using kagglehub if not already present.
    """
    if h5_path.exists():
        print("[kagglehub] Model already exists locally ✅")
        return

    print(f"[kagglehub] Downloading model: {KAGGLE_MODEL_ID}")
    model_dir = kagglehub.model_download(KAGGLE_MODEL_ID)

    # Find any .h5 file inside the downloaded model directory
    candidates = list(Path(model_dir).rglob("*.h5"))
    if not candidates:
        raise FileNotFoundError(
            f"No .h5 found in {model_dir}. Check the Kaggle model contents."
        )

    src = candidates[0]
    shutil.copy2(src, h5_path)
    print(f"[kagglehub] Model copied to: {h5_path}")

# ===== Import recommender =====
try:
    from recommender import H5Recommender
except ModuleNotFoundError:
    from recommender import H5Recommender  # fallback if your file is named recommend.py

# ===== FastAPI App Setup =====
app = FastAPI(title="Movie Recommender API", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

H5_PATH = MODELS_DIR / MODEL_FILENAME

# Ensure model is available
ensure_kaggle_model(H5_PATH)

# Sanity logs
print("BASE_DIR =", BASE_DIR)
print("STATIC_DIR exists? ->", STATIC_DIR.exists())
print("H5_PATH exists? ->", H5_PATH.exists())

if not STATIC_DIR.exists():
    raise RuntimeError(
        f"Static directory not found: {STATIC_DIR}. "
        f"Create it and put index.html, styles.css, ui.js inside."
    )

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Load the recommender
rec = H5Recommender(h5_path=str(H5_PATH))

class RecommendResp(BaseModel):
    title: str
    score: float

@app.get("/health")
def health():
    return {"status": "ok", "titles": len(rec.titles)}

@app.get("/titles", response_model=List[str])
def titles(q: str = "", limit: int = 20):
    return rec.search_titles(q, limit=limit)

@app.get("/recommend", response_model=List[RecommendResp])
def recommend(title: str, k: int = 10):
    out = rec.recommend(title, k=k)
    if not out:
        raise HTTPException(status_code=404, detail="Title not found. Try /titles?q= for suggestions.")
    return [{"title": t, "score": s} for t, s in out]

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = STATIC_DIR / "index.html"
    if not html_path.exists():
        raise HTTPException(500, f"Missing {html_path.name} in {STATIC_DIR}")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))
