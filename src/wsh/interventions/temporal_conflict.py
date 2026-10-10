"""P7 - temporal conflict between a historical and an updated statement.

Requires VERIFIED chronological information, which none of the loaded datasets provides.
The intervention therefore reads an external spec (JSONL), one object per question:

    {"question_uid": "...", "old": {"text": "...", "date": "YYYY[-MM[-DD]]", "source": "..."},
     "new": {"text": "...", "date": "...", "source": "..."},
     "verified_by": "annotator id / procedure", "status": "human_verified",
     "label_effect": "preserved" | "changed_verified", "revised_answers": ["..."]}

Without an entry for the question the intervention is reported as unavailable. Nothing is
generated automatically: synthesising "updated facts" would fabricate evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..data.schemas import AnnotationStatus, Claim, Edge, EvidenceBundle, Question, RelationType, Span
from .base import InterventionRecord, copy_bundle, record_intervention

_SPEC_CACHE: dict[str, dict] = {}


def load_spec(path: str | None) -> dict[str, dict]:
    if not path:
        return {}
    if path not in _SPEC_CACHE:
        p = Path(path)
        _SPEC_CACHE[path] = {} if not p.exists() else {
            (o := json.loads(line))["question_uid"]: o for line in p.read_text().splitlines() if line.strip()}
    return _SPEC_CACHE[path]


def apply(b: EvidenceBundle, q: Question, rate: float, seed: int, params: dict | None = None):
    params = params or {}
    out = copy_bundle(b)
    spec = load_spec(params.get("spec_path")).get(q.uid)
    rec = InterventionRecord("P7", rate, seed, params, applicable=spec is not None and rate > 0)
    if spec is None:
        rec.label_effect, rec.reason = "unavailable", "no verified temporal-conflict spec for this question"
        record_intervention(out, rec)
        return out, rec
    if rate <= 0:
        record_intervention(out, rec)
        return out, rec
    status = AnnotationStatus(spec.get("status", "human_verified"))
    new_claims = []
    for tag in ("old", "new"):
        s = spec[tag]
        pid = f"p7/{q.uid}/{tag}"
        from ..data.schemas import Passage

        out.passages[pid] = Passage(passage_id=pid, title=s["source"], text=s["text"], sentence_spans=[(0, len(s["text"]))],
                                    segmentation="external", segmentation_status=status, position=-1,
                                    lineage_id=f"p7:{s['source']}", timestamp=s["date"])
        out.passage_order.append(pid)
        c = Claim(claim_id=f"{pid}#s00", text=s["text"], spans=[Span(passage_id=pid, start=0, end=len(s["text"]))],
                  passage_id=pid, title=s["source"], lineage_id=f"p7:{s['source']}", status=status,
                  extraction_method="external:P7", timestamp=s["date"], meta={"p7": tag})
        new_claims.append(c)
    out.claims += new_claims
    out.edges.append(Edge(source=new_claims[1].claim_id, target=new_claims[0].claim_id, relation=RelationType.SUPERSEDES,
                          confidence=1.0, status=status, method="external:P7"))
    rec.n_affected = 2
    rec.label_effect = spec.get("label_effect", "preserved")
    rec.changes.append({"added": [c.claim_id for c in new_claims], "verified_by": spec.get("verified_by"),
                        "revised_answers": spec.get("revised_answers")})
    record_intervention(out, rec)
    return out, rec
