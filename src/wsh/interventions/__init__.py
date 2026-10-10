from . import claim_removal, distractors, extraction_corruption, ordering, provenance_corruption, relation_corruption, temporal_conflict

REGISTRY = {
    "P1": claim_removal.apply,
    "P2": relation_corruption.apply,
    "P3": ordering.apply,
    "P4": distractors.apply,
    "P5": provenance_corruption.apply,
    "P6": extraction_corruption.apply,
    "P7": temporal_conflict.apply,
}


LABEL_EFFECTS = {"preserved", "not_guaranteed", "answer_removed", "unavailable"}


def apply(name: str, bundle, question, rate: float, seed: int, params: dict | None = None):
    """Apply an intervention and audit it: the label effect must be from LABEL_EFFECTS, and
    ``answer_introduced`` records whether any added or modified text states a gold answer that
    the original faithful evidence did not already contain (such records are excluded from
    accuracy analyses by exp2_sensitivity)."""
    out, rec = REGISTRY[name](bundle, question, rate, seed, params or {})
    if rec.label_effect not in LABEL_EFFECTS:
        raise ValueError(f"{name}: unknown label effect {rec.label_effect!r}")
    rec.answer_introduced = _answer_introduced(bundle, out, question)
    if out.interventions:
        out.interventions[-1]["answer_introduced"] = rec.answer_introduced
    return out, rec


def _answer_introduced(before, after, q) -> bool:
    from ..text import contains_phrase

    if q.task != "qa" or q.answer_type != "span":
        return False
    old = {c.claim_id: c.text for c in before.claims}
    new_text = " ".join(c.text for c in after.claims if old.get(c.claim_id) != c.text)
    had = " ".join(c.text for c in before.claims if not c.is_corrupted)
    return any(contains_phrase(new_text, a) and not contains_phrase(had, a) for a in q.answers)
