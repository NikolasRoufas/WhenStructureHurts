"""P5 - provenance manipulation.

mode='strip'     : hide the source title of k claims (claim.meta['hide_source']=True).
mode='duplicate' : add k near-identical copies of real claims attributed to a "(mirror)"
                   source with the SAME lineage id (controlled source-lineage duplication).
                   Copies have faithful text but fabricated attribution: status CORRUPTED,
                   never gold. With params.annotate_edges (default True) a DUPLICATE edge
                   links copy and original, so lineage-aware methods can discount it.
Label: preserved in both modes.
"""

from __future__ import annotations

from ..data.provenance import derived_claim_id
from ..data.schemas import AnnotationStatus, Edge, EvidenceBundle, Question, RelationType
from .base import InterventionRecord, copy_bundle, n_affected, record_intervention, rng_for


def apply(b: EvidenceBundle, q: Question, rate: float, seed: int, params: dict | None = None):
    params = params or {}
    mode = params.get("mode", "strip")
    out = copy_bundle(b)
    rng = rng_for("P5", q, rate, seed, params)
    rec = InterventionRecord("P5", rate, seed, params, applicable=bool(b.claims), n_eligible=len(b.claims))
    k = n_affected(rate, len(b.claims))
    victims = sorted(rng.sample([c.claim_id for c in out.claims], k))
    if mode == "strip":
        for c in out.claims:
            if c.claim_id in victims:
                c.meta = {**c.meta, "hide_source": True}
                rec.changes.append({"stripped_source": c.claim_id, "title": c.title})
    elif mode == "duplicate":
        for v in victims:
            orig = out.claim(v)
            dup = orig.model_copy(deep=True, update={
                "claim_id": derived_claim_id(v, "dup"), "title": f"{orig.title} (mirror)",
                "status": AnnotationStatus.CORRUPTED, "is_gold_support": False, "derived_from": v,
                "meta": {**orig.meta, "provenance_corrupted": True}})
            pos = rng.randrange(len(out.claims) + 1)
            out.claims.insert(pos, dup)
            if params.get("annotate_edges", True):
                out.edges.append(Edge(source=dup.claim_id, target=v, relation=RelationType.DUPLICATE, confidence=1.0,
                                      status=AnnotationStatus.CORRUPTED, method="intervention:P5"))
            if out.path:
                for st in out.path:
                    if v in st.claim_ids:
                        st.claim_ids.insert(st.claim_ids.index(v) + 1, dup.claim_id)
            rec.changes.append({"duplicated": v, "copy": dup.claim_id, "position": pos})
    else:
        raise ValueError(f"unknown P5 mode {mode}")
    rec.n_affected = k
    rec.label_effect = "preserved"
    record_intervention(out, rec)
    return out, rec
