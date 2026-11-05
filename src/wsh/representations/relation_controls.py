"""Fixed-order relation controls (revision-1; exploratory).

R4P (model-predicted relations) differs from R4 (derived relations) in three ways at once: the
relation lines, their number, and the order of the items, because R4P's order is recomputed from
the predicted graph. These controls change one factor at a time, on the identical fact set:

    name        order        relation lines                                     isolates
    R5          derived      none                                               (existing C0)
    R4          derived      derived                                            (existing C1)
    R4P_FO      derived      predicted (all types)                              predicted lines at fixed order (C2)
    R4P_FO_NC   derived      predicted minus CONTRADICTS                        contradiction lines (C2 vs C3)
    R4N_FO      derived      the same predicted pairs, neutral label            label semantics vs line count (C5)
    R5P         predicted    none                                               order only (C6, vs R5)
    R4P_NC      predicted    predicted minus CONTRADICTS                        contradiction lines at R4P's order
    R4P         predicted    predicted                                          (existing)
    R4P_FO_CN   derived      predicted; only CONTRADICTS relabelled neutral     targeted label intervention (A4)
    R4P_FO_NCPAD derived     predicted; each CONTRADICTS line replaced by a     contradiction content at matched
                             non-relational filler line at the same position    line count and length (A5)

R4P_FO_CN and R4P_FO_NCPAD were added in revision-2 (exploratory).

Journal revision (experiments/andreas_revision, Experiment B) adds two label-dependent controls. They need a
frozen file of HUMAN-adjudicated labels for every predicted CONTRADICTS pair of the question
(``exp1.contradiction_labels``); a question with any unlabelled pair is refused (pipeline error), never imputed:

    R4P_FO_SC    derived     predicted minus the CONTRADICTS lines humans verified  selective removal (B)
                             as false (genuine and ambiguous lines are kept)
    R4P_FO_SN    derived     predicted; only the verified-false CONTRADICTS lines   selective neutralisation (D)
                             relabelled RELATED_TO (endpoints, position, line count kept)

Both are refused when the 40-line relation cap would bind, so that every non-target line is exactly the one
shown in R4P_FO.

The neutral label asserts nothing about the pair ("RELATED_TO"), so R4N_FO has the same pairs, the same
number of lines and nearly the same tokens as R4P_FO. The oracle-corrected variants (R4P_FO_SC,
R4P_FO_SN) are defined only from human labels supplied in a frozen file; nothing is labelled automatically.
"""

from __future__ import annotations

import hashlib

from ..data.schemas import EvidenceBundle, RelationType
from .evidence import topological_order

NEUTRAL_LABEL = "RELATED_TO"
# a non-relational line of about the same length as "E3 CONTRADICTS E7"; names no item
FILLER_LINE = "(this line is intentionally left blank)"  # 7 Qwen tokens; "E3 CONTRADICTS E7" is 8

CONTROL_REPS: dict[str, dict[str, str]] = {
    "R4P_FO": {"order": "derived", "relations": "predicted"},
    "R4P_FO_NC": {"order": "derived", "relations": "predicted_no_contradicts"},
    "R4N_FO": {"order": "derived", "relations": "predicted_pairs_neutral_label"},
    "R5P": {"order": "predicted", "relations": "none"},
    "R4P_NC": {"order": "predicted", "relations": "predicted_no_contradicts"},
    "R4P_FO_CN": {"order": "derived", "relations": "predicted_contradicts_neutral_label"},
    "R4P_FO_NCPAD": {"order": "derived", "relations": "predicted_contradicts_as_filler"},
}
# label-dependent controls (Experiment B); kept out of CONTROL_REPS so label-free code paths are unchanged
LABEL_CONTROL_REPS: dict[str, dict[str, str]] = {
    "R4P_FO_SC": {"order": "derived", "relations": "predicted_minus_verified_false_contradicts"},
    "R4P_FO_SN": {"order": "derived", "relations": "predicted_verified_false_contradicts_neutral_label"},
}
LABEL_REPS = set(LABEL_CONTROL_REPS)
ALL_CONTROL_REPS = {**CONTROL_REPS, **LABEL_CONTROL_REPS}
PREDICTED_REPS = {"R4P", *ALL_CONTROL_REPS}
HUMAN_CLASSES = ("genuine", "false", "ambiguous")
MAX_RELATION_LINES = 40  # = evidence_graphs.layout(max_relations)


class IncompleteContradictionLabels(ValueError):
    """A label-dependent control was requested for a question whose predicted CONTRADICTS pairs are not all
    human-labelled (or whose relation lines would be capped)."""


def contradiction_pair_id(question_uid: str, source: str, target: str) -> str:
    """Identical to scripts/revision/contradictions.py export: sha256 of 'uid|(sorted claim-id tuple)'[:16].
    Both directions of a pair share the id."""
    pair = tuple(sorted((source, target)))
    return hashlib.sha256(f"{question_uid}|{pair}".encode()).hexdigest()[:16]


def control_bundle(rep: str, derived: EvidenceBundle, predicted: EvidenceBundle,
                   labels: dict[str, str] | None = None) -> EvidenceBundle:
    """A bundle whose facts are those of `derived` (= `predicted`, same claims), whose item order
    is fixed by the derived or the predicted graph, and whose rendered relations are a controlled
    function of the predicted edges. All choices are recorded in ``origin``."""
    spec = ALL_CONTROL_REPS[rep]
    if [c.claim_id for c in derived.claims] != [c.claim_id for c in predicted.claims]:
        raise ValueError(f"{derived.question_uid}: derived and predicted bundles do not share the same facts")
    b = predicted.model_copy(deep=True)
    order = topological_order(derived if spec["order"] == "derived" else predicted)
    edges = list(predicted.edges)
    removed = 0
    if spec["relations"].endswith("no_contradicts"):
        kept = [e for e in edges if e.relation != RelationType.CONTRADICTS]
        removed = len(edges) - len(kept)
        edges = kept
    edge_override: dict[str, str] = {}
    label_counts = None
    if rep in LABEL_REPS:
        edges, edge_override, label_counts = _apply_human_labels(rep, predicted, edges, labels)
        removed = len(predicted.edges) - len(edges)
    b.edges = edges
    origin = {**b.origin, "control": rep, "order_source": spec["order"], "relations": spec["relations"],
              "fixed_order": order, "n_predicted_edges": len(predicted.edges), "n_contradicts_removed": removed}
    if spec["relations"] == "predicted_pairs_neutral_label":
        origin["relation_label_override"] = NEUTRAL_LABEL
    elif spec["relations"] == "predicted_contradicts_neutral_label":
        origin["relation_label_map"] = {RelationType.CONTRADICTS.value: NEUTRAL_LABEL}
    elif spec["relations"] == "predicted_contradicts_as_filler":
        origin["relation_filler"] = {RelationType.CONTRADICTS.value: FILLER_LINE}
    if rep in LABEL_REPS:
        origin["human_label_counts"] = label_counts
        if edge_override:
            origin["relation_label_edge_override"] = edge_override
    b.origin = origin
    return b


def _apply_human_labels(rep: str, predicted: EvidenceBundle, edges: list, labels: dict[str, str] | None):
    q = predicted.question_uid
    if labels is None:
        raise IncompleteContradictionLabels(f"{q}: {rep} needs human contradiction labels; none supplied")
    if len(edges) > MAX_RELATION_LINES:
        raise IncompleteContradictionLabels(f"{q}: {len(edges)} predicted edges > {MAX_RELATION_LINES}; the relation "
                                            f"cap would bind, so {rep} could change non-target lines")
    pids = {contradiction_pair_id(q, e.source, e.target) for e in edges if e.relation == RelationType.CONTRADICTS}
    missing = sorted(pids - set(labels))
    if missing:
        raise IncompleteContradictionLabels(f"{q}: {len(missing)} of {len(pids)} predicted CONTRADICTS pairs have no "
                                            f"human label ({missing[:3]})")
    bad = {labels[p] for p in pids} - set(HUMAN_CLASSES)
    if bad:
        raise IncompleteContradictionLabels(f"{q}: invalid human label(s) {sorted(bad)}")
    counts = {c: sum(labels[p] == c for p in pids) for c in HUMAN_CLASSES}

    def is_false(e) -> bool:
        return e.relation == RelationType.CONTRADICTS and labels[contradiction_pair_id(q, e.source, e.target)] == "false"

    if rep == "R4P_FO_SC":
        return [e for e in edges if not is_false(e)], {}, counts
    return edges, {f"{e.source}|{e.target}": NEUTRAL_LABEL for e in edges if is_false(e)}, counts


def with_edges(rep: str) -> bool:
    return ALL_CONTROL_REPS[rep]["relations"] != "none"
