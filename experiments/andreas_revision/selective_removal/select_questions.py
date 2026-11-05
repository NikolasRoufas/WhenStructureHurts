"""Experiment B: question selection, annotation package v3, frozen label file and run config.

select   : seeded permutation (seed 11) of the eligible confirm2_v1 questions per dataset (>= 1 rendered
           CONTRADICTS line in Qwen R4P_FO, relation cap not binding). Reads the R4P_FO EVIDENCE only; no
           outcome field is read. Writes tier files (first 150 / next 150 per dataset) as frozen question sets.
package  : the blinded two-annotator package v3 (same format and GUIDE as v2) with EVERY predicted
           contradiction pair of the selected questions; passages reconstructed from the rendered evidence.
           Pairs already in package v2 cannot occur (v2 comes from confirm_v1; checked). Key kept separately.
labels   : convert adjudicated final_labels.csv (annotation_tools.py finalize) into the frozen
           exp1.contradiction_labels JSON; refuses any selected question with an unlabelled pair.

    PYTHONPATH=src python experiments/andreas_revision/selective_removal/select_questions.py select  <confirm2_run> <out_dir>
    ... package <confirm2_run> <tier_qids.json> <out_dir>
    ... labels  <final_labels.csv> <key.json> <tier_qids.json> <out.json>
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arlib import CLASSES3, sha256  # noqa: E402
from wsh.representations.relation_controls import MAX_RELATION_LINES, contradiction_pair_id  # noqa: E402

SEED = 11
TIER = 150
COLS = ["item", "pair_id", "fact_A_source_title", "fact_A", "fact_B_source_title", "fact_B",
        "label_sentences_only", "passage_A", "passage_B", "label_with_context", "notes", "annotator"]
LINE = re.compile(r"\[(E\d+)\] \(source: (.*?)\) (.*)$")
EVIDENCE_ONLY = {"dataset", "question_uid", "condition", "evidence", "record_key"}  # fields select/package may read


def r4p_fo(run: Path) -> dict[str, dict]:
    out = {}
    with open(run / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            c = r["condition"]
            if c.get("protocol") == "A" and c.get("representation") == "R4P_FO":
                out[r["question_uid"]] = {k: r[k] for k in EVIDENCE_ONLY}  # outcomes dropped on read
    return out


def contra_pairs(r: dict) -> dict[str, tuple[str, str]]:
    q = r["question_uid"]
    return {contradiction_pair_id(q, e["source"], e["target"]): tuple(sorted((e["source"], e["target"])))
            for e in r["evidence"]["edges"] if e["relation"] == "CONTRADICTS"}


def eligible(r: dict) -> bool:
    ev = r["evidence"]
    return " CONTRADICTS " in ev["text"] and len(ev["edges"]) <= MAX_RELATION_LINES


def cmd_select(run: Path, out: Path) -> None:
    recs = r4p_fo(run)
    out.mkdir(parents=True, exist_ok=True)
    tiers = {1: {}, 2: {}}
    summ = {"seed": SEED, "tier_size_per_dataset": TIER, "source_run": str(run),
            "source_predictions_sha256": sha256(run / "predictions.jsonl"), "datasets": {}}
    for ds in sorted({r["dataset"] for r in recs.values()}):
        el = sorted(q for q, r in recs.items() if r["dataset"] == ds and eligible(r))
        perm = el[:]
        random.Random(f"{SEED}:{ds}").shuffle(perm)
        for t in (1, 2):
            tiers[t][ds] = perm[(t - 1) * TIER: t * TIER]
        summ["datasets"][ds] = {"n_eligible": len(el), **{f"tier{t}_n_questions": len(tiers[t][ds]) for t in (1, 2)},
                                **{f"tier{t}_n_pairs": sum(len(contra_pairs(recs[q])) for q in tiers[t][ds]) for t in (1, 2)},
                                "permutation_sha256": hashlib.sha256("\n".join(perm).encode()).hexdigest()}
    for t in (1, 2):
        qids = {ds: [q.split("/", 1)[1] for q in qs] for ds, qs in tiers[t].items()}
        (out / f"expB_tier{t}_qids.json").write_text(json.dumps(
            {"created_at": "2026-11-05", "split": "dev", "seed": SEED, "derived_from": "configs/question_sets/confirm2_v1.json",
             "rule": f"tier {t}: eligible confirm2_v1 questions (>=1 rendered CONTRADICTS line in Qwen R4P_FO, "
                     f"<= {MAX_RELATION_LINES} predicted edges), random permutation seed {SEED} per dataset, "
                     f"positions {(t - 1) * TIER}-{t * TIER - 1}", "datasets": qids,
             "question_uids": tiers[t]}, indent=1))
    (out / "expB_selection_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


def _facts_and_passages(r: dict) -> tuple[dict, dict]:
    """claim id -> (title, text); passage id -> passage text (sentences of that passage in rendered order)."""
    lines = {m.group(1): (m.group(2), m.group(3)) for ln in r["evidence"]["text"].split("\n") if (m := LINE.match(ln))}
    facts, passages = {}, {}
    for eid, m in r["evidence"]["id_map"].items():
        title, text = lines[eid]
        for c in m["claim_ids"]:
            facts[c] = (title, text)
    by_p: dict = {}
    for c, (title, text) in facts.items():
        pid, _, idx = c.rpartition("#")
        digits = re.sub(r"\D", "", idx)  # claim ids end in '#s03' (sentence index 3)
        if not digits:
            raise ValueError(f"claim id {c!r} has no sentence index")
        by_p.setdefault(pid, []).append((int(digits), text))
    for pid, sents in by_p.items():
        passages[pid] = " ".join(t for _, t in sorted(sents))
    return facts, passages


def dataset_passages(tier_file: Path) -> dict[str, dict[str, tuple[str, str]]]:
    """question uid -> passage id -> (title, full dataset passage text), as package v2's context (whole passages)."""
    from wsh.config import load_config
    from wsh.experiments.common import load_questions

    cfg = load_config(Path(__file__).resolve().parent / "configs/expB_tier1_qwen.yaml",
                      {"datasets": [{"name": d, "split": "dev", "qids_file": str(tier_file)}
                                    for d in ("2wikimultihopqa", "hotpotqa")]})
    out = {}
    for qs in load_questions(cfg).values():
        for q in qs:
            out[q.uid] = {p.passage_id: (p.title, " ".join(p.sentence(i) for i in range(len(p.sentence_spans))))
                          for p in q.passages}
    return out


def cmd_package(run: Path, tier_file: Path, out: Path, v2_key: Path | None = None) -> None:
    recs = r4p_fo(run)
    tier = json.loads(tier_file.read_text())
    ds_pass = dataset_passages(tier_file)
    rows, key = [], {}
    for ds, qs in sorted(tier["question_uids"].items()):
        for q in qs:
            r = recs[q]
            facts, _ = _facts_and_passages(r)
            passages = {pid: text for pid, (_, text) in ds_pass[q].items()}
            for pid, (s, t) in sorted(contra_pairs(r).items()):
                if pid in key:
                    raise ValueError(f"pair id collision {pid}")
                (ta, xa), (tb, xb) = facts[s], facts[t]
                rows.append({"pair_id": pid, "fact_A_source_title": ta, "fact_A": xa, "fact_B_source_title": tb,
                             "fact_B": xb, "passage_A": passages[s.rpartition("#")[0]],
                             "passage_B": passages[t.rpartition("#")[0]]})
                key[pid] = {"question_uid": q, "dataset": ds, "source_claim": s, "target_claim": t,
                            "same_passage": s.rpartition("#")[0] == t.rpartition("#")[0]}
    if v2_key is not None and set(key) & set(json.loads(v2_key.read_text())):
        raise ValueError("package v3 overlaps package v2")
    pkg = out / "human_package_v3"
    pkg.mkdir(parents=True, exist_ok=True)
    for a in (1, 2):
        order = rows[:]
        random.Random(200 + a).shuffle(order)
        with open(pkg / f"pairs_annotator{a}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            for i, r in enumerate(order, 1):
                w.writerow({**r, "item": i, "label_sentences_only": "", "label_with_context": "", "notes": "", "annotator": ""})
    kp = out / "human_package_v3_KEY_do_not_share_with_annotators.json"
    kp.write_text(json.dumps(key, indent=1))
    summ = {"tier_file": str(tier_file), "tier_file_sha256": sha256(tier_file), "n_pairs": len(rows),
            "n_questions": len({v["question_uid"] for v in key.values()}),
            "by_dataset": dict(Counter(v["dataset"] for v in key.values())),
            "same_passage_pairs": sum(v["same_passage"] for v in key.values()),
            "csv_sha256": {a: sha256(pkg / f"pairs_annotator{a}.csv") for a in (1, 2)}, "key_sha256": sha256(kp)}
    (out / "human_package_v3_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


def cmd_labels(final: Path, key_p: Path, tier_file: Path, out: Path) -> None:
    key = json.loads(key_p.read_text())
    tier = json.loads(tier_file.read_text())
    lab = {r["pair_id"]: r["label3"] for r in csv.DictReader(open(final, newline=""))}
    bad = {v for v in lab.values() if v not in CLASSES3}
    if bad:
        raise SystemExit(f"invalid labels {bad}")
    qs: dict = {}
    for pid, k in key.items():
        qs.setdefault(k["question_uid"], {})[pid] = lab.get(pid)
    incomplete = sorted(q for q, d in qs.items() if any(v is None for v in d.values()))
    if incomplete:
        raise SystemExit(f"refused: {len(incomplete)} questions have unlabelled pairs (e.g. {incomplete[:3]}); "
                         "a question enters Experiment B only with every pair adjudicated")
    want = {q for v in tier["question_uids"].values() for q in v}
    if set(qs) != want:
        raise SystemExit("label key does not cover exactly the tier questions")
    doc = {"label_source": "human_adjudicated", "final_labels": str(final), "final_labels_sha256": sha256(final),
           "key_sha256": sha256(key_p), "tier_file_sha256": sha256(tier_file),
           "composition": dict(Counter(_comp(d) for d in qs.values())), "questions": qs}
    out.write_text(json.dumps(doc, indent=1))
    print(json.dumps({k: v for k, v in doc.items() if k != "questions"}, indent=1))


def _comp(d: dict) -> str:
    s = set(d.values())
    if s == {"false"}:
        return "all_false"
    if s == {"genuine"}:
        return "all_genuine"
    if "ambiguous" in s:
        return "any_ambiguous"
    return "mixed_genuine_false"


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "select":
        cmd_select(Path(sys.argv[2]), Path(sys.argv[3]))
    elif c == "package":
        cmd_package(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]) if len(sys.argv) > 5 else None)
    elif c == "labels":
        cmd_labels(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    else:
        raise SystemExit(__doc__)
