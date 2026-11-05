"""Journal-revision tooling (experiments/andreas_revision): statistics, annotation import/agreement/adjudication,
precision, Experiment B selection/labels/analysis checks. All labels below are SYNTHETIC TEST FIXTURES."""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "experiments" / "andreas_revision"
sys.path.insert(0, str(ROOT))


def _mod(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


arlib = _mod("arlib.py", "arlib")
at = _mod("annotation/annotation_tools.py", "annotation_tools")
sel = _mod("selective_removal/select_questions.py", "select_questions")
xb = _mod("selective_removal/analysis.py", "expb_analysis")


# ------------------------------------------------------------------ statistics

def test_unstratified_bootstrap_reproduces_project_bootstrap():
    from wsh.evaluation.statistics import paired_bootstrap
    import random
    rng = random.Random(3)
    a = {f"q{i}": float(rng.random() < 0.5) for i in range(150)}
    b = {q: float(rng.random() < 0.4) for q in a}
    ref, mine = paired_bootstrap(a, b), arlib.paired_bootstrap_strat(a, b)
    assert mine["delta"] == pytest.approx(ref["delta"]) and mine["ci"] == ref["ci"] and mine["p_boot"] == ref["p_boot"]


def test_stratified_bootstrap_requires_matching_keys_and_is_seeded():
    a, b = {"x": 0.0, "y": 1.0}, {"x": 1.0}
    with pytest.raises(ValueError):
        arlib.paired_bootstrap_strat(a, b)
    a = {f"q{i}": float(i % 2) for i in range(40)}
    b = {q: 1.0 for q in a}
    s = {q: q[-1] for q in a}
    assert arlib.paired_bootstrap_strat(a, b, s) == arlib.paired_bootstrap_strat(a, b, s)


def test_kappa_wilson_transitions():
    assert arlib.cohen_kappa(list("aabb"), list("aabb")) == 1.0
    assert arlib.cohen_kappa(list("ab"), list("ba")) == pytest.approx(-1.0)
    lo, hi = arlib.wilson(5, 10)
    assert lo == pytest.approx(0.2366, abs=1e-3) and hi == pytest.approx(0.7634, abs=1e-3)
    t = arlib.transitions({"q": "C", "r": "A"}, {"q": "W", "r": "A"})
    assert len(t) == 9 and t["C->W"] == 1 and t["A->A"] == 1 and sum(t.values()) == 2


def test_label_mapping_is_total_and_three_valued():
    assert {arlib.to3(x) for x in arlib.LABELS7} == set(arlib.CLASSES3)
    with pytest.raises(ValueError):
        arlib.to3("probably_false")


# ------------------------------------------------------------------ annotation workflow (synthetic fixture)

def _pkg(tmp_path, l1, l2, ann=("ann1", "ann2"), n=6):
    key = {f"p{i}": {"question_uid": f"ds/q{i // 2}", "dataset": "ds" if i < 4 else "ds2"} for i in range(n)}
    for a, labs, who in ((1, l1, ann[0]), (2, l2, ann[1])):
        with open(tmp_path / f"pairs_annotator{a}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=at.COLS)
            w.writeheader()
            for i, p in enumerate(key):
                w.writerow({c: "" for c in at.COLS} | {"item": i + 1, "pair_id": p, "label_with_context": labs[i],
                                                         "label_sentences_only": labs[i], "annotator": who if labs[i] else ""})
    (tmp_path / "key.json").write_text(json.dumps(key))
    return tmp_path / "key.json"


G, E, T, U = "genuine_contradiction", "compatible_different_entities", "compatible_different_times_or_values", "uncertain"


def test_import_refuses_invalid_unsigned_or_shared_annotator(tmp_path):
    key = _pkg(tmp_path, [G, E, "nonsense", E, G, E], [G] * 6)
    with pytest.raises(SystemExit, match="invalid"):
        at.cmd_validate(tmp_path, key)
    key = _pkg(tmp_path, [G] * 6, [G] * 6, ann=("same", "same"))
    with pytest.raises(SystemExit, match="independent"):
        at.cmd_validate(tmp_path, key)
    key = _pkg(tmp_path, [G] * 6, [G] * 6)
    rows = list(csv.DictReader(open(tmp_path / "pairs_annotator1.csv")))
    rows[0]["annotator"] = ""
    with open(tmp_path / "pairs_annotator1.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=at.COLS)
        w.writeheader()
        w.writerows(rows)
    with pytest.raises(SystemExit, match="without annotator"):
        at.cmd_validate(tmp_path, key)


def test_agreement_refuses_incomplete_and_builds_adjudication(tmp_path):
    key = _pkg(tmp_path, [G, E, T, E, G, ""], [G] * 6)
    with pytest.raises(SystemExit, match="incomplete"):
        at.cmd_agreement(tmp_path, key, tmp_path / "out")
    key = _pkg(tmp_path, [G, E, T, E, G, U], [G, T, T, G, G, U])
    rep = at.cmd_agreement(tmp_path, key, tmp_path / "out")
    assert rep["primary"]["raw_agreement_3"] == pytest.approx(5 / 6)   # only p3 differs at 3-class level
    adj = list(csv.DictReader(open(tmp_path / "out" / "adjudication_package.csv")))
    assert {r["pair_id"]: r["reason"][:7] for r in adj} == {"p1": "subtype", "p3": "3-class"}
    # finalize refuses until the 3-class disagreement is adjudicated by a named person
    with pytest.raises(SystemExit, match="without an adjudicated"):
        at.cmd_finalize(tmp_path, key, "-", tmp_path / "out")
    for r in adj:
        if r["pair_id"] == "p3":
            r["adjudicated_label"], r["adjudicator"] = E, "adj"
    with open(tmp_path / "adj.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(adj[0]))
        w.writeheader()
        w.writerows(adj)
    fp = at.cmd_finalize(tmp_path, key, str(tmp_path / "adj.csv"), tmp_path / "out")
    final = {r["pair_id"]: r for r in csv.DictReader(open(fp))}
    assert final["p3"]["label3"] == "false" and final["p3"]["source"] == "adjudicated"
    assert final["p1"]["label3"] == "false" and final["p1"]["label7"] == ""      # subtype unresolved, class agreed
    assert final["p5"]["label3"] == "ambiguous"
    # design-weighted precision with known inclusion probabilities
    with open(tmp_path / "pop.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pair_id", "strata", "pi_hat", "package_stratum"])
        w.writeheader()
        for i in range(6):
            w.writerow({"pair_id": f"p{i}", "strata": "s", "pi_hat": 0.5 if i == 0 else 0.25, "package_stratum": "s"})
        w.writerow({"pair_id": "unsampled", "strata": "", "pi_hat": 0, "package_stratum": ""})
    rep = at.cmd_precision(fp, tmp_path / "out", tmp_path / "pop.csv")
    g = [r for r in final.values() if r["label3"] == "genuine"]               # p0 (pi .5), p4 (pi .25)
    assert {r["pair_id"] for r in g} == {"p0", "p4"}
    assert rep["design_weighted"]["precision_strict"] == pytest.approx((2 + 4) / (2 + 5 * 4))
    assert rep["sample"]["precision_strict"] == pytest.approx(2 / 6)
    assert rep["sample"]["bounds"] == pytest.approx([2 / 6, 3 / 6])
    assert rep["design_weighted"]["excluded_pairs_without_stratum"] == 1


# ------------------------------------------------------------------ Experiment B

def _records(toy_question, labels_fn):
    """Records for A-D rendered by the real pipeline code (no model)."""
    from wsh.data.schemas import AnnotationStatus, Edge, RelationType
    from wsh.experiments.common import make_layout
    from wsh.models.prompts import build_request
    from wsh.representations.evidence import gold_bundle
    from wsh.representations.relation_controls import contradiction_pair_id, control_bundle
    from wsh.representations.serialization import render
    derived = gold_bundle(toy_question)
    pred = derived.model_copy(deep=True)
    c = [x.claim_id for x in pred.claims]
    mk = lambda s, t, r: Edge(source=s, target=t, relation=r, confidence=0.9, status=AnnotationStatus.MODEL_PREDICTED, method="t")  # noqa: E731
    pred.edges = [mk(c[1], c[2], RelationType.CONTRADICTS), mk(c[2], c[1], RelationType.CONTRADICTS),
                  mk(c[0], c[3], RelationType.CONTRADICTS), mk(c[0], c[1], RelationType.SUPPORTS)]
    q = toy_question.uid
    labels = labels_fn(contradiction_pair_id(q, c[1], c[2]), contradiction_pair_id(q, c[0], c[3]))
    rec = {}
    for k, rep in xb.COND.items():
        b = control_bundle(rep, derived, pred, labels if rep in ("R4P_FO_SC", "R4P_FO_SN") else None) \
            if rep in ("R4P_FO_SC", "R4P_FO_SN") else control_bundle(rep, derived, pred)
        ser = render(make_layout(rep, b))
        rec[k] = {"question_uid": q, "question": toy_question.question, "prompt": {"user": build_request(toy_question, ser.text, 64).user},
                  "evidence": {"text": ser.text, "id_map": ser.id_map,
                               "edges": [{"source": e.source, "target": e.target, "relation": e.relation.value} for e in b.edges]},
                  "generation": {"input_tokens": 1}}
    return rec, labels


def test_expb_checks_accept_pipeline_records_and_reject_tampering(toy_question):
    rec, labels = _records(toy_question, lambda x, y: {x: "false", y: "genuine"})
    v = xb.check_question(rec, labels)
    assert v["composition"] == "mixed_genuine_false" and v["n_false_lines"] == 2 and v["n_contra_lines"] == 3
    rec["B"]["evidence"]["text"] = rec["A"]["evidence"]["text"]          # B not cleaned -> refused
    with pytest.raises(SystemExit, match="intended intervention"):
        xb.check_question(rec, labels)
    rec, labels = _records(toy_question, lambda x, y: {x: "false", y: "genuine"})
    rec["C"]["evidence"]["text"] = rec["C"]["evidence"]["text"].replace("[E1]", "[E1] extra", 1)
    with pytest.raises(SystemExit, match="facts or order"):
        xb.check_question(rec, labels)
    rec, labels = _records(toy_question, lambda x, y: {x: "false", y: "genuine"})
    partial = dict(list(labels.items())[:1])                             # the analysis sees one pair unlabelled
    with pytest.raises(SystemExit, match="no human label"):
        xb.check_question(rec, partial)


def test_expb_edge_compositions(toy_question):
    rec, labels = _records(toy_question, lambda x, y: {x: "genuine", y: "genuine"})
    assert xb.check_question(rec, labels)["composition"] == "all_genuine"
    assert rec["B"]["prompt"]["user"] == rec["A"]["prompt"]["user"]
    rec, labels = _records(toy_question, lambda x, y: {x: "false", y: "false"})
    assert xb.check_question(rec, labels)["composition"] == "all_false"
    assert rec["B"]["prompt"]["user"] == rec["C"]["prompt"]["user"]


def test_selection_reads_no_outcome_fields_and_labels_refuse_incomplete(tmp_path):
    assert not ({"eval", "generation", "parsed", "failure", "gold_answers"} & sel.EVIDENCE_ONLY)
    key = {"a": {"question_uid": "ds/q1"}, "b": {"question_uid": "ds/q1"}, "c": {"question_uid": "ds/q2"}}
    (tmp_path / "key.json").write_text(json.dumps(key))
    (tmp_path / "tier.json").write_text(json.dumps({"question_uids": {"ds": ["ds/q1", "ds/q2"]}}))
    with open(tmp_path / "final.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pair_id", "label3"])
        w.writeheader()
        w.writerows([{"pair_id": "a", "label3": "false"}, {"pair_id": "c", "label3": "genuine"}])
    with pytest.raises(SystemExit, match="unlabelled"):
        sel.cmd_labels(tmp_path / "final.csv", tmp_path / "key.json", tmp_path / "tier.json", tmp_path / "out.json")
    with open(tmp_path / "final.csv", "a", newline="") as f:
        f.write("b,genuine\n")
    sel.cmd_labels(tmp_path / "final.csv", tmp_path / "key.json", tmp_path / "tier.json", tmp_path / "out.json")
    d = json.loads((tmp_path / "out.json").read_text())
    assert d["label_source"] == "human_adjudicated" and d["composition"] == {"mixed_genuine_false": 1, "all_genuine": 1}


def test_passage_reconstruction_from_rendered_evidence():
    r = {"evidence": {"text": "[E1] (source: T1) S two.\n[E2] (source: T1) S one.\n[E3] (source: T2) X.\nRelations:\nE1 CONTRADICTS E3",
                      "id_map": {"E1": {"claim_ids": ["p1#1"]}, "E2": {"claim_ids": ["p1#0"]}, "E3": {"claim_ids": ["p2#0"]}}}}
    facts, passages = sel._facts_and_passages(r)
    assert facts["p1#1"] == ("T1", "S two.") and passages == {"p1": "S one. S two.", "p2": "X."}
    # real claim ids carry an 's' prefix and must sort numerically, not alphabetically
    r = {"evidence": {"text": "[E1] (source: T) Zeta first.\n[E2] (source: T) Alpha second.\n[E3] (source: T) Mid tenth.",
                      "id_map": {"E1": {"claim_ids": ["d/q/p00#s00"]}, "E2": {"claim_ids": ["d/q/p00#s01"]},
                                 "E3": {"claim_ids": ["d/q/p00#s10"]}}}}
    assert sel._facts_and_passages(r)[1] == {"d/q/p00": "Zeta first. Alpha second. Mid tenth."}
