"""Revision-1 (EXPLORATORY): prompt factor qa-v2 vs qa-v2-noabst on the same 1,000 2Wiki questions.

qa-v2 records come from the confirmatory run (same questions, same evidence, same generator); noabst
records from the revision run. Reports, per prompt, R1-R0 and R4P-R4 (EM and abstention), the prompt
effect per representation, and the prompt x representation interaction (difference of paired differences),
all with question-level paired bootstrap CIs.
    PYTHONPATH=src python scripts/revision/noabst_analysis.py <F_exp1_dir> <noabst_dir> <out_dir>
"""
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path


def load(d, prompt):
    out = defaultdict(dict)
    recs = {}
    for line in open(Path(d) / "predictions.jsonl"):
        r = json.loads(line)
        recs[r["record_key"]] = r
    for r in recs.values():
        c = r["condition"]
        if r.get("unavailable") or c.get("protocol") != "A" or r["dataset"] != "2wikimultihopqa":
            continue
        out[r["question_uid"]][(prompt, c["representation"])] = r
    return out


def boot(vals, n_boot=2000, seed=0):
    rng = random.Random(seed)
    n = len(vals)
    s = sorted(sum(vals[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    return [s[int(0.025 * n_boot)], s[min(n_boot - 1, int(0.975 * n_boot) - 1)]]


def main():
    nb = load(sys.argv[2], "noabst")
    qs = set(nb)
    full = load(sys.argv[1], "qa-v2")
    data = {q: {**full[q], **nb[q]} for q in qs if q in full}
    em = lambda r: float((r["eval"].get("em") or 0) == 1)  # noqa: E731
    ab = lambda r: float(not r["failure"]["answered"])  # noqa: E731
    rows = []

    def add(label, prompt, fn_pairs):
        for name, fn in (("em", em), ("abst", ab)):
            pass
        diffs_em, diffs_ab = [], []
        for q, d in data.items():
            v = fn_pairs(d)
            if v is None:
                continue
            (x, y) = v
            diffs_em.append(em(y) - em(x))
            diffs_ab.append(ab(y) - ab(x))
        n = len(diffs_em)
        rows.append({"prompt": prompt, "contrast": label, "n": n, "d_em": sum(diffs_em) / n, "d_em_ci": boot(diffs_em),
                     "d_abst": sum(diffs_ab) / n, "d_abst_ci": boot(diffs_ab)})

    for p in ("qa-v2", "noabst"):
        add("R1-R0", p, lambda d, p=p: (d[(p, "R0")], d[(p, "R1")]) if (p, "R0") in d and (p, "R1") in d else None)
        add("R4P-R4", p, lambda d, p=p: (d[(p, "R4")], d[(p, "R4P")]) if (p, "R4") in d and (p, "R4P") in d else None)
    for rep in ("R0", "R1", "R4", "R4P"):
        add(f"noabst-qa-v2 ({rep})", "prompt effect", lambda d, rep=rep: (d[("qa-v2", rep)], d[("noabst", rep)])
            if ("qa-v2", rep) in d and ("noabst", rep) in d else None)
    # interaction: (b-a | noabst) - (b-a | qa-v2)
    for a, b in (("R0", "R1"), ("R4", "R4P")):
        ie, ia = [], []
        for q, d in data.items():
            keys = [("qa-v2", a), ("qa-v2", b), ("noabst", a), ("noabst", b)]
            if not all(k in d for k in keys):
                continue
            ie.append((em(d[("noabst", b)]) - em(d[("noabst", a)])) - (em(d[("qa-v2", b)]) - em(d[("qa-v2", a)])))
            ia.append((ab(d[("noabst", b)]) - ab(d[("noabst", a)])) - (ab(d[("qa-v2", b)]) - ab(d[("qa-v2", a)])))
        n = len(ie)
        rows.append({"prompt": "interaction", "contrast": f"({b}-{a}) noabst minus qa-v2", "n": n, "d_em": sum(ie) / n,
                     "d_em_ci": boot(ie), "d_abst": sum(ia) / n, "d_abst_ci": boot(ia)})
    # absolute
    for p in ("qa-v2", "noabst"):
        for rep in ("R0", "R1", "R4", "R4P"):
            rs = [d[(p, rep)] for d in data.values() if (p, rep) in d]
            rows.append({"prompt": p, "contrast": f"absolute {rep}", "n": len(rs), "d_em": sum(map(em, rs)) / len(rs), "d_em_ci": None,
                         "d_abst": sum(map(ab, rs)) / len(rs), "d_abst_ci": None})
    out = Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "noabst_contrasts.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in r.items()})
    for r in rows:
        print(f"{r['prompt']:14s} {r['contrast']:34s} n={r['n']} EM/Δ={r['d_em']:+.4f} {r['d_em_ci'] and [round(x, 4) for x in r['d_em_ci']]} "
              f"abst/Δ={r['d_abst']:+.4f}")


if __name__ == "__main__":
    main()
