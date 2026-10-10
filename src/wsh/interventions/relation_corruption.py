"""P2 - replace the type of a fraction of graph edges with a different (incorrect) relation,
or (params.mode='flip') reverse their direction. Claims are untouched, so the label is
preserved; only graph representations (R4/R4P) are affected."""

from __future__ import annotations

from ..data.schemas import AnnotationStatus, EvidenceBundle, Question, RelationType
from .base import InterventionRecord, copy_bundle, n_affected, record_intervention, rng_for


def apply(b: EvidenceBundle, q: Question, rate: float, seed: int, params: dict | None = None):
    params = params or {}
    mode = params.get("mode", "retype")
    out = copy_bundle(b)
    rec = InterventionRecord("P2", rate, seed, params, applicable=bool(b.edges), n_eligible=len(b.edges))
    if not b.edges:
        rec.label_effect, rec.reason = "unavailable", "bundle has no edges"
        record_intervention(out, rec)
        return out, rec
    rng = rng_for("P2", q, rate, seed, params)
    k = n_affected(rate, len(b.edges))
    for i in sorted(rng.sample(range(len(out.edges)), k)):
        e = out.edges[i]
        before = {"source": e.source, "target": e.target, "relation": e.relation.value}
        if mode == "flip":
            e.source, e.target = e.target, e.source
        else:
            e.relation = rng.choice([r for r in RelationType if r != e.relation])
        e.status = AnnotationStatus.CORRUPTED
        e.meta = {**e.meta, "corrupted_from": before}
        rec.changes.append({"edge_index": i, "before": before,
                            "after": {"source": e.source, "target": e.target, "relation": e.relation.value}})
    rec.n_affected = k
    rec.label_effect = "preserved"
    record_intervention(out, rec)
    return out, rec
