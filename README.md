# Movie Recommender Web App (FastAPI)
<img width="1919" height="895" alt="image" src="https://github.com/user-attachments/assets/c728d553-1fe7-44f7-8ba1-f9038a693389" />

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

Perfect 👍 — here’s a **ready-to-paste section** for your GitHub README.md that clearly lists every problem you ran into and the fixes we implemented.
I’ve formatted it in Markdown so you can drop it straight in.

---

## ⚙️ Troubleshooting Journey

### 🧩 1. Git not detecting project as a repository

**Issue:**
`fatal: not a git repository (or any of the parent directories): .git`
**Cause:**  The project folder wasn’t initialized for Git.
**Fix:**

```bash
git init
git add .
git commit -m "Initial commit"
```

---

### 🧩 2. Push blocked by GitHub 100 MB limit

**Issue:**
`File movie_recommender_model.h5 is 724.67 MB; this exceeds GitHub's file size limit`
**Cause:**  GitHub cannot store files > 100 MB.
**Fix:**
Removed the model from version control and ignored all `.h5` files:

```bash
git rm --cached movie_recommender_model.h5
echo "*.h5" >> .gitignore
git add .gitignore
git commit -m "Remove large model file and ignore future .h5 files"
```

---

### 🧩 3. Large file still blocking push (old commits contained it)

**Issue:**
GitHub continued to reject pushes after removing the file.
**Cause:**  The `.h5` blob was still in Git history.
**Fix:**
Used **git-filter-repo** to purge it completely:

```bash
pip install git-filter-repo
git filter-repo --path "movie_recommender_model.h5" --invert-paths
git push origin --force
```

---

### 🧩 4. Need the model but can’t host it on GitHub

**Decision:**
Upload the trained model to **Kaggle Models** instead of GitHub.
**Fix:**
Integrated automatic download with `kagglehub`:

```python
import kagglehub
model_dir = kagglehub.model_download(
    "kosaladeshapriya/movie-recommender-system1-0/keras/default"
)
```

On startup the API fetches the model into `/models/movie_recommender_model.h5`.

---

### 🧩 5. `fatal: not found` / `Invalid model handle` from kagglehub

**Cause:**  Used only the model name, missing framework/variation path.
**Fix:**  Copied the full handle from Kaggle’s **“Use this model → Python”** snippet:
`kosaladeshapriya/movie-recommender-system1-0/keras/default`

---

### 🧩 6. Heroku not recognizing the web process

**Issue:**
`Error: Couldn't find that process type (web)`
**Cause:**  Procfile missing or lowercase (`procfile` instead of `Procfile`).
**Fix:**
Created a properly-named root-level file:

```
Procfile
└─ web: uvicorn app:app --host 0.0.0.0 --port $PORT
```

then committed and redeployed.

---

### 🧩 7. Heroku “Application Error” / H14

**Cause:**  No running dyno because the Procfile wasn’t in the deployed commit.
**Fix:**
Re-pushed with:

```bash
git add Procfile
git commit -m "Add Procfile"
git push heroku HEAD:main
heroku ps:scale web=1
```

---

### 🧩 8. App crashed (R15 – Memory quota exceeded)

**Issue:**
Heroku logs showed:
`Process running mem=1591M(310%) → Error R15 (Memory quota vastly exceeded)`
**Cause:**  The 724 MB `.h5` model loaded an entire similarity matrix into RAM.
**Fix A (short-term):**
Upgraded to a higher-memory **Eco dyno**:

```bash
heroku ps:type eco -a bloodcurdling-cat-20659
```

**Fix B (permanent, free-tier friendly):**
Re-wrote `recommender.py` to **stream** only one row of the matrix from HDF5 at a time:

```python
self._f = h5py.File(path, "r")
self.sim_dset = self._f["similarity_matrix"]       # handle only
sims = self.sim_dset[idx, :]                       # read single row
```

and limited Uvicorn to one worker:

```
web: uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1
```

→ Memory usage dropped from >1.5 GB to ~200 MB.

---

### 🧩 9. Static homepage 500 error

**Cause:**  `/static/index.html` missing.
**Fix:**  Added a minimal HTML page in `static/index.html` to satisfy the root route.

---

### ✅ Final State

* Deployed successfully on **Heroku** as
  **[https://bloodcurdling-cat-20659.herokuapp.com](https://bloodcurdling-cat-20659.herokuapp.com)**
* Auto-downloads Kaggle model on startup
* Serves endpoints `/health`, `/titles`, `/recommend`
* Stable under memory limits with lazy HDF5 loading

---

You can drop this entire block into your README under a heading like
`## 🧠 Troubleshooting and Fixes` — it’s clear, complete, and documents your real deployment journey.
