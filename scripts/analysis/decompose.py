"""SECONDARY / EXPLORATORY: decompose a paired EM difference into abstention and accuracy channels.
    PYTHONPATH=src python scripts/analysis/decompose.py <runs.json> <label> <out.csv>
For each primary contrast (Protocol A) and question, classify the pair by which side answered
(parsed, non-abstaining) and sum the EM differences per class. The classes add up to the paired
ΔEM exactly. This analysis was added after seeing the confirmatory result and is labelled exploratory."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build import PRIMARY, load_run, setting  # noqa: E402
from wsh.evaluation.reporting import primary_metric  # noqa: E402

runs = json.loads(Path(sys.argv[1]).read_text())
label, out = sys.argv[2], Path(sys.argv[3])
recs, man, _ = load_run(Path(runs[label]))
by = defaultdict(dict)
for r in recs:
    c = r["condition"]
    if r.get("unavailable") or setting(c) != "A" or c.get("shuffle_seed") not in (None, 0):
        continue
    by[(r["dataset"], r["question_uid"])][c["representation"]] = r
rows = []
for ds in sorted({k[0] for k in by}):
    for a, b in PRIMARY + [("R4", "R4P")]:
        cls = defaultdict(lambda: [0, 0.0])
        n = 0
        for (d, q), reps in by.items():
            if d != ds or a not in reps or b not in reps:
                continue
            n += 1
            ra, rb = reps[a], reps[b]
            ans_a, ans_b = ra["failure"]["answered"], rb["failure"]["answered"]
            k = ("both_answered" if ans_a and ans_b else "only_a_answered" if ans_a else
                 "only_b_answered" if ans_b else "neither_answered")
            cls[k][0] += 1
            m = primary_metric(ra["task"])
            cls[k][1] += (rb["eval"].get(m) or 0) - (ra["eval"].get(m) or 0)
        row = {"run": label, "dataset": ds, "contrast": f"{b}-{a}", "n": n,
               "delta_primary_metric": sum(v[1] for v in cls.values()) / n if n else None}
        for k in ("both_answered", "only_a_answered", "only_b_answered", "neither_answered"):
            row[f"n_{k}"] = cls[k][0]
            row[f"contrib_{k}"] = cls[k][1] / n if n else None
        rows.append(row)
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
