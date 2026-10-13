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

The neutral label asserts nothing about the pair ("RELATED_TO"), so R4N_FO has the same pairs, the same
number of lines and nearly the same tokens as R4P_FO. An oracle-corrected variant (remove only
contradictions verified as wrong) needs human error labels and is deliberately not implemented.
"""

from __future__ import annotations

from ..data.schemas import EvidenceBundle, RelationType
from .evidence import topological_order

NEUTRAL_LABEL = "RELATED_TO"
# a non-relational line of about the same length as "E3 CONTRADICTS E7"; names no item
FILLER_LINE = "(line intentionally left blank)"

CONTROL_REPS: dict[str, dict[str, str]] = {
    "R4P_FO": {"order": "derived", "relations": "predicted"},
    "R4P_FO_NC": {"order": "derived", "relations": "predicted_no_contradicts"},
    "R4N_FO": {"order": "derived", "relations": "predicted_pairs_neutral_label"},
    "R5P": {"order": "predicted", "relations": "none"},
    "R4P_NC": {"order": "predicted", "relations": "predicted_no_contradicts"},
    "R4P_FO_CN": {"order": "derived", "relations": "predicted_contradicts_neutral_label"},
    "R4P_FO_NCPAD": {"order": "derived", "relations": "predicted_contradicts_as_filler"},
}
PREDICTED_REPS = {"R4P", *CONTROL_REPS}


def control_bundle(rep: str, derived: EvidenceBundle, predicted: EvidenceBundle) -> EvidenceBundle:
    """A bundle whose facts are those of `derived` (= `predicted`, same claims), whose item order
    is fixed by the derived or the predicted graph, and whose rendered relations are a controlled
    function of the predicted edges. All choices are recorded in ``origin``."""
    spec = CONTROL_REPS[rep]
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
    b.edges = edges
    origin = {**b.origin, "control": rep, "order_source": spec["order"], "relations": spec["relations"],
              "fixed_order": order, "n_predicted_edges": len(predicted.edges), "n_contradicts_removed": removed}
    if spec["relations"] == "predicted_pairs_neutral_label":
        origin["relation_label_override"] = NEUTRAL_LABEL
    elif spec["relations"] == "predicted_contradicts_neutral_label":
        origin["relation_label_map"] = {RelationType.CONTRADICTS.value: NEUTRAL_LABEL}
    elif spec["relations"] == "predicted_contradicts_as_filler":
        origin["relation_filler"] = {RelationType.CONTRADICTS.value: FILLER_LINE}
    b.origin = origin
    return b


def with_edges(rep: str) -> bool:
    return CONTROL_REPS[rep]["relations"] != "none"
