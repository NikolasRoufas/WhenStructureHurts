"""P1 - remove evidence claims required for the answer.

Required claims: gold-supporting sentence claims (sentence-level datasets). For passage-level
annotations (MuSiQue) a claim is required if it mentions a decomposition sub-answer or the
final answer (rule R-REQ); if none does, all gold-supporting claims are eligible.
"""

from __future__ import annotations

from ..data.schemas import Claim, EvidenceBundle, Question
from ..text import contains_phrase
from .base import (InterventionRecord, copy_bundle, finalize_label, n_affected, record_intervention,
                   remap_claim_refs, rng_for)


def required_claims(b: EvidenceBundle, q: Question) -> list[Claim]:
    gold = [c for c in b.claims if c.is_gold_support and not c.is_corrupted]
    if q.has_sentence_level_support():
        return gold
    anchors = [s.sub_answer for s in q.reasoning_steps if s.sub_answer] + (q.answers if q.task == "qa" else [])
    req = [c for c in gold if any(contains_phrase(c.text, a) for a in anchors)]
    return req or gold


def apply(b: EvidenceBundle, q: Question, rate: float, seed: int, params: dict | None = None):
    params = params or {}
    out = copy_bundle(b)
    elig = required_claims(b, q)
    rec = InterventionRecord("P1", rate, seed, params, applicable=bool(elig), n_eligible=len(elig))
    if not elig:
        rec.label_effect, rec.reason = "unavailable", "no required claims identifiable"
        record_intervention(out, rec)
        return out, rec
    rng = rng_for("P1", q, rate, seed, params)
    k = n_affected(rate, len(elig))
    victims = sorted(rng.sample([c.claim_id for c in elig], k))
    out.claims = [c for c in out.claims if c.claim_id not in victims]
    for v in victims:
        remap_claim_refs(out, v, None)
        rec.changes.append({"removed_claim": v, "text": b.claim(v).text})
    rec.n_affected = k
    finalize_label(rec, b, out, q)
    record_intervention(out, rec)
    return out, rec
