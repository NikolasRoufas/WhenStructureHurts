"""Independent check of package v3 context: every passage_A/passage_B must equal the dataset's own passage text
(sentences joined, whitespace-normalised) and contain its fact. Loads the questions through the project loader.

    PYTHONPATH=src python experiments/andreas_revision/selective_removal/verify_package_context.py <pkg_dir> <key.json> <out.json>
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

from wsh.config import load_config
from wsh.experiments.common import load_questions

CFG = Path(__file__).resolve().parent / "configs/expB_tier1_qwen.yaml"
norm = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731


def main(pkg: Path, key_p: Path, out: Path) -> None:
    key = json.loads(key_p.read_text())
    qs = {q.uid: q for v in load_questions(load_config(CFG)).values() for q in v}
    rows = list(csv.DictReader(open(pkg / "pairs_annotator1.csv", newline="")))
    bad, n = [], 0
    for r in rows:
        k = key[r["pair_id"]]
        q = qs[k["question_uid"]]
        ps = {p.passage_id: p for p in q.passages}
        for side, claim in (("A", k["source_claim"]), ("B", k["target_claim"])):
            p = ps[claim.rpartition("#")[0]]
            ref = norm(" ".join(p.sentence(i) for i in range(len(p.sentence_spans))))
            n += 1
            if norm(r[f"passage_{side}"]) != ref or norm(r[f"fact_{side}"]) not in ref or r[f"fact_{side}_source_title"] != p.title:
                bad.append({"pair_id": r["pair_id"], "side": side})
    res = {"n_passages_checked": n, "n_mismatch": len(bad), "mismatches": bad[:20]}
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    if bad:
        raise SystemExit("package context differs from the dataset passages")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
