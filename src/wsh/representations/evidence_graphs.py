"""R4 (evidence graph: claims in graph-derived order + typed relation lines) and R5 (the same
claims in the same order, without relation lines).

Contrasts (all on identical claims):
    R1 vs R5 : effect of graph-derived ordering
    R5 vs R4 : effect of explicit edge labels
    R5 vs R3 : effect of step markers (when the path order equals the topological order)
R4P: R4 whose edges are model-predicted (RelationClassifier) instead of dataset-derived.
"""

from __future__ import annotations

from ..data.schemas import EvidenceBundle, RelationType
from .atomic_claims import claim_unit
from .evidence import topological_order
from .serialization import Layout

DIRECTED_LABEL = {
    RelationType.SUPPORTS: "SUPPORTS",
    RelationType.CONTRADICTS: "CONTRADICTS",
    RelationType.DUPLICATE: "DUPLICATES",
    RelationType.SUPERSEDES: "SUPERSEDES",
    RelationType.DEPENDS_ON: "DEPENDS_ON",
}


def layout(b: EvidenceBundle, rep: str = "R4", with_edges: bool = True, max_relations: int = 40) -> Layout:
    cm = b.claim_map()
    # relation controls (relation_controls.py) may fix the order and relabel edges; bundles without
    # these origin keys (all R4/R4P/R5 bundles) render exactly as before
    fixed = b.origin.get("fixed_order")
    # under a budget (Protocol B) a control bundle keeps only some facts: keep the fixed order, restricted
    order = [c for c in fixed if c in cm] if fixed else topological_order(b)
    label_override = b.origin.get("relation_label_override")
    idx = {cid: i for i, cid in enumerate(order)}
    units = [claim_unit(cm[c], b.provenance_visible) for c in order]
    rels: list[tuple[int, int, str]] = []
    if with_edges:
        for e in b.edges:
            if e.source in idx and e.target in idx and len(rels) < max_relations:
                r = (idx[e.source], idx[e.target], label_override or DIRECTED_LABEL[e.relation])
                if r not in rels:
                    rels.append(r)
    conflicts = []
    if with_edges:
        for cs in b.conflicts:
            unresolved = [idx[c] for c in cs.claim_ids if cs.resolution.get(c) == "unresolved" and c in idx]
            if len(unresolved) > 1:
                conflicts.append(unresolved)
    return Layout(rep, units, rels, conflicts, show_source=b.provenance_visible,
                  notes={"edge_status": sorted({e.status.value for e in b.edges}), "n_edges": len(b.edges)})
