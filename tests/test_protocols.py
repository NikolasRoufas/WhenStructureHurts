"""Exp1 Protocol A (information-controlled) and Protocol B (budget-controlled)."""

import pytest

from conftest import FakeGenerator
from wsh.artifacts import RunContext
from wsh.cache import KVCache
from wsh.config import load_config
from wsh.data.schemas import AnnotationStatus, Edge, RelationType
from wsh.evaluation.evaluator import evaluate
from wsh.experiments import exp1_representations
from wsh.experiments.common import Runner, make_layout
from wsh.representations.evidence import gold_bundle
from wsh.representations.protocols import (BudgetViolation, InformationEquivalenceViolation, added_information,
                                           budget_select, check_equivalence, edge_stratum, information_profile,
                                           parse_budget, rank_facts, restrict_bundle)
from wsh.representations.serialization import render

REPS = ["R0", "R1", "R2", "R3", "R4", "R5"]


def count(t):
    return len(t.split())


def _profiles(q, b, reps=REPS):
    out = {}
    for rep in reps:
        lay = make_layout(rep, b, 0)
        ser = render(lay)
        out[rep] = information_profile(rep, lay, ser, b, q, count)
    return out


# 1. identical evidence facts whenever a condition claims information equivalence
def test_protocol_a_fact_sets_identical(toy_question):
    b = gold_bundle(toy_question)
    prof = _profiles(toy_question, b)
    assert len({p["fact_digest"] for p in prof.values()}) == 1
    assert prof["R0"]["fact_ids"] == prof["R4"]["fact_ids"] == [c.claim_id for c in b.claims]
    check_equivalence(prof)  # no exception


def test_protocol_a_violation_is_detected(toy_question):
    b = gold_bundle(toy_question)
    prof = _profiles(toy_question, b, ["R0", "R1"])
    short = restrict_bundle(b, {c.claim_id for c in b.claims[1:]})
    prof["R1"] = information_profile("R1", make_layout("R1", short), render(make_layout("R1", short)), short,
                                     toy_question, count)
    with pytest.raises(InformationEquivalenceViolation):
        check_equivalence(prof)


def test_added_information_is_named(toy_question):
    b = gold_bundle(toy_question)
    assert added_information("R0", b) == [] and added_information("R1", b) == []
    assert added_information("R2", b) == ["order:random"]
    assert added_information("R3", b) == ["step_grouping_and_order:deterministic_derived"]
    assert added_information("R5", b) == ["passage_order_from_edges:B_derived_exact_anchor"]
    assert "explicit_relations:B_derived_exact_anchor" in added_information("R4", b)


def test_overhead_measured_separately(toy_question):
    b = gold_bundle(toy_question)
    prof = _profiles(toy_question, b)
    assert len({p["content_tokens"] for p in prof.values()}) == 1  # same facts, same content
    assert prof["R4"]["overhead_tokens"] > prof["R5"]["overhead_tokens"]  # relation lines cost tokens
    assert all(p["evidence_tokens"] == p["content_tokens"] + p["overhead_tokens"] for p in prof.values())


# 2. shuffling alone does not change order-invariant coverage metrics
def test_shuffle_does_not_change_coverage(toy_question):
    b = gold_bundle(toy_question)
    keys = ("support_coverage", "content_recall", "answer_in_evidence", "hop_answer_coverage", "evidence_sufficient")
    vals = set()
    for rep, seed in [("R1", 0)] + [("R2", s) for s in range(8)]:
        ev = evaluate(toy_question, "Answer: x", "eos", render(make_layout(rep, b, seed)), b)["eval"]
        vals.add(tuple(ev[k] for k in keys))
    assert len(vals) == 1


# 3. token limits are respected; 4. truncation is logged
@pytest.mark.parametrize("policy", ["shared", "per_representation"])
@pytest.mark.parametrize("budget", [5, 20, 40, 80, 400])
def test_budget_respected_and_logged(toy_question, policy, budget):
    b = gold_bundle(toy_question)
    variants = {rep: (b, (lambda sub, rep=rep: make_layout(rep, sub, 0))) for rep in REPS}
    ranking = rank_facts(b, toy_question, "relevance")
    sel = budget_select(variants, toy_question, budget, ranking, policy, count)
    for rep, (sub, lay, ser, acct) in sel.items():
        assert ser.evidence_tokens <= budget and count(ser.text) <= budget
        kept = {c.claim_id for c in sub.claims}
        assert kept == set(ranking[:acct["n_facts_kept"]])  # whole facts in ranking order, nothing else
        assert [d["claim_id"] for d in ser.dropped] == [c for c in ranking if c not in kept]
        assert acct["n_facts_kept"] + acct["n_facts_dropped"] == acct["n_facts_total"] == len(b.claims)
        assert acct["truncated"] == bool(ser.dropped)
        assert all({"gold_support", "answer_bearing"} <= set(d) for d in ser.dropped)
        assert all(e.source in kept and e.target in kept for e in sub.edges)
    if policy == "shared":
        assert len({a["kept_fact_digest"] for *_, a in sel.values()}) == 1
    if budget == 400:
        assert not any(a["truncated"] for *_, a in sel.values())


def test_verbose_representation_keeps_fewer_facts_per_representation(toy_question):
    b = gold_bundle(toy_question)
    variants = {rep: (b, (lambda sub, rep=rep: make_layout(rep, sub, 0))) for rep in ("R0", "R4")}
    ranking = rank_facts(b, toy_question, "relevance")
    full_r0 = count(render(make_layout("R0", b)).text)
    sel = budget_select(variants, toy_question, full_r0, ranking, "per_representation", count)
    assert sel["R0"][3]["n_facts_kept"] == len(b.claims)
    assert sel["R4"][3]["n_facts_kept"] < len(b.claims)  # pays for its IDs/titles/relations with facts


# 5. answer-bearing information loss is measured, not hidden
def test_answer_bearing_loss_is_measured(toy_question):
    b = gold_bundle(toy_question)
    answer_claim = next(c.claim_id for c in b.claims if "Larry Page" in c.text)
    ranking = [c.claim_id for c in b.claims if c.claim_id != answer_claim] + [answer_claim]
    variants = {"R1": (b, lambda sub: make_layout("R1", sub, 0))}
    budget = count(render(make_layout("R1", restrict_bundle(b, set(ranking[:2])))).text)
    sub, lay, ser, acct = budget_select(variants, toy_question, budget, ranking, "shared", count)["R1"]
    assert acct["answer_bearing_facts_total"] == 1 and acct["answer_bearing_facts_dropped"] == 1
    assert any(d["claim_id"] == answer_claim and d["answer_bearing"] for d in ser.dropped)
    ev = evaluate(toy_question, "Answer: Larry Page", "eos", ser, sub)["eval"]
    assert ev["answer_in_evidence"] == 0.0 and ev["evidence_sufficient"] == 0.0
    assert acct["required_facts_dropped"] >= 1


def test_selection_policies(toy_question):
    b = gold_bundle(toy_question)
    sf = rank_facts(b, toy_question, "support_first")
    gold = [c.claim_id for c in b.claims if c.is_gold_support]
    assert sf[:len(gold)] == [c for c in sf if c in gold] and set(sf[:len(gold)]) == set(gold)
    assert rank_facts(b, toy_question, "relevance") == rank_facts(b, toy_question, "relevance")  # deterministic
    with pytest.raises(ValueError):
        rank_facts(b, toy_question, "oracle_answer")


def test_parse_budget():
    assert parse_budget("abs:300", 999) == 300 and parse_budget("content:0.5", 200) == 100
    with pytest.raises(ValueError):
        parse_budget("min_matched", 100)


def test_edge_strata(toy_question):
    b = gold_bundle(toy_question)
    e = b.edges[0]
    assert edge_stratum(e) == "B_derived_exact_anchor"
    assert edge_stratum(e.model_copy(update={"meta": {**e.meta, "anchor_match": "fallback"}})) == "C_derived_fallback_anchor"
    assert edge_stratum(e.model_copy(update={"status": AnnotationStatus.HUMAN_VERIFIED})) == "A_human_verified"
    assert edge_stratum(e.model_copy(update={"status": AnnotationStatus.MODEL_PREDICTED})) == "D_model_predicted"


# end-to-end through the runner (software mock generator; never a reported result)
class _Res:
    def __init__(self, gen):
        self.generator = gen
        self.nli_grounding = None
        self.cache = KVCache(None)
        self.loaded = {}

    def count_tokens(self, t):
        return len(t.split())

    def apply_verified(self, q, b):
        pass


def test_exp1_records_keep_protocols_separate(tmp_path, toy_question):
    cfg = load_config("configs/smoke.yaml", {"results_root": str(tmp_path), "exp1.representations": REPS,
                                             "exp1.budgets": ["content:0.5"],
                                             "exp1.budget_policies": ["shared", "per_representation"]})
    ctx = RunContext(cfg, "exp1")
    runner = Runner(cfg, ctx, _Res(FakeGenerator(default="Answer: Larry Page\nEvidence: E1")))
    exp1_representations.body(runner, {"toy": [toy_question]})
    import json

    recs = [json.loads(x) for x in (ctx.dir / "predictions.jsonl").read_text().splitlines()]
    assert not [r for r in recs if r.get("pipeline_error")], [r.get("pipeline_error") for r in recs]
    a = [r for r in recs if r["condition"]["protocol"] == "A"]
    bb = [r for r in recs if r["condition"]["protocol"] == "B"]
    assert len(a) == len(REPS) and len(bb) == 2 * len(REPS)
    assert len({r["info"]["information"]["fact_digest"] for r in a}) == 1
    for r in bb:
        assert r["evidence"]["evidence_tokens"] <= r["evidence"]["budget"]
        assert "budget_accounting" in r["info"] and r["info"]["budget_accounting"]["policy"] == r["condition"]["policy"]
    from wsh.evaluation.reporting import contrasts

    for c in contrasts(recs, "exp1"):
        assert "protocol=A" in c["stratum"] or "protocol=B" in c["stratum"]
        assert not c["confirmatory"]  # smoke stage is never confirmatory
        assert 0 <= c["n_identical_evidence"] <= c["n_paired"]
        assert "delta" in c["coverage_delta"]
    r1r5 = [c for c in contrasts(recs, "exp1") if (c["a"], c["b"]) == ("R1", "R5") and c["edge_stratum"] == "all"
            and "protocol=A" in c["stratum"]]
    # toy graph order (DeepMind -> Google) equals the context order, so R5 shows exactly R1's
    # evidence: the pair can only contribute a zero difference and is counted as such
    assert r1r5 and r1r5[0]["n_identical_evidence"] == 1
    assert r1r5[0]["informative_pairs"]["n_paired"] == 0  # the only pair is uninformative
