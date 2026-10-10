"""Experiment 0 systems B0-B4 (retrieved-evidence setting).

B0 raw passage RAG       : BM25 top-k passages                               -> R0
B1 reranked passage RAG  : BM25 top rerank_pool -> cross-encoder -> top-k     -> R0
B2 atomic claim RAG      : B1 passages -> claim extraction (flat list)        -> R1
B3 reasoning path RAG    : B2 claims -> heuristic DEPENDS_ON + predicted path -> R3
B4 full EG-RAG           : reconstructed pipeline (egrag.pipeline)            -> R4
B2-B4 share B1's passages for B2/B3, so B2 vs B3 isolates path construction.
"""

from __future__ import annotations

from .data.provenance import gold_units
from .data.schemas import Question
from .egrag.pipeline import EGRAGPipeline, EGRAGResources
from .extraction.relation_classifier import heuristic_depends_on
from .representations.evidence import bundle_from_passages
from .representations.reasoning_paths import predicted_path
from .retrieval.reranking import retrieval_recall, retrieve

SYSTEM_REPRESENTATION = {"B0": "R0", "B1": "R0", "B2": "R1", "B3": "R3", "B4": "R4"}


def build_system_bundle(system: str, q: Question, cfg, res: EGRAGResources):
    trace: dict = {"system": system}
    if system == "B4":
        b, t = EGRAGPipeline(cfg, res).build(q)
        trace.update(t)
        trace["retrieval_recall"] = _recall_from_ids(q, t["retrieved"])
        return b, trace
    rerank = system != "B0"
    got = retrieve(q, cfg.retrieval, method="bm25", rerank=rerank, reranker=res.reranker, corpus=res.corpus)
    trace["retrieved"] = [r.passage.passage_id for r in got]
    trace["retrieval_scores"] = [{k: round(v, 4) for k, v in r.scores.items()} for r in got]
    trace["retrieval_recall"] = retrieval_recall(q, got)
    passages = [r.passage for r in got]
    units = gold_units(q)
    if system in ("B0", "B1"):
        from .extraction.claim_extractor import SentenceClaimExtractor

        claims, _ = SentenceClaimExtractor().extract(passages, units)  # for provenance only; R0 renders passages
        return bundle_from_passages(q, passages, claims, {"system": system, "evidence_source": "retrieved",
                                                          "retrieval": "bm25" + ("+rerank" if rerank else "")}), trace
    claims, xstats = res.extractor.extract(passages, units)
    trace["extraction"] = xstats
    b = bundle_from_passages(q, passages, claims, {"system": system, "evidence_source": "retrieved",
                                                   "retrieval": "bm25+rerank", "extraction": xstats.get("method")})
    if system == "B3":
        b.edges = heuristic_depends_on(claims, q.question)
        predicted_path(b, q.question)
        b.edges = []  # B3 shows order only; edges are used solely to build the path
        trace["path_status"] = b.path_status.value
    return b, trace


def _recall_from_ids(q: Question, ids: list[str]) -> float | None:
    gold = set(q.gold_passage_ids())
    return len(gold & set(ids)) / len(gold) if gold else None
