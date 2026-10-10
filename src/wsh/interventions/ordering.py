"""P3 - reorder evidence while keeping its text: permute the positions of k claims and of
k' reasoning-path steps (k = ceil(rate*n)). Label preserved. For R4 the rendered order is
graph-derived, so only orderings that the topological sort leaves free are affected; this is
recorded and expected."""

from __future__ import annotations

from ..data.schemas import EvidenceBundle, Question
from .base import InterventionRecord, copy_bundle, n_affected, record_intervention, rng_for


def _permute(items: list, k: int, rng) -> tuple[list, list[int]]:
    if k < 2:
        return items, []
    pos = sorted(rng.sample(range(len(items)), k))
    vals = [items[p] for p in pos]
    perm = vals[:]
    for _ in range(10):  # avoid the identity permutation when possible
        rng.shuffle(perm)
        if perm != vals:
            break
    out = items[:]
    for p, v in zip(pos, perm):
        out[p] = v
    return out, pos


def apply(b: EvidenceBundle, q: Question, rate: float, seed: int, params: dict | None = None):
    params = params or {}
    out = copy_bundle(b)
    rng = rng_for("P3", q, rate, seed, params)
    rec = InterventionRecord("P3", rate, seed, params, applicable=len(b.claims) > 1, n_eligible=len(b.claims))
    k = n_affected(rate, len(b.claims))
    before = [c.claim_id for c in out.claims]
    out.claims, pos = _permute(out.claims, k, rng)
    if pos:
        rec.changes.append({"claims_before": before, "claims_after": [c.claim_id for c in out.claims]})
    if out.path and len(out.path) > 1:
        ks = n_affected(rate, len(out.path))
        sb = [s.label for s in out.path]
        out.path, spos = _permute(out.path, ks, rng)
        if spos:
            rec.changes.append({"steps_before": sb, "steps_after": [s.label for s in out.path]})
    rec.n_affected = len(pos)
    rec.label_effect = "preserved"
    if not rec.applicable:
        rec.label_effect, rec.reason = "unavailable", f"fewer than 2 claims to reorder (n={len(b.claims)})"
    record_intervention(out, rec)
    return out, rec
