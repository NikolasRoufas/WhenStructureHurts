"""Conflict resolution (Sec. 3.9) and token-budgeted subgraph selection (Eqs. 9-10).

Conflict sets: connected components over CONTRADICTS/SUPERSEDES edges. Within a set the
claim with the highest propagated belief is 'preferred' if it beats every other member by
more than ``conflict_margin``; superseded claims are 'superseded'; otherwise members are
'unresolved' and rendered as such for the generator.

Selection approximates argmax S(G') with greedy connected expansion:
    gain(i | G') = w_b*b_i + w_u*u_i + w_c*dCoverage + w_p*dProvenance
                   - w_r*Redundancy(i, G') - w_x*(RepeatLineage + Contradiction) - w_l*tokens_i/budget
Seed = best single claim; candidates are graph neighbours of the selection; if none fits,
fall back to the best non-adjacent claim (documented connectivity fallback). Stop when the
best gain <= 0, the token budget or max_claims is reached. ``top_claim`` ranks claims by
w_b*b + w_u*u and ignores the graph (paper's ablation baseline).
"""

from __future__ import annotations

from collections import defaultdict

from ..config import EGRAGConfig
from ..data.schemas import Claim, ConflictSet, Edge, RelationType
from ..text import content_tokens, jaccard


def resolve_conflicts(claims: list[Claim], edges: list[Edge], belief: dict[str, float], margin: float) -> list[ConflictSet]:
    adj: dict[str, set[str]] = defaultdict(set)
    superseded = set()
    for e in edges:
        if e.relation in (RelationType.CONTRADICTS, RelationType.SUPERSEDES):
            adj[e.source].add(e.target)
            adj[e.target].add(e.source)
        if e.relation == RelationType.SUPERSEDES:
            superseded.add(e.target)
    seen, out = set(), []
    for c in claims:
        if c.claim_id in seen or c.claim_id not in adj:
            continue
        comp, stack = [], [c.claim_id]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adj[x] - seen)
        comp.sort()
        res: dict[str, str] = {}
        live = [x for x in comp if x not in superseded]
        for x in comp:
            if x in superseded:
                res[x] = "superseded"
        if live:
            ranked = sorted(live, key=lambda x: -belief.get(x, 0))
            if len(ranked) == 1 or belief[ranked[0]] - belief[ranked[1]] > margin:
                res[ranked[0]] = "preferred"
                for x in ranked[1:]:
                    res[x] = "rejected"
            else:
                for x in ranked:
                    res[x] = "unresolved"
        out.append(ConflictSet(claim_ids=comp, resolution=res))
    return out


def select_subgraph(claims: list[Claim], edges: list[Edge], belief: dict[str, float], utility: dict[str, float],
                    question: str, cfg: EGRAGConfig, count_tokens) -> tuple[list[str], dict]:
    w = cfg.omega
    cm = {c.claim_id: c for c in claims}
    cost = {c.claim_id: count_tokens(c.text) + 8 for c in claims}  # + id/source overhead
    base = {c: w["b"] * belief[c] + w["u"] * utility[c] for c in cm}
    trace = {"selector": cfg.selector, "budget": cfg.token_budget, "fallback_jumps": 0}
    if cfg.selector == "top_claim":
        sel, used = [], 0
        for c in sorted(cm, key=lambda c: (-base[c], c)):
            if used + cost[c] <= cfg.token_budget and len(sel) < cfg.max_claims:
                sel.append(c)
                used += cost[c]
        trace["tokens"] = used
        return sel, trace
    adj: dict[str, set[str]] = defaultdict(set)
    contra: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        if e.source in cm and e.target in cm:
            adj[e.source].add(e.target)
            adj[e.target].add(e.source)
            if e.relation == RelationType.CONTRADICTS:
                contra[e.source].add(e.target)
                contra[e.target].add(e.source)
    qtok = set(content_tokens(question))

    def gain(c: str, sel: list[str]) -> float:
        covered = set().union(*(set(content_tokens(cm[s].text)) for s in sel)) & qtok if sel else set()
        new_cov = (set(content_tokens(cm[c].text)) & qtok) - covered
        lineages = {cm[s].lineage_id for s in sel}
        red = max((jaccard(cm[c].text, cm[s].text) for s in sel), default=0.0)
        rep = 1.0 if cm[c].lineage_id in lineages and red > 0.5 else 0.0
        con = 1.0 if contra[c] & set(sel) else 0.0
        return (base[c] + w["c"] * len(new_cov) / max(1, len(qtok)) + w["p"] * (cm[c].lineage_id not in lineages)
                - w["r"] * red - w["x"] * (rep + con) - w["l"] * cost[c] / cfg.token_budget)

    sel: list[str] = []
    used = 0
    while len(sel) < cfg.max_claims:
        frontier = {n for s in sel for n in adj[s]} - set(sel) if sel else set(cm)
        fits = [c for c in frontier if used + cost[c] <= cfg.token_budget]
        if not fits:
            fits = [c for c in cm if c not in sel and used + cost[c] <= cfg.token_budget]
            if not fits:
                break
            trace["fallback_jumps"] += 1
        best = max(sorted(fits), key=lambda c: gain(c, sel))
        if sel and gain(best, sel) <= 0:
            break
        sel.append(best)
        used += cost[best]
    trace["tokens"] = used
    return sel, trace
