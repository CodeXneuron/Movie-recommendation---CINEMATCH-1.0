# recommender.py
import h5py
import numpy as np
from pathlib import Path
from typing import List, Tuple

class H5Recommender:
    def __init__(self, h5_path: str = "models/movie_recommender_model.h5"):
        self.h5_path = h5_path
        self._f = None            # keep file handle open to stream slices
        self.sim_dset = None      # h5py dataset handle (no full load)
        self._load()

    def _load(self):
        path = Path(self.h5_path)
        if not path.exists():
            raise FileNotFoundError(f"H5 file not found: {path}")

        # Keep the file open for the lifetime of the process
        self._f = h5py.File(path, "r")
        # Do NOT read [:] — just keep a handle to the dataset
        self.sim_dset = self._f["similarity_matrix"]   # shape: (N, N)

        # Titles are small; safe to load fully
        titles = self._f["movie_titles"][:]
        if isinstance(titles, np.ndarray) and titles.dtype.kind in ("S", "O"):
            titles = np.array(
                [t.decode("utf-8", errors="ignore") if isinstance(t, (bytes, bytearray)) else str(t)
                 for t in titles],
                dtype=object
            )
        else:
            titles = titles.astype(str)

        self.titles = titles
        self.keys = np.char.lower(np.char.strip(self.titles.astype(str)))

        n_rows, n_cols = self.sim_dset.shape
        if n_rows != n_cols:
            raise ValueError(f"similarity_matrix must be square, got {self.sim_dset.shape}")
        if n_rows != len(self.titles):
            raise ValueError(f"Mismatch: sim size {n_rows} vs titles {len(self.titles)}")

    def recommend(self, title: str, k: int = 10) -> List[Tuple[str, float]]:
        if not title:
            raise ValueError("title is required")
        key = title.lower().strip()
        matches = np.where(self.keys == key)[0]
        if len(matches) == 0:
            return []

        idx = matches[0]

        # Stream only the needed row into memory (1 x N)
        sims = self.sim_dset[idx, :]  # this reads a single row from disk
        # Convert to a NumPy array in RAM for sorting (small)
        sims = np.array(sims, dtype=float)

        order = np.argsort(-sims)
        order = order[order != idx][:k]  # drop self
        return [(self.titles[i], float(sims[i])) for i in order]

    def search_titles(self, q: str, limit: int = 20) -> List[str]:
        q = (q or "").lower().strip()
        if not q:
            return []
        mask = np.char.find(self.keys, q) >= 0
        hits = np.where(mask)[0][:limit]
        return [str(self.titles[i]) for i in hits]

    def close(self):
        if self._f is not None:
            try:
                self._f.close()
            except Exception:
                pass
            self._f = None
            self.sim_dset = None

    def __del__(self):
        self.close()
