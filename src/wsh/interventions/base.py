"""Shared intervention machinery.

Every intervention is a pure function (bundle, question, rate, seed, params) -> (new bundle,
InterventionRecord). It never mutates its input. The number of affected units is
k = ceil(rate * n_eligible) for rate > 0 (so small bundles can make different rates
coincide; the realised k is always recorded and is what analyses should use).

Label effects:
    preserved       the original gold answer remains justified by the evidence
    not_guaranteed  evidence the answer relied on was altered/removed; evaluate robustness
                    (agreement with the unperturbed prediction) and abstention, not accuracy
    answer_removed  the gold answer string no longer occurs in any faithful evidence item
    unavailable     intervention not applicable / required verified data missing
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass, field
from typing import Any

from ..data.schemas import EvidenceBundle, Question
from ..hashing import derive_seed
from ..text import contains_phrase


@dataclass
class InterventionRecord:
    name: str
    rate: float
    seed: int
    params: dict[str, Any]
    applicable: bool
    n_eligible: int = 0
    n_affected: int = 0
    changes: list[dict[str, Any]] = field(default_factory=list)
    label_effect: str = "preserved"
    reason: str | None = None
    answer_introduced: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def n_affected(rate: float, n_eligible: int) -> int:
    if rate <= 0 or n_eligible == 0:
        return 0
    return min(n_eligible, math.ceil(rate * n_eligible - 1e-9))


def rng_for(name: str, q: Question, rate: float, seed: int, params: dict) -> random.Random:
    return random.Random(derive_seed(name, q.uid, rate, seed, sorted(params.items())))


def copy_bundle(b: EvidenceBundle) -> EvidenceBundle:
    return b.model_copy(deep=True)


def answer_in_faithful_evidence(b: EvidenceBundle, q: Question) -> bool:
    if q.task != "qa" or q.answer_type == "yes_no":
        return True  # not decidable lexically; callers treat as unknown
    text = " ".join(c.text + " " + c.title for c in b.claims if not c.is_corrupted)
    return any(contains_phrase(text, a) for a in q.answers)


def finalize_label(rec: InterventionRecord, before: EvidenceBundle, after: EvidenceBundle, q: Question,
                   default_if_changed: str = "not_guaranteed") -> None:
    if rec.n_affected == 0:
        rec.label_effect = "preserved"
        return
    if answer_in_faithful_evidence(before, q) and not answer_in_faithful_evidence(after, q):
        rec.label_effect = "answer_removed"
    else:
        rec.label_effect = default_if_changed


def remap_claim_refs(b: EvidenceBundle, old: str, new: str | None) -> None:
    """Point edges/path/conflicts at a replacement claim id (or drop them if new is None)."""
    if new is None:
        b.edges = [e for e in b.edges if old not in (e.source, e.target)]
    else:
        for e in b.edges:
            if e.source == old:
                e.source = new
            if e.target == old:
                e.target = new
    if b.path:
        for st in b.path:
            st.claim_ids = [new if c == old else c for c in st.claim_ids if not (c == old and new is None)]
        b.path = [st for st in b.path if st.claim_ids]
    for cs in b.conflicts:
        cs.claim_ids = [new if c == old else c for c in cs.claim_ids if not (c == old and new is None)]


def record_intervention(b: EvidenceBundle, rec: InterventionRecord) -> None:
    b.interventions.append(rec.to_dict())
