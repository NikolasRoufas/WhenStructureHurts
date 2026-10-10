"""R1 (claims in bundle order) and R2 (claims in a seeded random order)."""

from __future__ import annotations

import random

from ..data.schemas import Claim, EvidenceBundle
from ..hashing import derive_seed
from .serialization import Layout, Unit


def claim_unit(c: Claim, show_source: bool, group: str | None = None) -> Unit:
    visible = show_source and not c.meta.get("hide_source")
    return Unit([c.claim_id], [c.passage_id], list(c.spans)[:1], [c.text], c.title if visible else None, group,
                meta={"corrupted": c.is_corrupted, "distractor": c.is_distractor})


def layout(b: EvidenceBundle, order: list[str] | None = None, rep: str = "R1") -> Layout:
    cm = b.claim_map()
    ids = order or [c.claim_id for c in b.claims]
    return Layout(rep, [claim_unit(cm[i], b.provenance_visible) for i in ids], show_source=b.provenance_visible)


def shuffled_layout(b: EvidenceBundle, seed: int) -> Layout:
    ids = [c.claim_id for c in b.claims]
    rng = random.Random(derive_seed("R2", b.question_uid, seed))
    rng.shuffle(ids)
    lay = layout(b, ids, rep="R2")
    lay.notes["shuffle_seed"] = seed
    return lay
