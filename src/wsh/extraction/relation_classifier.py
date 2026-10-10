"""Predicted evidence relations (paper Sec. 3.5-3.6). All output edges are MODEL_PREDICTED.

* Candidate pruning: pairs sharing a heuristic entity mention or with content-token
  Jaccard >= prune_min_jaccard; at most ``max_pairs`` (highest Jaccard first).
* SUPPORTS a->b  : NLI(premise=a, hypothesis=b) entailment >= entail_threshold.
* CONTRADICTS a->b: NLI contradiction >= contradict_threshold (default 0.9) AND the claims share
  an entity mention other than their source titles (added per direction; not assumed
  symmetric). The entity requirement was added after smoke inspection showed the small NLI
  model labelling most unrelated pairs as contradictions (190 edges among 42 claims).
* DUPLICATE      : Jaccard >= duplicate_jaccard, or entailment >= 0.9 in both directions.
                   Recorded once (earlier claim -> later claim) and treated as symmetric.
* SUPERSEDES new->old: both mention years, share an entity, Jaccard >= 0.3, contradiction
  >= year_supersession_threshold in either direction (conditions i-iv of Sec. 3.6, with
  the year as the only available temporal signal).
* DEPENDS_ON b->a (heuristic): claim a mentions the normalised title of b's passage, the
  claims come from different lineages, and that title is not mentioned in the question
  (b is reached through a: the bridge pattern).
"""

from __future__ import annotations

from itertools import combinations

from ..config import RelationConfig
from ..data.schemas import AnnotationStatus, Claim, Edge, RelationType
from ..text import YEAR, contains_phrase, jaccard, normalize_title


def _shares_entity(a: Claim, b: Claim, titles: bool = True) -> bool:
    ea = {e.lower() for e in a.entities} | ({normalize_title(a.title)} if titles else set())
    eb = {e.lower() for e in b.entities} | ({normalize_title(b.title)} if titles else set())
    return bool(ea & eb)


def candidate_pairs(claims: list[Claim], cfg: RelationConfig) -> list[tuple[int, int, float]]:
    pairs = []
    for i, j in combinations(range(len(claims)), 2):
        jac = jaccard(claims[i].text, claims[j].text)
        if jac >= cfg.prune_min_jaccard or _shares_entity(claims[i], claims[j]):
            pairs.append((i, j, jac))
    pairs.sort(key=lambda x: (-x[2], x[0], x[1]))
    return pairs[: cfg.max_pairs]


def heuristic_depends_on(claims: list[Claim], question: str) -> list[Edge]:
    edges = []
    for a in claims:
        for b in claims:
            if a.claim_id == b.claim_id or a.lineage_id == b.lineage_id:
                continue
            t = normalize_title(b.title)
            if len(t) < 3 or contains_phrase(question, t):
                continue
            if contains_phrase(a.text, t):
                edges.append(Edge(source=b.claim_id, target=a.claim_id, relation=RelationType.DEPENDS_ON,
                                  confidence=0.6, status=AnnotationStatus.MODEL_PREDICTED,
                                  method="heuristic:title-mention", meta={"anchor": b.title}))
    # keep one edge per (source passage, target claim) to avoid fan-out over every sentence
    seen, out = set(), []
    for e in edges:
        key = (e.source.split("#")[0], e.target)
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


class RelationClassifier:
    def __init__(self, nli, cfg: RelationConfig):
        self.nli = nli
        self.cfg = cfg

    @property
    def method_id(self) -> str:
        return f"nli:{self.nli.id}" if self.nli is not None else "none"

    def classify(self, claims: list[Claim], question: str) -> tuple[list[Edge], dict]:
        cfg = self.cfg
        pairs = candidate_pairs(claims, cfg)
        stats = {"n_claims": len(claims), "n_candidate_pairs": len(pairs), "classifier": self.method_id}
        edges: list[Edge] = []
        if pairs and self.nli is not None:
            nli_in = []
            for i, j, _ in pairs:
                nli_in += [(claims[i].text, claims[j].text), (claims[j].text, claims[i].text)]
            probs = self.nli.predict(nli_in)
            for k, (i, j, jac) in enumerate(pairs):
                a, b = claims[i], claims[j]
                pab, pba = probs[2 * k], probs[2 * k + 1]
                mk = lambda s, t, rel, conf, extra=None: Edge(  # noqa: E731
                    source=s.claim_id, target=t.claim_id, relation=rel, confidence=round(conf, 4),
                    status=AnnotationStatus.MODEL_PREDICTED, method=self.method_id, meta=extra or {"jaccard": round(jac, 3)})
                if jac >= cfg.duplicate_jaccard or (pab["entailment"] >= 0.9 and pba["entailment"] >= 0.9):
                    edges.append(mk(a, b, RelationType.DUPLICATE, max(jac, min(pab["entailment"], pba["entailment"]))))
                    continue
                ya, yb = YEAR.findall(a.text), YEAR.findall(b.text)
                contra = max(pab["contradiction"], pba["contradiction"])
                if ya and yb and jac >= 0.3 and _shares_entity(a, b) and contra >= cfg.year_supersession_threshold:
                    new, old = (a, b) if max(map(int, ya)) > max(map(int, yb)) else (b, a)
                    if max(map(int, ya)) != max(map(int, yb)):
                        edges.append(mk(new, old, RelationType.SUPERSEDES, contra, {"years": [ya, yb]}))
                for s, t, p in ((a, b, pab), (b, a, pba)):
                    if p["entailment"] >= cfg.entail_threshold:
                        edges.append(mk(s, t, RelationType.SUPPORTS, p["entailment"]))
                    elif p["contradiction"] >= cfg.contradict_threshold and (
                            not cfg.contradiction_requires_shared_entity or _shares_entity(a, b, titles=False)):
                        edges.append(mk(s, t, RelationType.CONTRADICTS, p["contradiction"]))
        dep = heuristic_depends_on(claims, question)
        edges += dep
        stats["n_edges"] = {r.value: sum(e.relation == r for e in edges) for r in RelationType}
        return edges, stats
