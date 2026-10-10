"""Construction of ``EvidenceBundle`` objects from gold annotations or retrieval.

Gold bundles contain only dataset text (sentence-unit claims). Their DEPENDS_ON edges and
reasoning path come from the dataset's reasoning annotation via the loader rules
(R-MSQ / R-2WK / R-HPQ) plus the anchoring rule below; they carry the status of that
annotation (DATASET_SUPPLIED / DETERMINISTIC_DERIVED). No other relation type is added to a
gold bundle, because no dataset supplies one.

Anchoring rule (R-ANCHOR): for step j depending on step i, with anchor a = sub-answer of
step i, the edge goes from the first in-scope claim of step j that mentions a to the first
in-scope claim of step i that mentions a. If no claim mentions a, the step's first
supporting sentence (or first sentence) is used and the edge is tagged anchor=fallback.
"""

from __future__ import annotations

from typing import Literal

from ..data.provenance import gold_units
from ..data.schemas import AnnotationStatus, Claim, Edge, EvidenceBundle, PathStep, Question, RelationType
from ..text import contains_phrase

EvidenceScope = Literal["gold_passages", "gold_sentences"]


class EvidenceUnavailable(RuntimeError):
    """Raised when a requested evidence condition cannot be built without fabricating data."""


def _scope_filter(q: Question, scope: EvidenceScope) -> dict[str, list[int]] | None:
    if scope == "gold_passages":
        return None
    if not q.has_sentence_level_support():
        raise EvidenceUnavailable(f"{q.uid}: gold_sentences scope requires sentence-level supporting facts")
    out: dict[str, list[int]] = {}
    for f in q.gold_facts():
        out.setdefault(f.passage_id, []).append(f.sentence_index)  # type: ignore[arg-type]
    return out


def gold_passage_order(q: Question) -> list[str]:
    """Canonical (dataset context) order of gold passages: the 'natural' order used by R0/R1."""
    gold = set(q.gold_passage_ids())
    return [p.passage_id for p in sorted(q.passages, key=lambda p: p.position) if p.passage_id in gold]


def gold_bundle(q: Question, scope: EvidenceScope = "gold_passages") -> EvidenceBundle:
    from ..extraction.claim_extractor import sentence_claim

    pids = gold_passage_order(q)
    if not pids:
        raise EvidenceUnavailable(f"{q.uid}: no usable gold evidence (e.g. FEVER NEI evidence is not gold)")
    filt = _scope_filter(q, scope)
    units = gold_units(q)
    claims: list[Claim] = []
    for pid in pids:
        p = q.passage(pid)
        idx = range(p.n_sentences) if filt is None else sorted(set(filt.get(pid, [])))
        claims += [sentence_claim(p, i, units) for i in idx if p.sentence(i).strip()]
    b = EvidenceBundle(
        question_uid=q.uid, claims=claims, passages={pid: q.passage(pid) for pid in pids}, passage_order=pids,
        origin={"evidence_source": "gold", "scope": scope, "claims": "sentence units (dataset text)",
                "claim_status": sorted({c.status.value for c in claims})},
    )
    if filt is not None:
        # gold_sentences scope: passage-level renderings (R0) show only the in-scope sentences;
        # passage text itself is untouched so every span keeps its original offsets.
        b.origin["passage_text"] = "in_scope_sentences_only"
    add_gold_structure(q, b)
    return b


def _step_claims(q: Question, step, claims: list[Claim]) -> list[Claim]:
    out = [c for c in claims if c.passage_id in step.passage_ids]
    if step.sentence_indices:
        sup = [c for c in out if c.meta.get("sentence_index") in step.sentence_indices.get(c.passage_id, [])]
        # supporting sentences of the step first, then the rest of the step's passage
        out = sup + [c for c in out if c not in sup]
    return out


def add_gold_structure(q: Question, b: EvidenceBundle) -> None:
    """Attach dataset-derived reasoning path and DEPENDS_ON edges (if annotated)."""
    status = q.annotations.get("reasoning_order", AnnotationStatus.UNAVAILABLE)
    if not q.reasoning_steps or status == AnnotationStatus.UNAVAILABLE:
        b.path, b.path_status = None, AnnotationStatus.UNAVAILABLE
        return
    used: set[str] = set()
    path: list[PathStep] = []
    pos = {c.claim_id: i for i, c in enumerate(b.claims)}
    for st in q.reasoning_steps:
        # within a step, claims keep context order: ordering supporting sentences first would
        # reveal the supporting-fact annotation to R3 only (information the other layouts lack)
        cs = sorted((c.claim_id for c in _step_claims(q, st, b.claims) if c.claim_id not in used), key=pos.get)
        used.update(cs)
        path.append(PathStep(claim_ids=cs, label=f"Step {st.index + 1}"))
    rest = [c.claim_id for c in b.claims if c.claim_id not in used]
    if rest:
        path.append(PathStep(claim_ids=rest, label="Other evidence"))
    b.path = [s for s in path if s.claim_ids]
    b.path_status = status
    edge_status = q.annotations.get("depends_on_edges", AnnotationStatus.UNAVAILABLE)
    if edge_status == AnnotationStatus.UNAVAILABLE:
        return
    for st in q.reasoning_steps:
        for i in st.depends_on:
            anchor = q.reasoning_steps[i].sub_answer
            src_c = _step_claims(q, st, b.claims)
            tgt_c = _step_claims(q, q.reasoning_steps[i], b.claims)
            if not src_c or not tgt_c:
                continue
            s_m = [c for c in src_c if anchor and contains_phrase(c.text, anchor)]
            t_m = [c for c in tgt_c if anchor and contains_phrase(c.text, anchor)]
            src, tgt = (s_m or src_c)[0], (t_m or tgt_c)[0]
            if src.claim_id == tgt.claim_id:
                continue
            b.edges.append(Edge(
                source=src.claim_id, target=tgt.claim_id, relation=RelationType.DEPENDS_ON, confidence=1.0,
                status=AnnotationStatus.DETERMINISTIC_DERIVED,
                method=f"derived:{q.dataset}-steps+R-ANCHOR",
                meta={"anchor": anchor, "anchor_match": "exact" if (s_m and t_m) else "fallback",
                      "steps": [i, st.index], "source_annotation_status": edge_status.value},
            ))


def bundle_from_passages(q: Question, passages, claims: list[Claim], origin: dict) -> EvidenceBundle:
    pm = {p.passage_id: p for p in passages}
    return EvidenceBundle(question_uid=q.uid, claims=claims, passages=pm,
                          passage_order=[p.passage_id for p in passages], origin=origin)


def topological_order(b: EvidenceBundle) -> list[str]:
    """Graph-derived claim order: passages are ordered so that a passage containing a
    DEPENDS_ON target precedes the passage containing its source (ties and cycles fall back
    to bundle order); claims keep their bundle order within a passage."""
    pids: list[str] = []
    for c in b.claims:
        if c.passage_id not in pids:
            pids.append(c.passage_id)
    pos = {p: i for i, p in enumerate(pids)}
    cm = b.claim_map()
    deps: dict[str, set[str]] = {p: set() for p in pids}
    for e in b.edges:
        if e.relation == RelationType.DEPENDS_ON and e.source in cm and e.target in cm:
            sp, tp = cm[e.source].passage_id, cm[e.target].passage_id
            if sp != tp:
                deps[sp].add(tp)
    order: list[str] = []
    done: set[str] = set()
    visiting: set[str] = set()

    def visit(p: str) -> None:
        if p in done or p in visiting:
            return
        visiting.add(p)
        for d in sorted(deps[p], key=pos.get):
            visit(d)
        visiting.discard(p)
        done.add(p)
        order.append(p)

    for p in pids:
        visit(p)
    rank = {p: i for i, p in enumerate(order)}
    return [c.claim_id for c in sorted(b.claims, key=lambda c: (rank[c.passage_id], b.claims.index(c)))]
