"""Revision-1 (EXPLORATORY, post hoc): question-level outcome transitions between two representations.

Each (question, representation) record is one of three states:
    C = answered and correct (EM = 1)
    W = answered and wrong   (EM = 0, a parsed non-abstaining answer)
    A = not answered         (abstained, or no parseable answer)
For a pair (a, b) we count the 3x3 transition matrix a-state -> b-state over questions, and report with
95% question-level bootstrap CIs (2000 resamples, seed 0):
    dEM = P(b=C) - P(a=C); dAbst = P(b=A) - P(a=A); dWrong = P(b=W) - P(a=W);
    accuracy given answered under BOTH (paired over the questions answered by both).
Shuffled R2 (several seeds) is not used here; all compared representations are single records per question.

    PYTHONPATH=src python scripts/revision/transitions.py <run_dir> <out.csv> [pairs like R0:R1,R4:R4P ...]
"""
from __future__ import annotations

import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

STATES = ("C", "W", "A")


def load_states(run_dir: Path, protocol: str = "A") -> dict:
    out = defaultdict(dict)  # (dataset, qid) -> rep -> state
    recs = {}
    with open(run_dir / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            recs[r["record_key"]] = r
    for r in recs.values():
        c = r["condition"]
        if r.get("unavailable") or c.get("protocol") != protocol or r["task"] != "qa":
            continue
        if c.get("representation") == "R2":
            continue
        if not r["failure"]["answered"]:
            s = "A"
        else:
            s = "C" if (r["eval"].get("em") or 0) == 1 else "W"
        out[(r["dataset"], r["question_uid"])][c["representation"]] = s
    return out


def boot_ci(stat, items, n_boot=2000, seed=0):
    rng = random.Random(seed)
    n = len(items)
    vals = sorted(stat([items[rng.randrange(n)] for _ in range(n)]) for _ in range(n_boot))
    return [vals[int(0.025 * n_boot)], vals[min(n_boot - 1, int(0.975 * n_boot) - 1)]]


def analyse(states: dict, a: str, b: str, ds: str) -> dict:
    pairs = [(v[a], v[b]) for (d, _), v in states.items() if d == ds and a in v and b in v]
    n = len(pairs)
    if not n:
        return {}
    mat = {f"{x}->{y}": sum(1 for p in pairs if p == (x, y)) for x in STATES for y in STATES}
    p = lambda ps, s, i: sum(1 for q in ps if q[i] == s) / len(ps)  # noqa: E731
    d_em = lambda ps: p(ps, "C", 1) - p(ps, "C", 0)  # noqa: E731
    d_ab = lambda ps: p(ps, "A", 1) - p(ps, "A", 0)  # noqa: E731
    d_wr = lambda ps: p(ps, "W", 1) - p(ps, "W", 0)  # noqa: E731
    both = [q for q in pairs if q[0] != "A" and q[1] != "A"]
    acc_both = lambda ps: (sum(q[1] == "C" for q in ps) - sum(q[0] == "C" for q in ps)) / len(ps) if ps else 0  # noqa: E731
    row = {"dataset": ds, "a": a, "b": b, "n": n, **mat,
           "em_a": p(pairs, "C", 0), "em_b": p(pairs, "C", 1), "abst_a": p(pairs, "A", 0), "abst_b": p(pairs, "A", 1),
           "wrong_a": p(pairs, "W", 0), "wrong_b": p(pairs, "W", 1),
           "d_em": d_em(pairs), "d_em_ci": boot_ci(d_em, pairs), "d_abst": d_ab(pairs), "d_abst_ci": boot_ci(d_ab, pairs),
           "d_wrong": d_wr(pairs), "d_wrong_ci": boot_ci(d_wr, pairs),
           "n_both_answered": len(both), "acc_given_both_answered_a": (sum(q[0] == "C" for q in both) / len(both)) if both else None,
           "acc_given_both_answered_b": (sum(q[1] == "C" for q in both) / len(both)) if both else None,
           "d_acc_given_both_answered": acc_both(both), "d_acc_given_both_answered_ci": boot_ci(acc_both, both) if both else None,
           "C_to_A": mat["C->A"], "A_to_C": mat["A->C"], "C_to_W": mat["C->W"], "W_to_C": mat["W->C"],
           "W_to_A": mat["W->A"], "A_to_W": mat["A->W"]}
    return row


def main():
    run_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
    pairs = [tuple(x.split(":")) for x in (sys.argv[3:] or ["R0:R1", "R1:R5", "R5:R4", "R4:R4P"])]
    st = load_states(run_dir)
    rows = []
    for ds in sorted({d for d, _ in st}):
        for a, b in pairs:
            r = analyse(st, a, b, ds)
            if r:
                rows.append(r)
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in r.items()})
    for r in rows:
        print(f"{r['dataset'][:6]} {r['b']}-{r['a']} n={r['n']} dEM={r['d_em']:+.3f} {[round(x,3) for x in r['d_em_ci']]} "
              f"dAbst={r['d_abst']:+.3f} {[round(x,3) for x in r['d_abst_ci']]} dWrong={r['d_wrong']:+.3f} "
              f"accBoth {r['acc_given_both_answered_a']:.3f}->{r['acc_given_both_answered_b']:.3f} "
              f"({r['d_acc_given_both_answered']:+.3f} {[round(x,3) for x in r['d_acc_given_both_answered_ci']]}, n={r['n_both_answered']}) "
              f"C->A {r['C_to_A']} A->C {r['A_to_C']} C->W {r['C_to_W']} W->C {r['W_to_C']} W->A {r['W_to_A']} A->W {r['A_to_W']}")


if __name__ == "__main__":
    main()
