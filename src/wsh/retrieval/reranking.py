"""Cross-encoder reranking and the retrieval entry point used by all systems."""

from __future__ import annotations

from ..config import RetrievalConfig
from ..data.schemas import Passage, Question
from .bm25 import CorpusIndex, Retrieved, bm25_scores, rank
from .dense import dense_scores, rrf_fusion, weighted_fusion


def candidate_pool(q: Question, corpus: CorpusIndex | None, prefilter: int) -> list[Passage]:
    """Distractor-setting datasets: the question's own context. Shared-corpus datasets
    (FEVER): BM25 prefilter over the split-wide pool."""
    if corpus is not None:
        return corpus.search(q.question, prefilter)
    return list(q.passages)


def retrieve(q: Question, cfg: RetrievalConfig, *, method: str | None = None, rerank: bool = False,
             top_k: int | None = None, dense_encoder=None, reranker=None,
             corpus: CorpusIndex | None = None) -> list[Retrieved]:
    method = method or cfg.method
    k = top_k or cfg.top_k
    pool = candidate_pool(q, corpus, cfg.corpus_prefilter)
    sparse = bm25_scores(q.question, pool)
    if method == "bm25":
        ranked = rank(pool, sparse, "bm25")
    else:
        if dense_encoder is None:
            raise ValueError("dense/hybrid retrieval requires a dense encoder")
        dense = dense_scores(dense_encoder, q.question, pool)
        if method == "dense":
            fused = dense
        elif cfg.fusion == "weighted":
            fused = weighted_fusion(sparse, dense, cfg.lambda_sparse, cfg.lambda_dense)
        else:
            fused = rrf_fusion(sparse, dense)
        ranked = rank(pool, fused, method)
        for r in ranked:
            i = pool.index(r.passage)
            r.scores.update({"bm25": sparse[i], "dense": dense[i]})
    if rerank:
        if reranker is None:
            raise ValueError("reranking requires a reranker")
        cand = ranked[: cfg.rerank_pool]
        s = reranker.score(q.question, [f"{r.passage.title}. {r.passage.text}" for r in cand])
        order = sorted(range(len(cand)), key=lambda i: (-s[i], cand[i].rank))
        ranked = [Retrieved(cand[i].passage, s[i], r, {**cand[i].scores, "rerank": s[i], "first_stage_rank": cand[i].rank})
                  for r, i in enumerate(order)]
    return ranked[:k]


def retrieval_recall(q: Question, got: list[Retrieved]) -> float | None:
    gold = set(q.gold_passage_ids())
    if not gold:
        return None
    return len(gold & {r.passage.passage_id for r in got}) / len(gold)
