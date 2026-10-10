"""Dense retrieval and score fusion (EG-RAG Eq. 2 and reciprocal-rank fusion)."""

from __future__ import annotations

import numpy as np

from ..data.schemas import Passage
from ..models.encoders import DenseEncoder


def dense_scores(encoder: DenseEncoder, query: str, passages: list[Passage]) -> list[float]:
    if not passages:
        return []
    q = encoder.encode([query], is_query=True)[0]
    d = encoder.encode([f"{p.title}. {p.text}" for p in passages])
    return [float(x) for x in d @ q]


def _minmax(x: list[float]) -> list[float]:
    a = np.asarray(x, dtype=float)
    if len(a) == 0:
        return []
    lo, hi = a.min(), a.max()
    return [0.0] * len(a) if hi - lo < 1e-12 else list((a - lo) / (hi - lo))


def weighted_fusion(sparse: list[float], dense: list[float], lam_s: float, lam_d: float) -> list[float]:
    """Eq. 2: s = lam_s * s_sparse + lam_d * s_dense, after per-query min-max normalisation
    (normalisation is our choice; the paper does not specify one)."""
    return [lam_s * s + lam_d * d for s, d in zip(_minmax(sparse), _minmax(dense))]


def rrf_fusion(*score_lists: list[float], k: int = 60) -> list[float]:
    n = len(score_lists[0])
    out = [0.0] * n
    for scores in score_lists:
        order = sorted(range(n), key=lambda i: (-scores[i], i))
        for r, i in enumerate(order):
            out[i] += 1.0 / (k + r + 1)
    return out
