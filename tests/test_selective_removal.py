"""Journal revision, Experiment B: label-dependent contradiction controls R4P_FO_SC / R4P_FO_SN.

Only human-verified-false CONTRADICTS lines may change; facts, order, question text and every other relation
line must be identical to R4P_FO; incomplete labels and a binding relation cap are refused."""
import pytest

from wsh.data.schemas import AnnotationStatus, Edge, RelationType
from wsh.experiments.common import make_layout
from wsh.models.prompts import build_request
from wsh.representations.protocols import layout_facts
from wsh.representations.relation_controls import (CONTROL_REPS, LABEL_REPS, NEUTRAL_LABEL,
                                                   IncompleteContradictionLabels, contradiction_pair_id,
                                                   control_bundle)
from wsh.representations.evidence import gold_bundle
from wsh.representations.serialization import render


def _mk(s, t, r):
    return Edge(source=s, target=t, relation=r, confidence=0.95, status=AnnotationStatus.MODEL_PREDICTED, method="test")


def _bundles(q, extra_edges=0):
    derived = gold_bundle(q)
    pred = derived.model_copy(deep=True)
    c = [x.claim_id for x in pred.claims]
    assert len(c) >= 4
    pred.edges = [_mk(c[0], c[-1], RelationType.DEPENDS_ON),
                  _mk(c[1], c[2], RelationType.CONTRADICTS), _mk(c[2], c[1], RelationType.CONTRADICTS),  # pair X
                  _mk(c[0], c[3], RelationType.CONTRADICTS),                                             # pair Y
                  _mk(c[0], c[1], RelationType.SUPPORTS)]
    pred.edges += [_mk(c[0], c[1], RelationType.SUPPORTS) for _ in range(extra_edges)]
    x = contradiction_pair_id(q.uid, c[1], c[2])
    y = contradiction_pair_id(q.uid, c[0], c[3])
    return derived, pred, x, y


def _text(rep, derived, pred, labels=None):
    b = control_bundle(rep, derived, pred, labels) if rep in LABEL_REPS else (
        control_bundle(rep, derived, pred) if rep in CONTROL_REPS else pred)
    return b, render(make_layout(rep, b)).text


def test_pair_id_is_direction_free_and_matches_export_formula(toy_question):
    import hashlib
    q = toy_question.uid
    assert contradiction_pair_id(q, "a#1", "b#2") == contradiction_pair_id(q, "b#2", "a#1")
    assert contradiction_pair_id(q, "a#1", "b#2") == hashlib.sha256(f"{q}|{('a#1', 'b#2')}".encode()).hexdigest()[:16]


def test_selective_removal_drops_only_false_lines(toy_question):
    derived, pred, x, y = _bundles(toy_question)
    _, t_fo = _text("R4P_FO", derived, pred)
    b, t_sc = _text("R4P_FO_SC", derived, pred, {x: "false", y: "genuine"})
    fo_lines, sc_lines = t_fo.split("\n"), t_sc.split("\n")
    removed = [ln for ln in fo_lines if ln not in sc_lines]
    assert len(removed) == 2 and all(" CONTRADICTS " in ln for ln in removed)   # both directions of pair X
    assert [ln for ln in fo_lines if ln not in removed] == sc_lines            # everything else identical, same order
    assert b.origin["human_label_counts"] == {"genuine": 1, "false": 1, "ambiguous": 0}
    assert b.origin["n_contradicts_removed"] == 2


def test_selective_equals_original_when_nothing_false_and_equals_nc_when_all_false(toy_question):
    derived, pred, x, y = _bundles(toy_question)
    _, t_fo = _text("R4P_FO", derived, pred)
    _, t_nc = _text("R4P_FO_NC", derived, pred)
    assert _text("R4P_FO_SC", derived, pred, {x: "genuine", y: "ambiguous"})[1] == t_fo
    assert _text("R4P_FO_SC", derived, pred, {x: "false", y: "false"})[1] == t_nc


def test_neutralisation_keeps_endpoints_position_and_count(toy_question):
    derived, pred, x, y = _bundles(toy_question)
    _, t_fo = _text("R4P_FO", derived, pred)
    _, t_sn = _text("R4P_FO_SN", derived, pred, {x: "false", y: "genuine"})
    a, b = t_fo.split("\n"), t_sn.split("\n")
    assert len(a) == len(b)
    diff = [(u, v) for u, v in zip(a, b) if u != v]
    assert len(diff) == 2
    assert all(u.replace(" CONTRADICTS ", f" {NEUTRAL_LABEL} ") == v for u, v in diff)


def test_facts_order_and_question_identical(toy_question):
    derived, pred, x, y = _bundles(toy_question)
    labels = {x: "false", y: "genuine"}
    lays = {r: make_layout(r, control_bundle(r, derived, pred, labels) if r in LABEL_REPS else control_bundle(r, derived, pred))
            for r in ("R4P_FO", "R4P_FO_NC", "R4P_FO_SC", "R4P_FO_SN")}
    facts = {r: layout_facts(l) for r, l in lays.items()}
    order = {r: [u.claim_ids for u in l.units] for r, l in lays.items()}
    assert len({str(v) for v in facts.values()}) == 1 and len({str(v) for v in order.values()}) == 1
    texts = {r: render(l).text for r, l in lays.items()}
    reqs = {r: build_request(toy_question, t, 64) for r, t in texts.items()}
    assert len({r.system for r in reqs.values()}) == 1
    assert all(r.user.endswith(reqs["R4P_FO"].user.split("Question:")[1]) for r in reqs.values())
    for t in texts.values():                      # no gold answer enters through the intervention
        assert t.split("Relations:")[0] == texts["R4P_FO"].split("Relations:")[0]


@pytest.mark.parametrize("rep", sorted(LABEL_REPS))
def test_incomplete_labels_are_refused(toy_question, rep):
    derived, pred, x, y = _bundles(toy_question)
    with pytest.raises(IncompleteContradictionLabels):
        control_bundle(rep, derived, pred, {x: "false"})
    with pytest.raises(IncompleteContradictionLabels):
        control_bundle(rep, derived, pred, None)
    with pytest.raises(IncompleteContradictionLabels):
        control_bundle(rep, derived, pred, {x: "false", y: "maybe"})


@pytest.mark.parametrize("rep", sorted(LABEL_REPS))
def test_binding_relation_cap_is_refused(toy_question, rep):
    derived, pred, x, y = _bundles(toy_question, extra_edges=40)
    with pytest.raises(IncompleteContradictionLabels, match="cap"):
        control_bundle(rep, derived, pred, {x: "false", y: "genuine"})


def test_label_reps_not_in_label_free_registry():
    assert not (LABEL_REPS & set(CONTROL_REPS))
