"""Experiment C preflight checks on two independent smoke runs (separate caches). Outputs are not analysed
for effects; only mechanics are checked.

    PYTHONPATH=src python experiments/andreas_revision/model_replication/smoke_check.py <smoke1> <smoke2> <qwen_confirm2_run> <out.json>
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def load(run: Path) -> dict:
    recs = {}
    with open(run / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            recs[(r["dataset"], r["question_uid"], r["condition"]["representation"])] = r
    return recs


def main(s1: Path, s2: Path, qwen: Path, out: Path) -> None:
    a, b = load(s1), load(s2)
    keys = set(a)
    q = {k: v for k, v in load(qwen).items() if k in keys}
    man = json.loads((s1 / "manifest.json").read_text())
    res = {
        "n_records": [len(a), len(b)], "same_keys": set(a) == set(b),
        "cached_in_run2": sum(r["generation"]["cached"] for r in b.values()),
        "identical_generation_text": sum(a[k]["generation"]["text"] == b[k]["generation"]["text"] for k in keys),
        "identical_user_prompt_vs_qwen_confirm2": sum(a[k]["prompt"]["user"] == q[k]["prompt"]["user"] for k in keys if k in q),
        "n_with_qwen_counterpart": sum(k in q for k in keys),
        "finish_reasons": dict(Counter(r["generation"]["finish_reason"] for r in a.values())),
        "errors": sum(bool(r["generation"].get("error")) or bool(r.get("pipeline_error")) for r in a.values()),
        "answered": sum(r["failure"]["answered"] for r in a.values()),
        "em_defined": sum(r["eval"].get("em") is not None for r in a.values()),
        "format_ok": dict(Counter(str((r.get("parsed") or {}).get("format_ok")) for r in a.values())),
        "loaded_models": man.get("loaded_models"), "determinism": man.get("determinism"),
        "examples": [{"key": list(k), "output": a[k]["generation"]["text"][:160], "gold": a[k]["gold_answers"][:3]}
                     for k in sorted(keys)[:6]],
    }
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*map(Path, sys.argv[1:5]))
