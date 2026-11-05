"""Experiment D gate input: eligible development questions not used by any earlier sample
(smoke, pilot, prompt development, confirm_v1, retr_v1 = configs/excluded_confirm2.json, plus confirm2_v1).
Eligibility rules are the project's pre-specified ones (wsh.data.question_sets.ELIGIBILITY). No generation.

    PYTHONPATH=src python experiments/andreas_revision/retrieval_extension/pool_count.py <out.json>
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from wsh.data.question_sets import ELIGIBILITY, load_excluded
from wsh.data.loaders import iter_questions

ROOT = Path(__file__).resolve().parents[3]


def main(out: Path) -> None:
    excl = set(load_excluded(ROOT / "configs/excluded_confirm2.json"))
    c2 = json.loads((ROOT / "configs/question_sets/confirm2_v1.json").read_text())["datasets"]
    res = {}
    for ds in ("musique", "2wikimultihopqa", "hotpotqa"):
        used2 = {f"{ds}/{q}" for q in c2.get(ds, [])}
        n = n_used = 0
        free = Counter()
        for q in iter_questions(ds, "dev"):
            n += 1
            if q.uid in excl or q.uid in used2:
                n_used += 1
                continue
            if all(f(q) for _, f in ELIGIBILITY[ds]):
                free[str(q.question_type)] += 1
        res[ds] = {"n_dev": n, "n_used_by_earlier_samples": n_used, "n_unused_eligible": sum(free.values()),
                   "unused_eligible_by_type": dict(free)}
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
