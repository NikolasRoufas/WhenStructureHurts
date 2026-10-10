"""Identifier construction and span-level provenance utilities."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .schemas import Claim, EvidenceBundle, Passage, Question, Span


class DuplicateIdentifierError(ValueError):
    pass


def passage_id(dataset: str, qid: str, position: int) -> str:
    # Position-based: two context entries with the same title (or chunks of the same
    # document) can never collide. This is the fix for the original HotpotQA
    # passage-baseline duplicate-identifier bug.
    return f"{dataset}/{qid}/p{position:02d}"


def sentence_claim_id(pid: str, sentence_index: int) -> str:
    return f"{pid}#s{sentence_index:02d}"


def atomic_claim_id(pid: str, sentence_index: int, k: int) -> str:
    return f"{sentence_claim_id(pid, sentence_index)}.a{k}"


def derived_claim_id(cid: str, tag: str) -> str:
    return f"{cid}~{tag}"


def assert_unique(ids: Iterable[str], what: str = "identifier") -> None:
    dup = [k for k, v in Counter(ids).items() if v > 1]
    if dup:
        raise DuplicateIdentifierError(f"duplicate {what}(s): {dup[:5]}")


def sentence_span(p: Passage, i: int) -> Span:
    s, e = p.sentence_spans[i]
    return Span(passage_id=p.passage_id, start=s, end=e)


def gold_units(q: Question) -> list[Span]:
    """Gold evidence units as spans: sentences where annotated, else whole passages."""
    units: list[Span] = []
    for f in q.gold_facts():
        p = q.passage(f.passage_id)
        if f.sentence_index is None:
            units.append(Span(passage_id=p.passage_id, start=0, end=len(p.text)))
        elif 0 <= f.sentence_index < p.n_sentences:
            units.append(sentence_span(p, f.sentence_index))
    return units


def claim_overlaps_gold(claim: Claim, units: list[Span]) -> bool:
    return any(s.overlaps(u) for s in claim.spans for u in units)


def units_covered(spans: list[Span], units: list[Span]) -> list[bool]:
    return [any(s.overlaps(u) for s in spans) for u in units]


def bundle_spans(bundle: EvidenceBundle, include_corrupted: bool = False) -> list[Span]:
    """Spans of evidence whose *text faithfully reflects its source*.

    Corrupted claims keep their spans for auditing but are excluded here so they never
    count as preserved gold evidence.
    """
    out: list[Span] = []
    for c in bundle.claims:
        if c.is_corrupted and not include_corrupted:
            continue
        out.extend(c.spans)
    return out
