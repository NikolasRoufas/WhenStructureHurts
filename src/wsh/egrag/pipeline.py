"""Reconstructed EG-RAG (B4), following Algorithm 1 of the original paper.

RECONSTRUCTED BASELINE. Stage structure, equations and relation set follow the paper.
Everything the paper leaves unspecified (retriever/reranker/NLI/extractor checkpoints,
feature definitions, weights, budgets, prompt) is our choice and listed in
docs/EGRAG_RECONSTRUCTION.md. This is not the original code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..config import ExperimentConfig
from ..data.provenance import gold_units
from ..data.schemas import Claim, Edge, EvidenceBundle, Question
from ..retrieval.reranking import retrieve
from .belief_propagation import claim_features, initial_belief, propagate, query_utility
from .graph_selection import resolve_conflicts, select_subgraph


@dataclass
class EGRAGResources:
    extractor: Any
    relation_classifier: Any
    count_tokens: Any
    dense_encoder: Any = None
    reranker: Any = None
    corpus: Any = None


def claim_relevance(dense_encoder, question: str, claims: list[Claim]) -> dict[str, float] | None:
    if dense_encoder is None or not claims:
        return None
    q = dense_encoder.encode([question], is_query=True)[0]
    d = dense_encoder.encode([c.text for c in claims])
    return {c.claim_id: float(v) for c, v in zip(claims, d @ q)}


def score_and_select(q: Question, claims: list[Claim], edges: list[Edge], passage_relevance: dict[str, float],
                     cfg: ExperimentConfig, res: EGRAGResources, use_edges_for_selection: bool = True
                     ) -> tuple[list[str], dict[str, float], dict[str, float], list, dict]:
    """Eqs. 5-10 on a given claim set: belief, utility, propagation, conflicts, selection."""
    feats = claim_features(claims, edges, q.question, passage_relevance,
                           claim_relevance(res.dense_encoder, q.question, claims))
    b0 = {c: initial_belief(f, cfg.egrag.theta) for c, f in feats.items()}
    u = {c: query_utility(f, cfg.egrag.eta) for c, f in feats.items()}
    b, ptrace = propagate(claims, edges, b0, cfg.egrag)
    conflicts = resolve_conflicts(claims, edges, b, cfg.egrag.conflict_margin)
    sel_edges = edges if use_edges_for_selection else []
    selected, strace = select_subgraph(claims, sel_edges, b, u, q.question, cfg.egrag, res.count_tokens)
    trace = {"propagation": ptrace, "selection": strace, "n_conflict_sets": len(conflicts),
             "belief": {c: round(v, 4) for c, v in b.items()}, "utility": {c: round(v, 4) for c, v in u.items()}}
    return selected, b, u, conflicts, trace


def subset_bundle(q: Question, claims: list[Claim], edges: list[Edge], conflicts, selected: list[str],
                  passages: dict, origin: dict) -> EvidenceBundle:
    keep = set(selected)
    sel_claims = [c for c in claims if c.claim_id in keep]
    sel_claims.sort(key=lambda c: selected.index(c.claim_id))
    pids = []
    for c in sel_claims:
        if c.passage_id not in pids:
            pids.append(c.passage_id)
    cs = []
    for cset in conflicts:
        ids = [x for x in cset.claim_ids if x in keep]
        if len(ids) > 1:
            cs.append(cset.model_copy(update={"claim_ids": ids, "resolution": {k: v for k, v in cset.resolution.items() if k in keep}}))
    return EvidenceBundle(question_uid=q.uid, claims=sel_claims, passages={p: passages[p] for p in pids},
                          passage_order=pids, edges=[e for e in edges if e.source in keep and e.target in keep],
                          conflicts=cs, origin=origin)


class EGRAGPipeline:
    def __init__(self, cfg: ExperimentConfig, res: EGRAGResources):
        self.cfg = cfg
        self.res = res

    def build(self, q: Question) -> tuple[EvidenceBundle, dict]:
        cfg, res = self.cfg, self.res
        got = retrieve(q, cfg.retrieval, method="hybrid", rerank=True, dense_encoder=res.dense_encoder,
                       reranker=res.reranker, corpus=res.corpus)                                  # lines 1-2
        passages = [r.passage for r in got]
        scores = [r.score for r in got]
        lo, hi = min(scores), max(scores)
        prel = {r.passage.passage_id: (r.score - lo) / (hi - lo) if hi > lo else 1.0 for r in got}
        claims, xstats = res.extractor.extract(passages, gold_units(q))                         # line 3
        edges, rstats = res.relation_classifier.classify(claims, q.question)                     # line 4
        selected, b, u, conflicts, trace = score_and_select(q, claims, edges, prel, cfg, res)    # lines 5-8
        bundle = subset_bundle(q, claims, edges, conflicts, selected, {p.passage_id: p for p in passages}, {
            "system": "B4", "evidence_source": "retrieved", "retrieval": "hybrid+rerank",
            "extraction": xstats.get("method"), "relations": rstats.get("classifier"),
            "note": "reconstructed EG-RAG; see reconstruction ledger",
        })
        trace.update({"retrieved": [r.passage.passage_id for r in got], "extraction": xstats, "relations": rstats,
                      "n_claims_total": len(claims), "n_edges_total": len(edges), "n_selected": len(selected)})
        return bundle, trace
