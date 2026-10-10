"""R3: ordered reasoning path, claims grouped under 'Step k:' headers.

Gold paths come from dataset reasoning annotations (see representations.evidence). For
retrieved/predicted evidence, ``predicted_path`` builds a heuristic chain (documented
approximation): start at the claim most similar to the question, then repeatedly follow a
DEPENDS_ON edge (or, failing that, the most similar unused claim sharing an entity), until
all claims are placed.

Step sub-questions are NOT rendered by default: they would add information that the other
representations lack.
"""

from __future__ import annotations

from ..data.schemas import AnnotationStatus, EvidenceBundle, PathStep, RelationType
from ..text import jaccard
from .atomic_claims import claim_unit
from .serialization import Layout


class PathUnavailable(RuntimeError):
    pass


def layout(b: EvidenceBundle) -> Layout:
    if not b.path:
        raise PathUnavailable(f"{b.question_uid}: no reasoning path (status={b.path_status.value})")
    cm = b.claim_map()
    units = []
    for st in b.path:
        for cid in st.claim_ids:
            if cid in cm:
                units.append(claim_unit(cm[cid], b.provenance_visible, group=st.label))
    present = {c for st in b.path for c in st.claim_ids}
    leftovers = [c for c in b.claims if c.claim_id not in present]
    units += [claim_unit(c, b.provenance_visible, group="Other evidence") for c in leftovers]
    return Layout("R3", units, show_source=b.provenance_visible, notes={"path_status": b.path_status.value})


def predicted_path(b: EvidenceBundle, question: str) -> None:
    """Attach a heuristic path (MODEL_PREDICTED) to a bundle that has none."""
    if not b.claims:
        b.path, b.path_status = None, AnnotationStatus.UNAVAILABLE
        return
    cm = b.claim_map()
    nxt: dict[str, list[str]] = {}
    for e in b.edges:
        if e.relation == RelationType.DEPENDS_ON:
            nxt.setdefault(e.target, []).append(e.source)
    remaining = [c.claim_id for c in b.claims]
    order: list[str] = []
    cur = max(remaining, key=lambda c: (jaccard(cm[c].text, question), -remaining.index(c)))
    while remaining:
        order.append(cur)
        remaining.remove(cur)
        if not remaining:
            break
        follow = [s for s in nxt.get(cur, []) if s in remaining]
        if follow:
            cur = follow[0]
            continue
        ents = {e.lower() for e in cm[cur].entities}
        linked = [c for c in remaining if ents & {e.lower() for e in cm[c].entities}]
        pool = linked or remaining
        cur = max(pool, key=lambda c: (jaccard(cm[c].text, question), -remaining.index(c)))
    b.path = [PathStep(claim_ids=[c], label=f"Step {i + 1}") for i, c in enumerate(order)]
    b.path_status = AnnotationStatus.MODEL_PREDICTED
