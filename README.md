# Movie Recommender Web App (FastAPI)

## Quick start
1) Copy `movie_recommender_model.h5` into this folder (same level as app.py).
2) Install deps:
```bash
pip install -r requirements.txt
```
3) Run the API:
```bash
uvicorn app:app --reload --port 8000
```
4) Open the UI:
- http://localhost:8000  (frontend)
- http://localhost:8000/docs (interactive API docs)

## Endpoints
- `GET /health` — status and title count
- `GET /titles?q=toy&limit=10` — title suggestions (substring match, case-insensitive)
- `GET /recommend?title=Toy%20Story%20(1995)&k=10` — top-k similar titles

## Files
- `app.py` — FastAPI server + routes
- `recommender.py` — H5 loader + recommend/search
- `static/index.html` — minimal frontend
- `requirements.txt` — deps
"# Movie-recommendation---CINEMATCH-1.0" 
