"""EXPLORATORY (added after the confirmatory result): which relation types does R4P show, and how
does abstention vary with them? Reads saved records only.
    PYTHONPATH=src python scripts/analysis/r4p_relations.py <runs.json> <label> <out.csv>"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build import load_run, setting  # noqa: E402

runs = json.loads(Path(sys.argv[1]).read_text())
label, out = sys.argv[2], Path(sys.argv[3])
recs, _, _ = load_run(Path(runs[label]))
REL = re.compile(r"^E\d+ ([A-Z_]+) E\d+$", re.M)
rows = []
groups = defaultdict(lambda: defaultdict(list))
types = defaultdict(Counter)
for r in recs:
    c = r["condition"]
    if r.get("unavailable") or setting(c) != "A" or c["representation"] not in ("R4", "R4P"):
        continue
    text = r["evidence"]["text"]
    rel_block = text.split("Relations:", 1)[1] if "Relations:" in text else ""
    rels = REL.findall(rel_block)
    for t in rels:
        types[(r["dataset"], c["representation"])][t] += 1
    has_contra = any(t.startswith("CONTRADICT") for t in rels)
    key = (r["dataset"], c["representation"], "has_contradiction_line" if has_contra else "no_contradiction_line")
    groups[key]["abstained"].append(float(bool(r["eval"].get("abstained"))))
    groups[key]["em"].append(float(r["eval"].get("em") or 0))
    groups[key]["n_rel"].append(len(rels))
for (ds, rep), cnt in sorted(types.items()):
    n = sum(1 for r in recs if r["dataset"] == ds and r["condition"].get("representation") == rep and setting(r["condition"]) == "A")
    rows.append({"run": label, "dataset": ds, "representation": rep, "kind": "relation_type_counts", "n_records": n,
                 **{f"lines_{k}": v for k, v in cnt.items()}})
for (ds, rep, g), d in sorted(groups.items()):
    rows.append({"run": label, "dataset": ds, "representation": rep, "kind": g, "n_records": len(d["em"]),
                 "abstention_rate": sum(d["abstained"]) / len(d["abstained"]), "em": sum(d["em"]) / len(d["em"]),
                 "mean_relation_lines": sum(d["n_rel"]) / len(d["n_rel"])})
cols = list(dict.fromkeys(k for r in rows for k in r))
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})

# Paired within-question view: for questions whose R4P block contains >=1 CONTRADICTS line vs not,
# compare R4 and R4P on the SAME questions (removes between-question confounding such as type).
byq = defaultdict(dict)
for r in recs:
    c = r["condition"]
    if r.get("unavailable") or setting(c) != "A" or c["representation"] not in ("R4", "R4P"):
        continue
    byq[(r["dataset"], r["question_uid"])][c["representation"]] = r
paired = defaultdict(lambda: defaultdict(list))
for (ds, q), d in byq.items():
    if "R4" not in d or "R4P" not in d:
        continue
    t = d["R4P"]["evidence"]["text"]
    has = "CONTRADICTS" in (t.split("Relations:", 1)[1] if "Relations:" in t else "")
    g = paired[(ds, "R4P_has_contradiction" if has else "R4P_no_contradiction")]
    for rep in ("R4", "R4P"):
        g[f"abst_{rep}"].append(float(bool(d[rep]["eval"].get("abstained"))))
        g[f"em_{rep}"].append(float(d[rep]["eval"].get("em") or 0))
prow = []
for (ds, g), v in sorted(paired.items()):
    n = len(v["em_R4"])
    prow.append({"run": label, "dataset": ds, "subset": g, "n_questions": n,
                 "abstention_R4": sum(v["abst_R4"]) / n, "abstention_R4P": sum(v["abst_R4P"]) / n,
                 "em_R4": sum(v["em_R4"]) / n, "em_R4P": sum(v["em_R4P"]) / n})
with open(str(out).replace(".csv", "_paired.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(prow[0]))
    w.writeheader()
    w.writerows(prow)
for r in prow:
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
