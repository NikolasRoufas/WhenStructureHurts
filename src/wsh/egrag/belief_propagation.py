"""Initial belief (Eq. 5), query utility (Eq. 6) and damped signed propagation (Eqs. 7-8).

Reconstructed from the paper's equations. The paper does not report feature definitions or
weight values; the choices below are OURS and are configurable:

    r_i   source reliability     : constant 0.5 (no reliability signal available)
    x_i   extraction confidence  : Claim.extraction_confidence
    rho_i retrieval relevance    : min-max normalised retrieval score of the claim's passage
                                   (1.0 for gold-evidence bundles)
    tau_i temporal validity      : 0 if superseded by a SUPERSEDES edge, else 1
    pi_i  provenance diversity   : distinct lineages among {i} + SUPPORTS/DUPLICATE neighbours,
                                   divided by (1 + number of such neighbours)
    srel  semantic relevance     : dense cosine(question, claim) if an encoder is given, else
                                   content-token Jaccard
    h_i   multi-hop contribution : 1 if the claim participates in a DEPENDS_ON edge, else 0
    kappa query-entity coverage  : fraction of question content tokens present in the claim

Eq. 7 (as implemented):
    b_i^{t+1} = sigma( mu*logit(b_i^0) + alpha*sum_{j in N+} w+_ji b_j^t
                       - beta*sum_{j in N-} w-_ji b_j^t - gamma*sum_{j in NT} wT_ji b_j^t )
where N+ = SUPPORTS in-neighbours, N- = CONTRADICTS in-neighbours, NT = claims that
SUPERSEDE i. The sign of the temporal term (negative for the superseded claim) is our
interpretation of "temporal-update neighbors send an adjustment to temporal validity".
Weights: w_ji = conf_ji / (1 + sum of confs of that type into i), divided by the number of
neighbours sharing j's lineage (lineage discount). DUPLICATE neighbours send no message
(they are not independent evidence). Iterate until max|b^{t+1}-b^t| < eps or max_iter.
"""

from __future__ import annotations

import math
from collections import defaultdict

from ..config import EGRAGConfig
from ..data.schemas import Claim, Edge, RelationType
from ..text import content_tokens, jaccard


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def claim_features(claims: list[Claim], edges: list[Edge], question: str, passage_relevance: dict[str, float],
                   relevance: dict[str, float] | None = None) -> dict[str, dict[str, float]]:
    nb: dict[str, set[str]] = defaultdict(set)
    superseded, in_dep = set(), set()
    lin = {c.claim_id: c.lineage_id for c in claims}
    for e in edges:
        if e.relation in (RelationType.SUPPORTS, RelationType.DUPLICATE):
            nb[e.target].add(e.source)
            nb[e.source].add(e.target) if e.relation == RelationType.DUPLICATE else None
        if e.relation == RelationType.SUPERSEDES:
            superseded.add(e.target)
        if e.relation == RelationType.DEPENDS_ON:
            in_dep.update([e.source, e.target])
    qtok = set(content_tokens(question))
    feats = {}
    for c in claims:
        lineages = {c.lineage_id} | {lin[j] for j in nb[c.claim_id] if j in lin}
        ctok = set(content_tokens(c.text + " " + c.title))
        feats[c.claim_id] = {
            "r": 0.5, "x": float(c.extraction_confidence), "rho": float(passage_relevance.get(c.passage_id, 0.0)),
            "tau": 0.0 if c.claim_id in superseded else 1.0,
            "pi": len(lineages) / (1 + len(nb[c.claim_id])),
            "srel": float(relevance[c.claim_id]) if relevance else jaccard(question, c.text),
            "h": 1.0 if c.claim_id in in_dep else 0.0,
            "kappa": len(qtok & ctok) / max(1, len(qtok)),
        }
    return feats


def initial_belief(f: dict[str, float], theta: list[float]) -> float:
    t = theta
    return sigmoid(t[0] + t[1] * f["r"] + t[2] * f["x"] + t[3] * f["rho"] + t[4] * f["tau"] + t[5] * f["pi"])


def query_utility(f: dict[str, float], eta: list[float]) -> float:
    return eta[0] * f["srel"] + eta[1] * f["h"] + eta[2] * f["kappa"]


def _weights(claims: list[Claim], edges: list[Edge], rel: RelationType) -> dict[str, list[tuple[str, float]]]:
    lin = {c.claim_id: c.lineage_id for c in claims}
    incoming: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for e in edges:
        if e.relation == rel and e.source in lin and e.target in lin:
            incoming[e.target].append((e.source, e.confidence))
    out: dict[str, list[tuple[str, float]]] = {}
    for i, lst in incoming.items():
        total = 1.0 + sum(c for _, c in lst)
        per_lineage: dict[str, int] = defaultdict(int)
        for j, _ in lst:
            per_lineage[lin[j]] += 1
        out[i] = [(j, (c / total) / per_lineage[lin[j]]) for j, c in lst]
    return out


def propagate(claims: list[Claim], edges: list[Edge], b0: dict[str, float], cfg: EGRAGConfig) -> tuple[dict[str, float], dict]:
    if not cfg.propagate:
        return dict(b0), {"iterations": 0, "converged": True, "propagation": False}
    wp = _weights(claims, edges, RelationType.SUPPORTS)
    wn = _weights(claims, edges, RelationType.CONTRADICTS)
    wt = _weights(claims, edges, RelationType.SUPERSEDES)
    b = dict(b0)
    delta, it = float("inf"), 0
    for it in range(1, cfg.max_iter + 1):
        nb = {}
        for i in b:
            x = cfg.mu * logit(b0[i])
            x += cfg.alpha * sum(w * b[j] for j, w in wp.get(i, []))
            x -= cfg.beta * sum(w * b[j] for j, w in wn.get(i, []))
            x -= cfg.gamma * sum(w * b[j] for j, w in wt.get(i, []))
            nb[i] = sigmoid(x)
        delta = max((abs(nb[i] - b[i]) for i in b), default=0.0)
        b = nb
        if delta < cfg.eps:
            break
    return b, {"iterations": it, "converged": delta < cfg.eps, "final_delta": delta, "propagation": True}
