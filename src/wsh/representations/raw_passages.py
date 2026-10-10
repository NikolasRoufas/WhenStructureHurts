"""R0 / B0-B1: raw evidence passages, one unit per passage, in bundle passage order."""

from __future__ import annotations

from ..data.provenance import sentence_claim_id
from ..data.schemas import EvidenceBundle, Span
from .serialization import Layout, Unit


def layout(b: EvidenceBundle) -> Layout:
    units = []
    in_scope_only = b.origin.get("passage_text") == "in_scope_sentences_only"
    for pid in b.passage_order:
        p = b.passages[pid]
        claims = [c for c in b.claims if c.passage_id == pid]
        if in_scope_only or b.interventions:
            # Render the passage from its (possibly perturbed / restricted) claims so that the
            # passage representation carries exactly the same content as the claim ones.
            if not claims:
                continue
            hidden = any(c.meta.get("hide_source") for c in claims)
            units.append(Unit([c.claim_id for c in claims], [pid], [c.spans[0] for c in claims],
                              [c.text for c in claims], p.title if b.provenance_visible and not hidden else None,
                              meta={"corrupted": any(c.is_corrupted for c in claims)}))
        else:
            idx = [i for i in range(p.n_sentences) if p.sentence(i).strip()]
            if idx:  # per-sentence ids/spans keep budget truncation exact
                units.append(Unit([sentence_claim_id(pid, i) for i in idx], [pid],
                                  [Span(passage_id=pid, start=p.sentence_spans[i][0], end=p.sentence_spans[i][1]) for i in idx],
                                  [p.sentence(i) for i in idx], p.title if b.provenance_visible else None))
            else:
                units.append(Unit([], [pid], [Span(passage_id=pid, start=0, end=len(p.text))], [p.text],
                                  p.title if b.provenance_visible else None))
    return Layout("R0", units, show_source=b.provenance_visible)
