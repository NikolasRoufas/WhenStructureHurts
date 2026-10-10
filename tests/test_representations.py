from wsh.data.schemas import AnnotationStatus, RelationType
from wsh.experiments.common import make_layout
from wsh.representations.evidence import gold_bundle, topological_order
from wsh.representations.serialization import render
from wsh.text import content_tokens


def test_gold_edges_and_path_from_annotations(toy_question):
    b = gold_bundle(toy_question)
    dep = [e for e in b.edges if e.relation == RelationType.DEPENDS_ON]
    assert len(dep) == 1
    p0, p1 = toy_question.passages[0].passage_id, toy_question.passages[1].passage_id
    # "Google was founded..." depends on "DeepMind was acquired by Google..."
    assert dep[0].source == f"{p1}#s00" and dep[0].target == f"{p0}#s01"
    assert dep[0].status == AnnotationStatus.DETERMINISTIC_DERIVED and dep[0].meta["anchor_match"] == "exact"
    assert b.path_status == AnnotationStatus.DETERMINISTIC_DERIVED
    # step claims keep context order (support-first ordering would leak the supporting-fact
    # annotation into R3 only)
    assert b.path[0].claim_ids == [f"{p0}#s00", f"{p0}#s01", f"{p0}#s02"]


def test_all_representations_carry_identical_content(toy_question):
    b = gold_bundle(toy_question)
    texts = {}
    for rep in ["R0", "R1", "R2", "R3", "R4", "R5"]:
        ser = render(make_layout(rep, b, seed=0))
        body = [ln for ln in ser.text.splitlines() if ln.startswith("[E")]
        texts[rep] = sorted(t for ln in body for t in content_tokens(ln.split(") ", 1)[1]))
    assert len({tuple(v) for v in texts.values()}) == 1  # information-equivalent in gold scope


def test_r4_has_relations_r5_does_not(toy_question):
    b = gold_bundle(toy_question)
    r4 = render(make_layout("R4", b))
    r5 = render(make_layout("R5", b))
    assert "Relations:" in r4.text and "DEPENDS_ON" in r4.text
    assert "Relations:" not in r5.text
    assert [ln for ln in r4.text.splitlines() if ln.startswith("[E")] == [ln for ln in r5.text.splitlines() if ln.startswith("[E")]


def test_display_ids_map_back_to_claims(toy_question):
    b = gold_bundle(toy_question)
    ser = render(make_layout("R1", b))
    assert list(ser.id_map) == [f"E{i + 1}" for i in range(len(b.claims))]
    for did, item in ser.id_map.items():
        assert item["claim_ids"][0] in b.claim_map()


def test_r2_shuffle_deterministic_and_seed_dependent(toy_question):
    b = gold_bundle(toy_question)
    a = render(make_layout("R2", b, seed=0)).text
    assert a == render(make_layout("R2", b, seed=0)).text
    others = {render(make_layout("R2", b, seed=s)).text for s in range(1, 6)}
    assert any(o != a for o in others)


def test_topological_order_puts_dependency_first(toy_question):
    b = gold_bundle(toy_question)
    b.claims = list(reversed(b.claims))  # adversarial input order
    order = topological_order(b)
    p0, p1 = toy_question.passages[0].passage_id, toy_question.passages[1].passage_id
    assert order.index(f"{p0}#s01") < order.index(f"{p1}#s00")
