"""BM25 (Okapi, rank_bm25 defaults k1=1.5, b=0.75) over a question's candidate pool or a shared corpus."""

from __future__ import annotations

from dataclasses import dataclass, field

from rank_bm25 import BM25Okapi

from ..data.schemas import Passage
from ..text import content_tokens


@dataclass
class Retrieved:
    passage: Passage
    score: float
    rank: int
    scores: dict[str, float] = field(default_factory=dict)


def _doc_tokens(p: Passage) -> list[str]:
    return content_tokens(f"{p.title} {p.text}") or ["<empty>"]


def bm25_scores(query: str, passages: list[Passage]) -> list[float]:
    if not passages:
        return []
    bm = BM25Okapi([_doc_tokens(p) for p in passages])
    return [float(s) for s in bm.get_scores(content_tokens(query))]


def rank(passages: list[Passage], scores: list[float], key: str) -> list[Retrieved]:
    # Stable tie-break on original position keeps rankings deterministic.
    order = sorted(range(len(passages)), key=lambda i: (-scores[i], i))
    return [Retrieved(passages[i], scores[i], r, {key: scores[i]}) for r, i in enumerate(order)]


class CorpusIndex:
    """Shared-corpus BM25 index (used for FEVER, whose evidence pool is split-wide)."""

    def __init__(self, passages: list[Passage]):
        self.passages = passages
        self.bm = BM25Okapi([_doc_tokens(p) for p in passages])

    def search(self, query: str, n: int) -> list[Passage]:
        s = self.bm.get_scores(content_tokens(query))
        order = sorted(range(len(s)), key=lambda i: (-s[i], i))[:n]
        return [self.passages[i] for i in order]
