"""Revision-1: Exp0 budget and cost accounting per system (descriptive; pilot runs only).

Per dataset x system: n, EM / verdict accuracy, coverage, evidence tokens, units shown, passage retrieval
recall of gold supporting passages, answer string retained in the evidence, extraction calls (sentences),
extraction latency (original-call latency, also for cache hits), answer latency, and for B4 the predicted
relation profile (CONTRADICTS share, conflict sets) and the selection budget actually used.
    PYTHONPATH=src python scripts/revision/exp0_costs.py <exp0_run_dir> <out.csv>
"""
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

recs = {}
for line in open(Path(sys.argv[1]) / "predictions.jsonl"):
    r = json.loads(line)
    recs[r["record_key"]] = r
g = defaultdict(list)
for r in recs.values():
    g[(r["dataset"], r["condition"]["system"])].append(r)
rows = []
mean = lambda xs: st.mean(xs) if xs else None  # noqa: E731
for (ds, s), rs in sorted(g.items()):
    m = "em" if rs[0]["task"] == "qa" else "verdict_acc"
    ok = [r for r in rs if not r.get("unavailable") and "eval" in r]
    info = [r.get("info") or {} for r in ok]
    ext = [i.get("extraction") or {} for i in info]
    rel = [i.get("relations") or {} for i in info]
    rows.append({
        "dataset": ds, "system": s, "n": len(ok), "metric": m,
        "score": mean([float(r["eval"].get(m) or 0) for r in ok]),
        "coverage": mean([float(r["failure"]["answered"]) for r in ok]),
        "evidence_tokens": mean([r["evidence"]["evidence_tokens"] for r in ok]),
        "units": mean([r["evidence"]["n_units"] for r in ok]),
        "gold_passage_recall": mean([i["retrieval_recall"] for i in info if i.get("retrieval_recall") is not None]),
        "answer_in_evidence": mean([r["eval"]["answer_in_evidence"] for r in ok if r["eval"].get("answer_in_evidence") is not None]),
        "extraction_calls": mean([e.get("n_sentences", 0) for e in ext]),
        "extraction_latency_s": mean([e.get("latency_s", 0.0) for e in ext]),
        "extracted_claims": mean([e.get("n_claims", 0) for e in ext]) if any(ext) else None,
        "answer_latency_s": mean([r["generation"]["latency_s"] for r in ok if r.get("generation")]),
        "total_latency_s": mean([(e.get("latency_s", 0.0) + (r.get("generation") or {}).get("latency_s", 0.0)) for e, r in zip(ext, ok)]),
        "b4_contradicts_share": mean([(x["n_edges"].get("CONTRADICTS", 0) / max(1, sum(x["n_edges"].values()))) for x in rel if x.get("n_edges")]) if s == "B4" else None,
        "b4_conflict_sets": mean([i.get("n_conflict_sets", 0) for i in info]) if s == "B4" else None,
        "b4_selection_tokens": mean([(i.get("selection") or {}).get("tokens", 0) for i in info]) if s == "B4" else None,
    })
out = Path(sys.argv[2])
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if v is not None})
