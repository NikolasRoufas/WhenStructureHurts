"""Confirmatory protocol 2 (docs/CONFIRMATORY_PROTOCOL_2.md): predicted CONTRADICTS lines on vs off.

Written and committed before any generation on confirm2_v1. Reads only the run's predictions.jsonl.

    PYTHONPATH=src python scripts/revision/confirm2_analysis.py <run_dir> <out_dir>

Primary (Holm over the two datasets): EM difference R4P_FO - R4P_FO_NC in the primary population
(questions whose R4P_FO block renders >= 1 CONTRADICTS line). Secondary: abstention difference (same
population, Holm separately); EM difference over all questions. Descriptive: C/W/A transitions,
accuracy among questions answered under both, strata by number of contradiction lines.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from wsh.evaluation.statistics import paired_bootstrap, holm

A, B = "R4P_FO_NC", "R4P_FO"  # difference reported as B - A (lines on minus lines off)


def n_contra(text: str) -> int:
    return sum(1 for ln in text.splitlines() if " CONTRADICTS " in f" {ln} ")


def state(r: dict) -> str:
    if r["generation"].get("error") or not r["failure"]["answered"]:
        return "A"
    return "C" if (r["eval"].get("em") or 0) == 1 else "W"


def load(run_dir: Path) -> dict:
    recs = {}
    with open(run_dir / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            recs[r["record_key"]] = r  # last write wins if a resumed run rewrote a record
    by_q: dict = defaultdict(dict)
    for r in recs.values():
        c = r["condition"]
        if c["protocol"] == "A" and c["representation"] in (A, B):
            by_q[(r["dataset"], r["question_uid"])][c["representation"]] = r
    return by_q


def main(run_dir: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    by_q = load(run_dir)
    rows, prim_p, abst_p = [], {}, {}
    summary: dict = {"run_dir": str(run_dir), "protocol": "docs/CONFIRMATORY_PROTOCOL_2.md", "datasets": {}}
    for ds in sorted({d for d, _ in by_q}):
        qs = {q: v for (d, q), v in by_q.items() if d == ds}
        complete = {q: v for q, v in qs.items() if A in v and B in v}
        k = {q: n_contra(v[B]["evidence"]["text"]) for q, v in complete.items()}
        identical = sum(v[A]["prompt"]["user"] == v[B]["prompt"]["user"] for v in complete.values())
        assert all((k[q] == 0) == (v[A]["prompt"]["user"] == v[B]["prompt"]["user"]) for q, v in complete.items()), \
            "prompts must be identical exactly when no contradiction line is rendered"
        n_err = sum(bool(r["generation"].get("error")) for v in complete.values() for r in v.values())
        em = {c: {q: float(state(v[c]) == "C") for q, v in complete.items()} for c in (A, B)}
        ab = {c: {q: float(state(v[c]) == "A") for q, v in complete.items()} for c in (A, B)}
        prim = [q for q in complete if k[q] >= 1]
        sub = lambda m, keep: {q: x for q, x in m.items() if q in keep}  # noqa: E731
        pk = set(prim)
        res = {
            "primary_em": paired_bootstrap(sub(em[A], pk), sub(em[B], pk)),
            "secondary_abstention": paired_bootstrap(sub(ab[A], pk), sub(ab[B], pk)),
            "secondary_em_all_questions": paired_bootstrap(em[A], em[B]),
        }
        for lo, hi, lab in ((1, 2, "1-2"), (3, 5, "3-5"), (6, 10**9, "6+")):
            s = {q for q in prim if lo <= k[q] <= hi}
            res[f"stratum_em_{lab}"] = paired_bootstrap(sub(em[A], s), sub(em[B], s))
        trans = defaultdict(int)
        for q in prim:
            trans[f"{state(complete[q][A])}->{state(complete[q][B])}"] += 1
        both = [q for q in prim if state(complete[q][A]) != "A" and state(complete[q][B]) != "A"]
        res["acc_given_both_answered"] = paired_bootstrap(sub(em[A], set(both)), sub(em[B], set(both)))
        prim_p[ds], abst_p[ds] = res["primary_em"]["p_boot"], res["secondary_abstention"]["p_boot"]
        summary["datasets"][ds] = {
            "n_questions": len(qs), "n_complete_pairs": len(complete), "n_primary_population": len(prim),
            "n_identical_prompts": identical, "n_generation_errors": n_err,
            "mean_contradiction_lines_primary": sum(k[q] for q in prim) / max(1, len(prim)),
            "transitions_primary (off->on)": dict(trans), **res,
        }
    for ds, p in holm(prim_p).items():
        d = summary["datasets"][ds]
        d["primary_em"]["p_holm"] = p
        est = d["primary_em"]["delta"]
        d["decision"] = ("confirmed (EM lower with contradiction lines)" if p is not None and p < 0.05 and est < 0
                         else "significant, opposite direction" if p is not None and p < 0.05
                         else "inconclusive")
    for ds, p in holm(abst_p).items():
        summary["datasets"][ds]["secondary_abstention"]["p_holm"] = p
    (out / "confirm2_summary.json").write_text(json.dumps(summary, indent=1))
    for ds, d in summary["datasets"].items():
        for key in [k for k in d if isinstance(d[k], dict) and "delta" in d[k]]:
            r = d[key]
            rows.append({"dataset": ds, "analysis": key, "n": r["n_paired"], "delta": r["delta"], "ci": json.dumps(r["ci"]),
                         "p_boot": r["p_boot"], "p_holm": r.get("p_holm", ""),
                         "decision": d["decision"] if key == "primary_em" else ""})
    with open(out / "confirm2_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({ds: {"n_primary": d["n_primary_population"], "delta": d["primary_em"]["delta"],
                           "ci": d["primary_em"]["ci"], "p_holm": d["primary_em"]["p_holm"], "decision": d["decision"]}
                      for ds, d in summary["datasets"].items()}, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
