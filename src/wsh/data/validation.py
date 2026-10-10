"""Schema-level integrity checks. Violations raise ``ValidationError`` (never silently fixed)."""

from __future__ import annotations

from .provenance import assert_unique
from .schemas import AnnotationStatus, EvidenceBundle, Question, RelationType


class ValidationError(ValueError):
    pass


REQUIRED_ANNOTATION_KEYS = {
    "answer", "supporting_sentences", "sentence_segmentation", "reasoning_order", "depends_on_edges",
    "supports_edges", "contradicts_edges", "duplicate_edges", "supersedes_edges",
}


def validate_question(q: Question) -> list[str]:
    """Raise on hard errors; return a list of soft warnings."""
    warnings: list[str] = []
    if not q.question.strip():
        raise ValidationError(f"{q.uid}: empty question")
    if not q.answers or not all(a.strip() for a in q.answers[:1]):
        raise ValidationError(f"{q.uid}: missing gold answer")
    if q.task == "verification" and (not q.label_set or q.answers[0] not in q.label_set):
        raise ValidationError(f"{q.uid}: verdict {q.answers[:1]} not in label set {q.label_set}")
    missing = REQUIRED_ANNOTATION_KEYS - set(q.annotations)
    if missing:
        raise ValidationError(f"{q.uid}: annotation manifest lacks {sorted(missing)}")
    assert_unique([p.passage_id for p in q.passages], "passage_id")
    for p in q.passages:
        for s, e in p.sentence_spans:
            if not (0 <= s <= e <= len(p.text)):
                raise ValidationError(f"{p.passage_id}: sentence span {(s, e)} outside text")
        if p.text and not p.sentence_spans:
            warnings.append(f"{p.passage_id}: no sentences")
    pids = {p.passage_id for p in q.passages}
    for f in q.supporting_facts:
        if f.passage_id not in pids:
            raise ValidationError(f"{q.uid}: supporting fact references unknown passage {f.passage_id}")
        if f.sentence_index is not None and not 0 <= f.sentence_index < q.passage(f.passage_id).n_sentences:
            raise ValidationError(f"{q.uid}: supporting sentence index out of range")
    if q.annotations["supporting_sentences"] == AnnotationStatus.UNAVAILABLE and any(
            f.sentence_index is not None for f in q.supporting_facts):
        raise ValidationError(f"{q.uid}: sentence-level facts present but marked unavailable")
    if q.reasoning_steps and q.annotations["reasoning_order"] == AnnotationStatus.UNAVAILABLE:
        raise ValidationError(f"{q.uid}: reasoning steps present but order marked unavailable")
    for st in q.reasoning_steps:
        for pid in st.passage_ids:
            if pid not in pids:
                raise ValidationError(f"{q.uid}: step {st.index} references unknown passage")
        if any(d >= st.index for d in st.depends_on):
            raise ValidationError(f"{q.uid}: step {st.index} depends on a later step")
    for k, v in q.annotation_notes.items():
        if k.endswith("dropped") or k.endswith("ambiguous"):
            warnings.append(f"{q.uid}: {k}: {v}")
    return warnings


def validate_bundle(b: EvidenceBundle) -> None:
    assert_unique([c.claim_id for c in b.claims], "claim_id")
    cids = {c.claim_id for c in b.claims}
    for c in b.claims:
        if c.is_corrupted and c.is_gold_support:
            raise ValidationError(f"{c.claim_id}: corrupted claim marked as gold support")
        if c.is_corrupted and c.status != AnnotationStatus.CORRUPTED:
            raise ValidationError(f"{c.claim_id}: corrupted claim must carry CORRUPTED status")
        for sp in c.spans:
            p = b.passages.get(sp.passage_id)
            if p is None:
                raise ValidationError(f"{c.claim_id}: span references passage not in bundle")
            if not 0 <= sp.start <= sp.end <= len(p.text):
                raise ValidationError(f"{c.claim_id}: span outside passage text")
        if c.extraction_method.startswith("sentence") and not c.is_corrupted and c.spans:
            sp = c.spans[0]
            if b.passages[sp.passage_id].text[sp.start:sp.end] != c.text:
                raise ValidationError(f"{c.claim_id}: sentence claim text does not match its source span")
    for e in b.edges:
        if e.source not in cids or e.target not in cids:
            raise ValidationError(f"edge {e.key} references a claim not in the bundle")
        if e.source == e.target:
            raise ValidationError(f"self-loop edge {e.key}")
        if not isinstance(e.relation, RelationType):
            raise ValidationError(f"edge {e.key}: unknown relation")
    if b.path:
        for st in b.path:
            for cid in st.claim_ids:
                if cid not in cids:
                    raise ValidationError(f"path references unknown claim {cid}")
    for pid in b.passage_order:
        if pid not in b.passages:
            raise ValidationError(f"passage_order references unknown passage {pid}")
