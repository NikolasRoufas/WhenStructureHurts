"""Revision-1 analysis code: paired statistics, transitions, missing results, human-label import validation."""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


audit = _load("scripts/audit/verify_claims.py", "verify_claims")
trans = _load("scripts/revision/transitions.py", "transitions")
contra = _load("scripts/revision/contradictions.py", "contradictions")


def test_independent_bootstrap_matches_frozen_procedure():
    from wsh.evaluation.statistics import paired_bootstrap
    a = {f"q{i}": float(i % 3 == 0) for i in range(300)}
    b = {f"q{i}": float(i % 4 == 0) for i in range(300)}
    ref = paired_bootstrap(a, b)
    mine = audit.frozen_bootstrap(a, b)
    assert mine["delta"] == pytest.approx(ref["delta"])
    assert mine["ci"] == pytest.approx(ref["ci"])
    assert mine["p"] == pytest.approx(ref["p_boot"])


def test_holm_and_mcnemar():
    assert audit.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert audit.mcnemar(0, 0) is None
    assert audit.mcnemar(5, 5) == pytest.approx(1.0)
    assert audit.mcnemar(0, 6) == pytest.approx(2 / 64)


def _rec(q, rep, em, answered, unavailable=False):
    r = {"record_key": f"{q}|{rep}", "dataset": "toy", "question_uid": q, "task": "qa",
         "condition": {"protocol": "A", "representation": rep}}
    if unavailable:
        r["unavailable"] = "X: missing"
    else:
        r["eval"] = {"em": em}
        r["failure"] = {"answered": answered}
    return r


def test_transitions_states_counts_and_missing_records(tmp_path):
    recs = [_rec("q1", "R0", 1, True), _rec("q1", "R1", 0, False),   # C -> A
            _rec("q2", "R0", 0, True), _rec("q2", "R1", 1, True),    # W -> C
            _rec("q3", "R0", 0, False), _rec("q3", "R1", 0, True),   # A -> W
            _rec("q4", "R0", 1, True), _rec("q4", "R1", 0, True, unavailable=True)]  # unpaired: excluded
    (tmp_path / "predictions.jsonl").write_text("\n".join(json.dumps(r) for r in recs))
    st = trans.load_states(tmp_path)
    row = trans.analyse(st, "R0", "R1", "toy")
    assert row["n"] == 3
    assert (row["C->A"], row["W->C"], row["A->W"]) == (1, 1, 1)
    assert sum(row[f"{x}->{y}"] for x in "CWA" for y in "CWA") == 3
    assert row["d_em"] == pytest.approx(0.0) and row["d_abst"] == pytest.approx(0.0)


def test_human_package_import_refuses_invalid_labels(tmp_path):
    with open(tmp_path / "pairs_to_label.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "pair_id", "fact_A_source_title", "fact_A", "fact_B_source_title", "fact_B", "label", "notes", "annotator"])
        w.writerow([1, "p1", "A", "x", "B", "y", "probably_fine", "", "NR"])
    with pytest.raises(SystemExit):
        contra.import_pkg(tmp_path)
    with open(tmp_path / "pairs_to_label.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "pair_id", "fact_A_source_title", "fact_A", "fact_B_source_title", "fact_B", "label", "notes", "annotator"])
        w.writerow([1, "p1", "A", "x", "B", "y", "compatible_different_entities", "", ""])  # no annotator
    with pytest.raises(SystemExit):
        contra.import_pkg(tmp_path)


def test_auto_category_is_heuristic_triage_only():
    a = {"title": "Film A", "text": "Film A was released in 2001."}
    b = {"title": "Film B", "text": "Film B was released in 2003."}
    assert contra.auto_category(a, b) == "auto:different_source_titles"
    c = {"title": "Film A", "text": "The teaser was released in 2016."}
    d = {"title": "Film A", "text": "The trailer was released in 2017."}
    assert contra.auto_category(c, d) == "auto:same_title_different_years"
