"""Fixed-order relation controls (revision-1): fact preservation, order control, edge substitution."""
import pytest

from wsh.data.schemas import AnnotationStatus, Edge, RelationType
from wsh.experiments.common import make_layout
from wsh.models.prompts import build_request
from wsh.representations.evidence import gold_bundle, topological_order
from wsh.representations.protocols import check_equivalence, information_profile, layout_facts
from wsh.representations.relation_controls import CONTROL_REPS, NEUTRAL_LABEL, control_bundle
from wsh.representations.serialization import render


def _bundles(q):
    derived = gold_bundle(q)
    pred = derived.model_copy(deep=True)
    c = [x.claim_id for x in pred.claims]
    mk = lambda s, t, r: Edge(source=s, target=t, relation=r, confidence=0.9,  # noqa: E731
                              status=AnnotationStatus.MODEL_PREDICTED, method="test")
    # predicted graph: reversed dependency (so its order differs), a contradiction pair, a support edge
    pred.edges = [mk(c[0], c[-1], RelationType.DEPENDS_ON), mk(c[1], c[2], RelationType.CONTRADICTS),
                  mk(c[2], c[1], RelationType.CONTRADICTS), mk(c[0], c[1], RelationType.SUPPORTS)]
    return derived, pred


def _layout(rep, derived, pred):
    if rep in CONTROL_REPS:
        return make_layout(rep, control_bundle(rep, derived, pred))
    return make_layout(rep, pred if rep == "R4P" else derived)


def test_all_controls_show_identical_facts(toy_question):
    derived, pred = _bundles(toy_question)
    facts = {rep: layout_facts(_layout(rep, derived, pred)) for rep in ["R1", "R4", "R5", "R4P", *CONTROL_REPS]}
    ref = facts["R1"]
    assert all(f == ref for f in facts.values())


def test_order_is_controlled(toy_question):
    derived, pred = _bundles(toy_question)
    order = lambda rep: [u.claim_ids[0] for u in _layout(rep, derived, pred).units]  # noqa: E731
    assert topological_order(derived) != topological_order(pred)  # the fixture really changes order
    assert order("R4P_FO") == order("R4P_FO_NC") == order("R4N_FO") == order("R5") == order("R4")
    assert order("R5P") == order("R4P_NC") == order("R4P")


def test_contradiction_removal_changes_only_contradiction_lines(toy_question):
    derived, pred = _bundles(toy_question)
    full = _layout("R4P_FO", derived, pred).relations
    nc = _layout("R4P_FO_NC", derived, pred).relations
    assert [r for r in full if r[2] != "CONTRADICTS"] == nc
    assert sum(r[2] == "CONTRADICTS" for r in full) == 2
    b = control_bundle("R4P_FO_NC", derived, pred)
    assert b.origin["n_contradicts_removed"] == 2 and b.origin["n_predicted_edges"] == 4


def test_neutral_label_keeps_pairs_and_count(toy_question):
    derived, pred = _bundles(toy_question)
    full = _layout("R4P_FO", derived, pred).relations
    neu = _layout("R4N_FO", derived, pred).relations
    assert [(a, b) for a, b, _ in full] == [(a, b) for a, b, _ in neu]
    assert {lab for _, _, lab in neu} == {NEUTRAL_LABEL}


def test_existing_representations_unchanged(toy_question):
    """Bundles without control keys render exactly as before (order from their own edges)."""
    derived, pred = _bundles(toy_question)
    for rep, b in (("R4", derived), ("R4P", pred), ("R5", derived)):
        lay = make_layout(rep, b)
        assert [u.claim_ids[0] for u in lay.units] == topological_order(b)
        assert "fixed_order" not in b.origin
    assert {lab for _, _, lab in make_layout("R4P", pred).relations} <= {"DEPENDS_ON", "CONTRADICTS", "SUPPORTS"}


def test_prompts_differ_only_in_relation_labels(toy_question):
    derived, pred = _bundles(toy_question)
    t_full = render(_layout("R4P_FO", derived, pred)).text
    t_neu = render(_layout("R4N_FO", derived, pred)).text
    for lab in ("CONTRADICTS", "SUPPORTS", "DEPENDS_ON"):
        t_full = t_full.replace(lab, NEUTRAL_LABEL)
    assert t_full == t_neu
    r1 = build_request(toy_question, render(_layout("R4P_FO", derived, pred)).text, 64)
    r2 = build_request(toy_question, render(_layout("R4N_FO", derived, pred)).text, 64)
    assert (r1.system, r1.prefill) == (r2.system, r2.prefill)


def test_information_equivalence_holds_across_controls(toy_question):
    derived, pred = _bundles(toy_question)
    count = lambda t: len(t.split())  # noqa: E731
    prof = {}
    for rep in ["R0", "R1", "R4", "R5", "R4P", *CONTROL_REPS]:
        b = control_bundle(rep, derived, pred) if rep in CONTROL_REPS else (pred if rep == "R4P" else derived)
        lay = make_layout(rep, b)
        ser = render(lay)
        prof[rep] = information_profile(rep, lay, ser, b, toy_question, count)
    check_equivalence(prof)  # raises on any fact-set difference
    assert prof["R4N_FO"]["added_information"][1].startswith("explicit_relations:predicted_pairs_neutral_label")


def test_control_bundle_refuses_different_facts(toy_question):
    derived, pred = _bundles(toy_question)
    pred.claims = pred.claims[:-1]
    with pytest.raises(ValueError):
        control_bundle("R4P_FO", derived, pred)
