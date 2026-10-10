import pytest

from wsh.config import EGRAGConfig
from wsh.data.schemas import AnnotationStatus, Edge, RelationType
from wsh.egrag.belief_propagation import claim_features, initial_belief, propagate
from wsh.egrag.graph_selection import resolve_conflicts, select_subgraph
from wsh.evaluation.statistics import by_question, holm, paired_bootstrap
from wsh.experiments.exp4_adaptive_selection import LeakageError, LogisticSelector, check_features, split_questions
from wsh.representations.evidence import gold_bundle


def test_paired_bootstrap_known_cases():
    a = {f"q{i}": 0.0 for i in range(50)}
    b = {f"q{i}": 1.0 for i in range(50)}
    r = paired_bootstrap(a, b)
    assert r["delta"] == 1.0 and r["ci"] == [1.0, 1.0] and r["verdict"] == "b > a" and r["n_paired"] == 50
    same = paired_bootstrap(a, dict(a))
    assert same["verdict"].startswith("inconclusive") and "equivalence" in same["verdict"]
    tiny = paired_bootstrap({"q": 0.0}, {"q": 1.0})
    assert tiny["power_note"] == "underpowered/exploratory"
    part = paired_bootstrap({"q1": 0, "q2": 0}, {"q2": 1, "q3": 1})
    assert part["n_paired"] == 1 and part["n_only_a"] == 1 and part["n_only_b"] == 1


def test_repeated_runs_are_averaged_within_question():
    recs = [{"question_uid": "q1", "v": 1.0}, {"question_uid": "q1", "v": 0.0}, {"question_uid": "q2", "v": 1.0}]
    assert by_question(recs, lambda r: r["v"]) == {"q1": 0.5, "q2": 1.0}


def test_holm():
    adj = holm({"a": 0.01, "b": 0.04, "c": None})
    assert adj["a"] == pytest.approx(0.02) and adj["b"] == pytest.approx(0.04) and adj["c"] is None


def _edge(s, t, rel, conf=0.9):
    return Edge(source=s, target=t, relation=rel, confidence=conf, status=AnnotationStatus.MODEL_PREDICTED, method="t")


def test_propagation_signs_and_no_propagation_ablation(toy_question):
    b = gold_bundle(toy_question)
    c = [x.claim_id for x in b.claims]
    edges = [_edge(c[0], c[1], RelationType.SUPPORTS), _edge(c[2], c[3], RelationType.CONTRADICTS)]
    feats = claim_features(b.claims, edges, toy_question.question, {})
    b0 = {k: initial_belief(f, EGRAGConfig().theta) for k, f in feats.items()}
    bel, tr = propagate(b.claims, edges, b0, EGRAGConfig())
    assert bel[c[1]] > b0[c[1]] and bel[c[3]] < b0[c[3]] and tr["converged"]
    off, tr2 = propagate(b.claims, edges, b0, EGRAGConfig(propagate=False))
    assert off == b0 and tr2["iterations"] == 0


def test_conflict_resolution_margin(toy_question):
    b = gold_bundle(toy_question)
    c = [x.claim_id for x in b.claims]
    edges = [_edge(c[0], c[1], RelationType.CONTRADICTS)]
    close = resolve_conflicts(b.claims, edges, {c[0]: 0.6, c[1]: 0.58}, margin=0.1)
    assert set(close[0].resolution.values()) == {"unresolved"}
    far = resolve_conflicts(b.claims, edges, {c[0]: 0.9, c[1]: 0.2}, margin=0.1)
    assert far[0].resolution[c[0]] == "preferred" and far[0].resolution[c[1]] == "rejected"


def test_selection_respects_budget(toy_question):
    b = gold_bundle(toy_question)
    ids = [x.claim_id for x in b.claims]
    bel = {i: 0.5 for i in ids}
    util = {i: 0.5 for i in ids}
    cfg = EGRAGConfig(token_budget=30)
    count = lambda t: len(t.split())  # noqa: E731
    for selector in ("greedy_connected", "top_claim"):
        sel, tr = select_subgraph(b.claims, b.edges, bel, util, toy_question.question,
                                  cfg.model_copy(update={"selector": selector}), count)
        assert tr["tokens"] <= 30 and sel


def test_exp4_leakage_guards():
    with pytest.raises(LeakageError):
        check_features(["q_tokens", "gold_coverage"])
    with pytest.raises(LeakageError):
        LogisticSelector(["answer_in_evidence"])
    tr, te = split_questions([f"q{i}" for i in range(100)], 0.5, 0)
    assert not set(tr) & set(te) and len(tr) + len(te) == 100
    assert split_questions([f"q{i}" for i in range(100)], 0.5, 0) == (tr, te)
