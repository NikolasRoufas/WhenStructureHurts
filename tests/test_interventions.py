import pytest

from wsh import interventions
from wsh.data.schemas import AnnotationStatus
from wsh.data.validation import validate_bundle
from wsh.interventions.base import n_affected
from wsh.representations.evidence import gold_bundle


@pytest.mark.parametrize("name,params", [("P1", {}), ("P2", {}), ("P3", {}), ("P4", {}), ("P5", {"mode": "strip"}),
                                         ("P5", {"mode": "duplicate"}), ("P6", {"op": "negation"}),
                                         ("P6", {"op": "temporal"}), ("P6", {"op": "entity"}), ("P6", {"op": "qualifier"})])
def test_determinism_and_validity(toy_question, name, params):
    b = gold_bundle(toy_question)
    a1, r1 = interventions.apply(name, b, toy_question, 0.4, 0, params)
    a2, r2 = interventions.apply(name, b, toy_question, 0.4, 0, params)
    assert a1.model_dump() == a2.model_dump() and r1.to_dict() == r2.to_dict()
    validate_bundle(a1)
    assert b.interventions == []  # input untouched


def test_rate_zero_is_identity(toy_question):
    b = gold_bundle(toy_question)
    for name in ["P1", "P2", "P3", "P4", "P6"]:
        out, rec = interventions.apply(name, b, toy_question, 0.0, 0, {})
        assert [c.model_dump() for c in out.claims] == [c.model_dump() for c in b.claims]
        assert rec.n_affected == 0 and rec.label_effect in ("preserved", "unavailable")


def test_n_affected_rule():
    assert n_affected(0.1, 3) == 1 and n_affected(0.4, 5) == 2 and n_affected(0.0, 5) == 0 and n_affected(0.2, 10) == 2


def test_p1_removes_required_and_flags_label(toy_question):
    b = gold_bundle(toy_question)
    out, rec = interventions.apply("P1", b, toy_question, 1.0, 0, {})
    assert rec.n_affected == 2 and not any(c.is_gold_support for c in out.claims)
    assert rec.label_effect in ("not_guaranteed", "answer_removed")
    assert all(e.source in out.claim_map() and e.target in out.claim_map() for e in out.edges)


def test_p6_corrupted_claims_never_gold(toy_question):
    b = gold_bundle(toy_question)
    out, rec = interventions.apply("P6", b, toy_question, 1.0, 0, {"op": "negation"})
    corrupted = [c for c in out.claims if c.is_corrupted]
    assert corrupted and all(not c.is_gold_support and c.status == AnnotationStatus.CORRUPTED for c in corrupted)
    assert any("not" not in ch["after"].split() for ch in rec.changes)
    out_t, rec_t = interventions.apply("P6", b, toy_question, 1.0, 0, {"op": "temporal"})
    assert all("2014" not in c.text for c in out_t.claims)


def test_p2_changes_relation_and_records(toy_question):
    b = gold_bundle(toy_question)
    out, rec = interventions.apply("P2", b, toy_question, 1.0, 0, {})
    assert rec.changes[0]["before"]["relation"] != rec.changes[0]["after"]["relation"]
    assert out.edges[0].status == AnnotationStatus.CORRUPTED


def test_p4_distractors_are_real_and_not_gold(toy_question):
    b = gold_bundle(toy_question)
    out, rec = interventions.apply("P4", b, toy_question, 0.4, 0, {"mode": "hard"})
    d = [c for c in out.claims if c.is_distractor]
    assert len(d) == rec.n_affected > 0
    for c in d:
        p = toy_question.passage(c.passage_id)
        assert c.text in p.text and not c.is_gold_support


def test_p7_unavailable_without_verified_spec(toy_question):
    b = gold_bundle(toy_question)
    _, rec = interventions.apply("P7", b, toy_question, 0.4, 0, {"spec_path": None})
    assert rec.label_effect == "unavailable" and not rec.applicable


def test_p7_with_spec(toy_question, tmp_path):
    import json
    spec = tmp_path / "t.jsonl"
    spec.write_text(json.dumps({"question_uid": toy_question.uid, "old": {"text": "A is CEO.", "date": "2010", "source": "s1"},
                                "new": {"text": "B is CEO.", "date": "2020", "source": "s2"}, "verified_by": "unit-test",
                                "status": "human_verified", "label_effect": "preserved"}) + "\n")
    out, rec = interventions.apply("P7", gold_bundle(toy_question), toy_question, 0.4, 0, {"spec_path": str(spec)})
    assert rec.applicable and any(e.relation.value == "SUPERSEDES" for e in out.edges)
    validate_bundle(out)
