"""Experiment B analysis (protocol §B): selective removal of human-verified false contradictions.

Conditions: A = R4P_FO, B = R4P_FO_SC, C = R4P_FO_NC, D = R4P_FO_SN. Differences are later - earlier, e.g.
"B-A" = EM(B) - EM(A). Primary family (Holm, 3 tests): B-A, C-A, C-B pooled over datasets with resampling of
questions within dataset. Written before any label or Experiment-B generation exists.

Every control assumption is re-checked from the records and the run is refused if one fails:
identical question, facts and order (everything before 'Relations:'), only target relation lines differ, B == A
when no line is false, B == C when all lines are false, every analysed question fully labelled.

    PYTHONPATH=src python experiments/andreas_revision/selective_removal/analysis.py <run_dir> <labels.json> <qwen_confirm2_run> <out_dir>
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arlib import holm, load_records, paired_bootstrap_strat, sha256, state, transitions  # noqa: E402
from wsh.representations.relation_controls import contradiction_pair_id  # noqa: E402

COND = {"A": "R4P_FO", "B": "R4P_FO_SC", "C": "R4P_FO_NC", "D": "R4P_FO_SN"}
PRIMARY = [("A", "B"), ("A", "C"), ("B", "C")]
SECONDARY = [("A", "D"), ("B", "D")]


def _rel_lines(text: str) -> list[str]:
    return text.split("Relations:\n", 1)[1].split("\n") if "Relations:\n" in text else []


def check_question(rec: dict, labels: dict[str, str]) -> dict:
    """Re-derive the expected B, C, D relation blocks from A's rendered lines and the human labels."""
    a = rec["A"]
    q = a["question_uid"]
    for c, r in rec.items():
        if r.get("pipeline_error"):
            raise SystemExit(f"{q} {c}: pipeline error {r['pipeline_error']}")
        if r["question"] != a["question"]:
            raise SystemExit(f"{q}: question text differs in {c}")
        if r["evidence"]["text"].split("Relations:")[0] != a["evidence"]["text"].split("Relations:")[0]:
            raise SystemExit(f"{q}: facts or order differ in {c}")
        if r["evidence"]["id_map"] != a["evidence"]["id_map"]:
            raise SystemExit(f"{q}: id map differs in {c}")
    eid = {cl: e for e, m in a["evidence"]["id_map"].items() for cl in m["claim_ids"]}
    false_lines, all_contra = set(), set()
    for e in a["evidence"]["edges"]:
        if e["relation"] != "CONTRADICTS":
            continue
        ln = f"{eid[e['source']]} CONTRADICTS {eid[e['target']]}"
        all_contra.add(ln)
        pid = contradiction_pair_id(q, e["source"], e["target"])
        if pid not in labels:
            raise SystemExit(f"{q}: pair {pid} has no human label")
        if labels[pid] == "false":
            false_lines.add(ln)
    la = _rel_lines(a["evidence"]["text"])
    if set(la) & all_contra != all_contra:
        raise SystemExit(f"{q}: a predicted CONTRADICTS line is not rendered in A (relation cap?)")
    exp = {"B": [x for x in la if x not in false_lines], "C": [x for x in la if x not in all_contra],
           "D": [x.replace(" CONTRADICTS ", " RELATED_TO ") if x in false_lines else x for x in la]}
    for c, want in exp.items():
        if _rel_lines(rec[c]["evidence"]["text"]) != want:
            raise SystemExit(f"{q}: condition {c} relation lines are not the intended intervention")
    vals = [labels[p] for p in {contradiction_pair_id(q, e["source"], e["target"])
                                for e in a["evidence"]["edges"] if e["relation"] == "CONTRADICTS"}]
    if not any(v == "false" for v in vals):
        assert rec["B"]["prompt"]["user"] == a["prompt"]["user"]
    if all(v == "false" for v in vals):
        assert rec["B"]["prompt"]["user"] == rec["C"]["prompt"]["user"]
    s = set(vals)
    comp = ("all_false" if s == {"false"} else "all_genuine" if s == {"genuine"} else
            "any_ambiguous" if "ambiguous" in s else "mixed_genuine_false")
    return {"n_genuine": vals.count("genuine"), "n_false": vals.count("false"), "n_ambiguous": vals.count("ambiguous"),
            "n_contra_lines": len(all_contra), "n_false_lines": len(false_lines), "composition": comp,
            "tokens": {c: rec[c]["generation"]["input_tokens"] for c in COND}}


def contrast(recs: dict, qs: list, x: str, y: str, metric: str) -> dict:
    f = {"em": lambda r: float(state(r) == "C"), "abstention": lambda r: float(state(r) == "A"),
         "wrong": lambda r: float(state(r) == "W"), "coverage": lambda r: float(state(r) != "A")}[metric]
    strata = {q: q[0] for q in qs}
    return paired_bootstrap_strat({q: f(recs[q][x]) for q in qs}, {q: f(recs[q][y]) for q in qs}, strata)


def main(run: Path, labels_p: Path, qwen_run: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    lab = json.loads(labels_p.read_text())
    if lab.get("label_source") != "human_adjudicated":
        raise SystemExit("labels must be human_adjudicated")
    by = load_records(run, set(COND.values()))
    recs = {k: {c: v[rep] for c, rep in COND.items()} for k, v in by.items() if set(v) == set(COND.values())}
    missing = sorted(set(lab["questions"]) - {k[1] for k in recs})
    if missing:
        raise SystemExit(f"{len(missing)} labelled questions lack a complete set of conditions (e.g. {missing[:3]})")
    per_q = {k: check_question(recs[k], lab["questions"][k[1]]) for k in sorted(recs)}
    qs = sorted(per_q)
    # reproducibility of A and C against the original Qwen confirm2 outputs
    orig = load_records(qwen_run, {"R4P_FO", "R4P_FO_NC"})
    repro = {c: {"same_prompt": sum(recs[k][c]["prompt"]["user"] == orig[k][COND[c]]["prompt"]["user"] for k in qs),
                 "same_output": sum(recs[k][c]["generation"]["text"] == orig[k][COND[c]]["generation"]["text"] for k in qs),
                 "same_state": sum(state(recs[k][c]) == state(orig[k][COND[c]]) for k in qs)} for c in ("A", "C")}
    rep: dict = {"run": str(run), "predictions_sha256": sha256(run / "predictions.jsonl"), "labels": str(labels_p),
                 "labels_sha256": sha256(labels_p), "n_questions": len(qs),
                 "by_dataset": {ds: sum(k[0] == ds for k in qs) for ds in sorted({k[0] for k in qs})},
                 "reproducibility_vs_original_confirm2 (n questions)": repro,
                 "label_composition": {c: sum(v["composition"] == c for v in per_q.values())
                                       for c in ("all_false", "all_genuine", "mixed_genuine_false", "any_ambiguous")},
                 "mean_tokens": {c: sum(v["tokens"][c] for v in per_q.values()) / len(qs) for c in COND},
                 "rates": {c: {m: sum((state(recs[k][c]) == s) for k in qs) / len(qs) for m, s in
                               (("em", "C"), ("wrong", "W"), ("abstention", "A"))} for c in COND},
                 "primary": {}, "secondary": {}, "per_dataset": {}, "by_composition": {}, "transitions": {}}
    for c in COND:
        rep["rates"][c]["coverage"] = 1 - rep["rates"][c]["abstention"]
    for x, y in PRIMARY:
        rep["primary"][f"{y}-{x}"] = contrast(recs, qs, x, y, "em")
    for name, p in holm({k: v["p_boot"] for k, v in rep["primary"].items()}).items():
        rep["primary"][name]["p_holm"] = p
    for x, y in PRIMARY + SECONDARY:
        for m in ("em", "abstention", "wrong", "coverage"):
            if (x, y) in PRIMARY and m == "em":
                continue
            rep["secondary"][f"{y}-{x}:{m}"] = contrast(recs, qs, x, y, m)
        rep["transitions"][f"{x}->{y}"] = transitions({k: state(recs[k][x]) for k in qs}, {k: state(recs[k][y]) for k in qs})
    for ds in rep["by_dataset"]:
        sub = [k for k in qs if k[0] == ds]
        rep["per_dataset"][ds] = {f"{y}-{x}": contrast(recs, sub, x, y, "em") for x, y in PRIMARY + SECONDARY}
    for comp in rep["label_composition"]:
        sub = [k for k in qs if per_q[k]["composition"] == comp]
        if sub:
            rep["by_composition"][comp] = {"n": len(sub), **{f"{y}-{x}": contrast(recs, sub, x, y, "em") for x, y in PRIMARY},
                                           "note": "observational: label composition is not randomised"}
    ca, ba = rep["primary"]["C-A"], rep["primary"]["B-A"]
    if ca["ci"] and not (ca["ci"][0] <= 0 <= ca["ci"][1]) and ca["delta"]:
        rep["share_of_C_minus_A_recovered_by_B"] = ba["delta"] / ca["delta"]
    with open(out / "expB_per_question.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "question_uid", "composition", "n_genuine", "n_false", "n_ambiguous", *[f"state_{c}" for c in COND],
                    *[f"tokens_{c}" for c in COND]])
        for k in qs:
            v = per_q[k]
            w.writerow([k[0], k[1], v["composition"], v["n_genuine"], v["n_false"], v["n_ambiguous"],
                        *[state(recs[k][c]) for c in COND], *[v["tokens"][c] for c in COND]])
    (out / "expB_summary.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: {m: v[m] for m in ("n", "delta", "ci", "p_holm")} for k, v in rep["primary"].items()}, indent=1))


if __name__ == "__main__":
    main(*map(Path, sys.argv[1:5]))
