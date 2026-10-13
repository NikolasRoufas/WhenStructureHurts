"""Revision-2 (EXPLORATORY; existing records only): serialisation fairness and annotation-quality strata.

    PYTHONPATH=src python scripts/revision/serialization_audit.py <out_dir> <run_dir> [<run_dir> ...]

For every (dataset, representation) under Protocol A it reports: input tokens, evidence tokens, content and
overhead tokens, facts, rendered relation lines (by label), source-title mentions, answer-in-evidence, and the
number of questions whose evidence text is byte-identical to R1's. It then stratifies the derived-relation
contrast R4 - R5 (and R5 - R1) by the question's edge stratum (exact-anchor vs fallback-anchor derived edges).
Records from several runs are merged by (dataset, question, representation, prompt version); a representation
present in two runs must have identical prompts (checked).
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from wsh.evaluation.statistics import paired_bootstrap

LABEL = re.compile(r"^E\d+ ([A-Z_]+) E\d+$")


def main(out: Path, runs: list[Path]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    recs: dict = {}
    for run in runs:
        with open(run / "predictions.jsonl") as f:
            for line in f:
                r = json.loads(line)
                c = r["condition"]
                if c["protocol"] != "A" or r["task"] != "qa" or r.get("unavailable") or c["representation"] == "R2":
                    continue
                if r.get("prompt_version", "qa-v2") != "qa-v2":
                    continue
                k = (r["dataset"], r["question_uid"], c["representation"])
                if k in recs:
                    assert recs[k]["prompt"]["user"] == r["prompt"]["user"], f"prompt mismatch across runs for {k}"
                    continue
                recs[k] = r
    by = defaultdict(dict)
    for (ds, q, rep), r in recs.items():
        by[(ds, q)][rep] = r

    rows = []
    reps = sorted({k[2] for k in recs})
    for ds in sorted({k[0] for k in recs}):
        for rep in reps:
            rs = [v[rep] for (d, _), v in by.items() if d == ds and rep in v]
            if not rs:
                continue
            labels = defaultdict(int)
            n_ident_r1 = 0
            for (d, _), v in by.items():
                if d == ds and rep in v and "R1" in v and v[rep]["evidence"]["text"] == v["R1"]["evidence"]["text"]:
                    n_ident_r1 += 1
            src = 0
            for r in rs:
                for ln in r["evidence"]["text"].splitlines():
                    m = LABEL.match(ln.strip())
                    if m:
                        labels[m.group(1)] += 1
                    elif ln.strip().startswith("(this line is intentionally"):
                        labels["FILLER"] += 1
                src += r["evidence"]["text"].count("(source: ")
            info = [r["info"]["information"] for r in rs]
            n = len(rs)
            mean = lambda xs: sum(xs) / max(1, len(xs))  # noqa: E731
            rows.append({
                "dataset": ds, "representation": rep, "n_questions": n,
                "input_tokens": round(mean([r["generation"]["input_tokens"] for r in rs]), 1),
                "evidence_tokens": round(mean([i["evidence_tokens"] for i in info]), 1),
                "content_tokens": round(mean([i["content_tokens"] for i in info]), 1),
                "overhead_tokens": round(mean([i["overhead_tokens"] for i in info]), 1),
                "facts": round(mean([i["n_facts"] for i in info]), 2),
                "units_shown": round(mean([r["evidence"]["n_units"] for r in rs]), 2),
                "relation_lines": round(mean([r["evidence"]["n_relations"] for r in rs]), 2),
                "lines_by_label": json.dumps({k: round(v / n, 2) for k, v in sorted(labels.items())}),
                "source_mentions": round(src / n, 2),
                "answer_in_evidence": round(mean([r["eval"].get("answer_in_evidence") or 0 for r in rs]), 3),
                "identical_to_R1": n_ident_r1,
                "em": round(mean([r["eval"].get("em") or 0 for r in rs]), 4),
                "f1": round(mean([r["eval"].get("f1") or 0 for r in rs]), 4),
                "abstained": round(mean([0 if r["failure"]["answered"] else 1 for r in rs]), 4),
            })
    with open(out / "serialization_accounting.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    srows = []
    for ds in sorted({k[0] for k in recs}):
        strata = defaultdict(list)
        for (d, q), v in by.items():
            if d == ds and "R4" in v:
                strata[v["R4"]["info"].get("question_edge_stratum") or "unknown"].append(q)
        for st, qs in sorted(strata.items()):
            keep = set(qs)
            for a, b in (("R5", "R4"), ("R1", "R5")):
                em = {rep: {q: float(by[(ds, q)][rep]["eval"].get("em") or 0) for q in keep if rep in by[(ds, q)]}
                      for rep in (a, b)}
                ab = {rep: {q: float(not by[(ds, q)][rep]["failure"]["answered"]) for q in keep if rep in by[(ds, q)]}
                      for rep in (a, b)}
                res, resa = paired_bootstrap(em[a], em[b]), paired_bootstrap(ab[a], ab[b])
                ident = sum(by[(ds, q)][a]["evidence"]["text"] == by[(ds, q)][b]["evidence"]["text"]
                            for q in keep if a in by[(ds, q)] and b in by[(ds, q)])
                srows.append({"dataset": ds, "edge_stratum": st, "contrast": f"{b}-{a}", "n": res["n_paired"],
                              "n_identical": ident, "d_em": res["delta"], "d_em_ci": json.dumps(res["ci"]),
                              "d_abst": resa["delta"], "d_abst_ci": json.dumps(resa["ci"])})
    with open(out / "anchor_strata.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(srows[0]))
        w.writeheader()
        w.writerows(srows)
    print(f"{len(rows)} accounting rows, {len(srows)} stratum rows -> {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]])
