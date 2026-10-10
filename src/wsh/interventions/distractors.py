"""P4 - inject real, non-supporting sentences from the question's own candidate pool.

k = ceil(rate * n_claims) sentences taken from passages that are not in the bundle and not
gold-supporting. params.mode='hard' (default) picks the sentences with the highest BM25
score against the question; 'random' samples uniformly. Each is inserted at a random
position (and into a random reasoning step when a path exists). Distractors are real
dataset text (status of their passage's segmentation), flagged is_distractor, never gold.
Candidates whose text contains a gold answer string (span QA) are excluded, so P4 never adds
answer evidence. Label: preserved (gold evidence is untouched). Caveat: a distractor may itself
conflict with the gold evidence; this is not checked.
"""

from __future__ import annotations

from ..data.provenance import gold_units
from ..data.schemas import EvidenceBundle, Question
from ..extraction.claim_extractor import sentence_claim
from ..retrieval.bm25 import bm25_scores
from ..text import contains_phrase
from .base import InterventionRecord, copy_bundle, n_affected, record_intervention, rng_for


def apply(b: EvidenceBundle, q: Question, rate: float, seed: int, params: dict | None = None):
    params = params or {}
    mode = params.get("mode", "hard")
    out = copy_bundle(b)
    gold_p = set(q.gold_passage_ids())
    pool = [p for p in q.passages if p.passage_id not in b.passages and p.passage_id not in gold_p]
    units = gold_units(q)
    cands = [sentence_claim(p, i, units) for p in pool for i in range(p.n_sentences) if p.sentence(i).strip()]
    # a distractor that states the gold answer would ADD answer evidence; such sentences are excluded
    answer_bearing = [c for c in cands if _states_answer(c.text, q)]
    cands = [c for c in cands if c not in answer_bearing]
    rec = InterventionRecord("P4", rate, seed, params, applicable=bool(cands), n_eligible=len(cands))
    rec.changes.append({"excluded_answer_bearing_candidates": len(answer_bearing)})
    if not cands:
        rec.label_effect, rec.reason = "unavailable", "no non-gold passages in the candidate pool"
        record_intervention(out, rec)
        return out, rec
    rng = rng_for("P4", q, rate, seed, params)
    k = min(len(cands), n_affected(rate, len(b.claims)))
    if mode == "hard":
        from ..data.schemas import Passage  # local: score sentences as tiny passages

        tmp = [Passage(passage_id=c.claim_id, title=c.title, text=c.text, sentence_spans=[(0, len(c.text))],
                       segmentation="tmp", segmentation_status=c.status, position=0, lineage_id=c.lineage_id) for c in cands]
        s = bm25_scores(q.question, tmp)
        picked = [cands[i] for i in sorted(range(len(cands)), key=lambda i: (-s[i], i))[:k]]
    else:
        picked = rng.sample(cands, k)
    for c in picked:
        c.is_distractor = True
        c.is_gold_support = False
        pos = rng.randrange(len(out.claims) + 1)
        out.claims.insert(pos, c)
        if c.passage_id not in out.passages:
            out.passages[c.passage_id] = q.passage(c.passage_id)
            out.passage_order.insert(rng.randrange(len(out.passage_order) + 1), c.passage_id)
        if out.path:
            st = out.path[rng.randrange(len(out.path))]
            st.claim_ids.insert(rng.randrange(len(st.claim_ids) + 1), c.claim_id)
        rec.changes.append({"inserted_claim": c.claim_id, "text": c.text, "position": pos, "mode": mode})
    rec.n_affected = k
    rec.label_effect = "preserved"
    record_intervention(out, rec)
    return out, rec


def _states_answer(text: str, q: Question) -> bool:
    return q.task == "qa" and q.answer_type == "span" and any(contains_phrase(text, a) for a in q.answers)
