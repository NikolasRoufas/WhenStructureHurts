"""P6 - controlled claim-extraction corruption (simulated extractor errors).

params.op in {negation, qualifier, entity, temporal}. Eligible claims are those where the
operation applies (regex match). k = ceil(rate * n_eligible) claims are rewritten:

    negation  : delete 'not', 'never', "n't" (e.g. "did not win" -> "did win")
    qualifier : delete hedges/quantifiers (about, approximately, nearly, reportedly, ...)
    entity    : replace one entity mention that does not occur in the question with "it"
                (simulates an unresolved pronoun)
    temporal  : delete dates (month-day-year, 'in 1994', bare years)

Corrupted claims get new ids (``{id}~p6{op}``), status CORRUPTED, is_corrupted=True and are
never gold. Label: answer_removed if the gold answer string disappears from faithful
evidence, else not_guaranteed.
"""

from __future__ import annotations

import re

from ..data.provenance import derived_claim_id
from ..data.schemas import AnnotationStatus, Claim, EvidenceBundle, Question
from ..text import contains_phrase, extract_entities
from .base import (InterventionRecord, copy_bundle, finalize_label, n_affected, record_intervention,
                   remap_claim_refs, rng_for)

_MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?"
PATTERNS = {
    "negation": [(re.compile(r"\b(can)not\b", re.I), r"\1"), (re.compile(r"n't\b", re.I), ""),
                 (re.compile(r"\s+(?:not|never)\b", re.I), "")],
    "qualifier": [(re.compile(r"\b(?:about|approximately|around|nearly|almost|roughly|reportedly|allegedly|"
                              r"possibly|probably|mainly|mostly|largely|partly|at least|more than|less than|"
                              r"over|some|several)\s+", re.I), "")],
    "temporal": [(re.compile(rf",?\s*(?:on|in|since|from|until|by|during)?\s*{_MONTH}\s+\d{{1,2}},?\s+\d{{4}}"), ""),
                 (re.compile(rf",?\s*(?:on|in|since|from|until|by|during)?\s*\d{{1,2}}\s+{_MONTH}\s+\d{{4}}"), ""),
                 (re.compile(r",?\s*\b(?:in|on|since|from|until|by|during|of)\s+(?:the\s+)?(?:1[0-9]{3}|20[0-9]{2})s?\b"), ""),
                 (re.compile(r"\s*\((?:[^()]*?\b(?:1[0-9]{3}|20[0-9]{2})\b[^()]*?)\)"), ""),
                 (re.compile(r"\b(?:1[0-9]{3}|20[0-9]{2})\b"), "")],
}
OPS = ("negation", "qualifier", "entity", "temporal")


def _entity_targets(c: Claim, q: Question) -> list[str]:
    return [e for e in extract_entities(c.text) if not contains_phrase(q.question, e) and not e.isdigit()]


def applies(op: str, c: Claim, q: Question) -> bool:
    if op == "entity":
        return bool(_entity_targets(c, q))
    return any(p.search(c.text) for p, _ in PATTERNS[op])


def corrupt_text(op: str, c: Claim, q: Question, rng) -> str:
    t = c.text
    if op == "entity":
        ent = rng.choice(_entity_targets(c, q))
        return re.sub(re.escape(ent), "it", t, count=1)
    for p, rep in PATTERNS[op]:
        t = p.sub(rep, t)
    return re.sub(r"\s{2,}", " ", re.sub(r"\s+([,.;:])", r"\1", t)).strip()


def apply(b: EvidenceBundle, q: Question, rate: float, seed: int, params: dict | None = None):
    params = params or {}
    op = params.get("op", "negation")
    if op not in OPS:
        raise ValueError(f"unknown P6 op {op}")
    out = copy_bundle(b)
    elig = [c.claim_id for c in out.claims if not c.is_corrupted and applies(op, c, q)]
    rec = InterventionRecord("P6", rate, seed, params, applicable=bool(elig), n_eligible=len(elig))
    if not elig:
        rec.label_effect, rec.reason = "unavailable", f"no claim admits op={op}"
        record_intervention(out, rec)
        return out, rec
    rng = rng_for("P6", q, rate, seed, params)
    k = n_affected(rate, len(elig))
    for v in sorted(rng.sample(elig, k)):
        i = next(j for j, c in enumerate(out.claims) if c.claim_id == v)
        orig = out.claims[i]
        new_text = corrupt_text(op, orig, q, rng)
        new_id = derived_claim_id(v, f"p6{op}")
        out.claims[i] = orig.model_copy(deep=True, update={
            "claim_id": new_id, "text": new_text, "status": AnnotationStatus.CORRUPTED, "is_corrupted": True,
            "is_gold_support": False, "derived_from": v, "extraction_method": f"intervention:P6:{op}",
            "entities": extract_entities(new_text)})
        remap_claim_refs(out, v, new_id)
        rec.changes.append({"claim": v, "new_id": new_id, "op": op, "before": orig.text, "after": new_text})
    rec.n_affected = k
    finalize_label(rec, b, out, q)
    record_intervention(out, rec)
    return out, rec
