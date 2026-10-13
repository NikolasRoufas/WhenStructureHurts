"""Model-agnostic evidence serialization (paper Sec. 3.11). Token budgets are handled by
whole-fact selection in representations/protocols.py (Protocol B), never by cutting text.

A representation produces a ``Layout``: an ordered list of evidence units (each mapped to
claim ids / passage ids / spans), optional step groupings, relation lines and conflicts.
``render`` assigns per-prompt display ids E1..En in layout order, so generators never copy
internal identifiers, and returns an id map for citation evaluation.

Line formats (identical across representations except for the structure they add):
    [E1] (source: Title) text
    Step 1:                     <- R3 grouping header
    Relations:\n E3 DEPENDS_ON E1  <- R4 relation block
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..data.schemas import Span


@dataclass
class Unit:
    claim_ids: list[str]
    passage_ids: list[str]
    spans: list[Span]
    texts: list[str]  # sentence-level pieces (joined with spaces); allows sentence-level truncation
    source: str | None
    group: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        return " ".join(self.texts)


@dataclass
class Layout:
    rep: str
    units: list[Unit]
    relations: list[tuple[int, int, str]] = field(default_factory=list)  # (src unit, tgt unit, label)
    conflicts: list[list[int]] = field(default_factory=list)
    show_source: bool = True
    notes: dict[str, Any] = field(default_factory=dict)


@dataclass
class SerializedEvidence:
    rep: str
    text: str
    id_map: dict[str, dict[str, Any]]  # "E1" -> {claim_ids, passage_ids, spans}
    n_units: int
    n_relations: int
    dropped: list[dict[str, Any]] = field(default_factory=list)
    budget: int | None = None
    evidence_tokens: int | None = None
    notes: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def render(layout: Layout) -> SerializedEvidence:
    lines: list[str] = []
    id_map: dict[str, dict[str, Any]] = {}
    current_group = None
    for k, u in enumerate(layout.units):
        did = f"E{k + 1}"
        if u.group and u.group != current_group:
            lines.append(f"{u.group}:")
            current_group = u.group
        src = f"(source: {u.source}) " if layout.show_source and u.source else ""
        lines.append(f"[{did}] {src}{u.text}")
        id_map[did] = {"claim_ids": u.claim_ids, "passage_ids": u.passage_ids,
                       "spans": [s.model_dump() for s in u.spans], "corrupted": bool(u.meta.get("corrupted"))}
    # s < 0 marks a filler line (relation controls): the label up to '#' is rendered verbatim
    rel_lines = [lab.split("#")[0] if s < 0 else f"E{s + 1} {lab} E{t + 1}" for s, t, lab in layout.relations]
    if rel_lines:
        lines.append("Relations:")
        lines += rel_lines
    if layout.conflicts:
        lines.append("Unresolved conflicts:")
        lines += [" vs ".join(f"E{i + 1}" for i in c) for c in layout.conflicts]
    return SerializedEvidence(rep=layout.rep, text="\n".join(lines), id_map=id_map, n_units=len(layout.units),
                              n_relations=len(rel_lines), notes=dict(layout.notes))
