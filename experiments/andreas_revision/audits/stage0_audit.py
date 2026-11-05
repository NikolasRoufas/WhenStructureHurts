"""Stage 0 audit (journal revision). Reads ONLY existing artifacts; generates nothing.

1. Annotation package v2: integrity (hashes, ids, duplicates, empty context), composition (dataset, stratum,
   questions), exact reproduction of the sampler (seed 0) from the pair population, and Monte-Carlo inclusion
   probabilities of every population pair under the same sampler (for design-weighted precision).
2. Experiment B pool on confirm2_v1 (Qwen run): per-question predicted CONTRADICTS pairs and relation-cap status,
   from the R4P_FO EVIDENCE only (no outcome field is read for this part).
3. Reproducibility of relation prediction: R4P_FO prompts of two independent runs on the same questions.
4. Prompt lengths and overflow in the original runs.

    PYTHONPATH=src python experiments/andreas_revision/audits/stage0_audit.py \
        --campaign /data/roufas/wsh_campaign --revision /data/roufas/wsh_revision --out <dir> [--n-sim 5000]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNS = {
    "confirm_v1_qwen_controls": "results/revision/exp1/20261012-200925_a2e6e3a8",
    "confirm_v1_mistral": "results/revision/exp1/20261013-033400_145ae2a1",
    "confirm2_qwen": "results/full/exp1/20261013-005305_1ded82bb",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fc_module():
    spec = importlib.util.spec_from_file_location("fc", ROOT / "scripts/revision/false_contradictions.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def iter_records(run: Path, reps: set[str]):
    seen = {}
    with open(run / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            c = r["condition"]
            if c.get("protocol") == "A" and c.get("representation") in reps:
                seen[r["record_key"]] = r
    return list(seen.values())


def rebuild_population(fc, edges_csv: Path, ctrl: Path) -> tuple[list[dict], float, float]:
    """Exactly the candidate list of false_contradictions.package (before shuffling)."""
    edges = fc._edges(edges_csv)
    ctl = fc._load(ctrl, {"R4P_FO", "R4P_FO_NC"})
    pairs = []
    for e in edges:
        q = e["question_uid"]
        if not e["first_direction_of_pair"] or q not in ctl or len(ctl[q]) < 2:
            continue
        fo = ctl[q]["R4P_FO"]
        if f"{e['source_eid']} CONTRADICTS {e['target_eid']}" not in fo["evidence"]["text"] and \
           f"{e['target_eid']} CONTRADICTS {e['source_eid']}" not in fo["evidence"]["text"]:
            continue
        pairs.append(dict(e, FO=fc._state(fo), NC=fc._state(ctl[q]["R4P_FO_NC"])))
    confs = sorted(p["nli_confidence"] for p in pairs if p["nli_confidence"] is not None)
    return pairs, confs[len(confs) // 4], confs[3 * len(confs) // 4]


def strata_of(p: dict, q25: float, q75: float) -> list[str]:
    s = []
    if p["FO"] == "A" and p["NC"] == "C":
        s.append("restored")
    elif p["FO"] == "A":
        s.append("abstained_other")
    if p["nli_confidence"] is not None and p["nli_confidence"] >= q75:
        s.append("high_confidence")
    if p["nli_confidence"] is not None and p["nli_confidence"] <= q25:
        s.append("low_confidence")
    if p["FO"] == "C" and p["NC"] == "C":
        s.append("no_failure_control")
    return s


def sample(pairs: list[dict], memb: dict, seed: int, strata: list[str], per: int) -> dict[str, str]:
    """pair_id -> stratum, replicating false_contradictions.package's selection loop."""
    order = pairs[:]
    random.Random(seed).shuffle(order)
    taken: dict[str, str] = {}
    for ds in sorted({p["dataset"] for p in order}):
        for st in strata:
            k = 0
            for p in order:
                if k == per:
                    break
                if p["dataset"] == ds and st in memb[p["pair_id"]] and p["pair_id"] not in taken:
                    taken[p["pair_id"]] = st
                    k += 1
    return taken


def audit_package(fc, rev: Path, campaign: Path, out: Path, n_sim: int) -> dict:
    pkg = rev / "false_contra/human_package_v2"
    key_p = rev / "false_contra/human_package_v2_KEY_do_not_share_with_annotators.json"
    summ = json.loads((rev / "false_contra/human_package_v2_summary.json").read_text())
    key = json.loads(key_p.read_text())
    files = {a: list(csv.DictReader(open(pkg / f"pairs_annotator{a}.csv"))) for a in (1, 2)}
    rep: dict = {"package_dir": str(pkg), "key_sha256": sha(key_p),
                 "csv_sha256_match_summary": {f"pairs_annotator{a}.csv": sha(pkg / f"pairs_annotator{a}.csv") ==
                                              summ["sha256"][f"pairs_annotator{a}.csv"] for a in (1, 2)},
                 "n_rows": {a: len(r) for a, r in files.items()},
                 "same_pair_set_in_both_files": {r["pair_id"] for r in files[1]} == {r["pair_id"] for r in files[2]} == set(key),
                 "duplicate_pair_ids": {a: len(r) - len({x["pair_id"] for x in r}) for a, r in files.items()},
                 "labels_filled": {a: sum(bool(x["label_sentences_only"].strip() or x["label_with_context"].strip())
                                          for x in r) for a, r in files.items()}}
    rows = {r["pair_id"]: r for r in files[1]}
    rep["empty_passage_A"] = sum(not r["passage_A"].strip() for r in rows.values())
    rep["empty_passage_B"] = sum(not r["passage_B"].strip() for r in rows.values())
    rep["fact_not_in_its_passage"] = sum((r["fact_A"] not in r["passage_A"]) or (r["fact_B"] not in r["passage_B"])
                                         for r in rows.values() if r["passage_A"] and r["passage_B"])
    rep["identical_fact_texts"] = sum(r["fact_A"].strip() == r["fact_B"].strip() for r in rows.values())
    txt = Counter(tuple(sorted((r["fact_A"], r["fact_B"]))) for r in rows.values())
    rep["duplicate_text_pairs_across_questions"] = sum(c - 1 for c in txt.values() if c > 1)
    qs = Counter(v["question_uid"] for v in key.values())
    rep["n_questions"] = len(qs)
    rep["pairs_per_question"] = dict(sorted(Counter(qs.values()).items()))
    rep["by_dataset"] = dict(Counter(v["dataset"] for v in key.values()))
    rep["by_stratum"] = dict(Counter(v["stratum"] for v in key.values()))
    rep["same_passage_pairs"] = sum(bool(v["same_passage"]) for v in key.values())
    # sampler reproduction + inclusion probabilities
    pairs, q25, q75 = rebuild_population(fc, rev / "contradictions/predicted_contradictions_all.csv",
                                         campaign / RUNS["confirm_v1_qwen_controls"])
    memb = {p["pair_id"]: strata_of(p, q25, q75) for p in pairs}
    rep["population"] = {"n_pairs": len(pairs), "matches_summary_n": len(pairs) == summ["n_pairs_rendered_in_R4P_FO"],
                         "q25": q25, "q75": q75, "q_match_summary": [q25, q75] == [summ["nli_confidence_q25"], summ["nli_confidence_q75"]],
                         "n_in_no_stratum": sum(not m for m in memb.values()),
                         "n_in_no_stratum_by_dataset": dict(Counter(p["dataset"] for p in pairs if not memb[p["pair_id"]])),
                         "by_dataset": dict(Counter(p["dataset"] for p in pairs)),
                         "n_questions": len({p["question_uid"] for p in pairs})}
    # the package's own shuffle: package() shuffles a list built in the same order with Random(0)
    re0 = sample(pairs, memb, 0, fc.STRATA, fc.PER_STRATUM)
    rep["sampler_reproduces_package_exactly"] = re0 == {k: v["stratum"] for k, v in key.items()}
    hits = Counter()
    for s in range(1, n_sim + 1):
        hits.update(sample(pairs, memb, 10_000 + s, fc.STRATA, fc.PER_STRATUM).keys())
    rep["inclusion_probability_simulations"] = n_sim
    pop_rows = []
    for p in pairs:
        pid = p["pair_id"]
        pop_rows.append({"pair_id": pid, "dataset": p["dataset"], "question_uid": p["question_uid"],
                         "strata": "|".join(memb[pid]), "nli_confidence": p["nli_confidence"],
                         "in_package": pid in key, "package_stratum": key.get(pid, {}).get("stratum", ""),
                         "pi_hat": hits[pid] / n_sim, "FO": p["FO"], "NC": p["NC"]})
    with open(out / "package_v2_population_KEY_do_not_share_with_annotators.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pop_rows[0]))
        w.writeheader()
        w.writerows(pop_rows)
    sampled = [r for r in pop_rows if r["in_package"]]
    rep["pi_hat_sampled_pairs"] = {"min": min(r["pi_hat"] for r in sampled), "max": max(r["pi_hat"] for r in sampled),
                                   "n_zero": sum(r["pi_hat"] == 0 for r in sampled)}
    rep["population_file_sha256"] = sha(out / "package_v2_population_KEY_do_not_share_with_annotators.csv")
    return rep


def exp_b_pool(campaign: Path, out: Path) -> dict:
    """Per-question contradiction structure in confirm2 R4P_FO (evidence fields only)."""
    sys.path.insert(0, str(ROOT / "src"))
    from wsh.representations.relation_controls import contradiction_pair_id
    recs = iter_records(campaign / RUNS["confirm2_qwen"], {"R4P_FO"})
    rows = []
    for r in recs:
        q = r["question_uid"]
        ev = r["evidence"]
        cl = [e for e in ev["edges"] if e["relation"] == "CONTRADICTS"]
        pids = {contradiction_pair_id(q, e["source"], e["target"]) for e in cl}
        n_lines = sum(1 for ln in ev["text"].splitlines() if " CONTRADICTS " in f" {ln} ")
        rows.append({"dataset": r["dataset"], "question_uid": q, "n_predicted_edges": len(ev["edges"]),
                     "cap_binding": len(ev["edges"]) > 40, "n_contradicts_edges": len(cl),
                     "n_contradicts_lines_rendered": n_lines, "n_contradiction_pairs": len(pids),
                     "pair_ids": "|".join(sorted(pids))})
    rows.sort(key=lambda x: (x["dataset"], x["question_uid"]))
    with open(out / "expB_confirm2_contradiction_structure.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    res = {}
    for ds in sorted({r["dataset"] for r in rows}):
        d = [r for r in rows if r["dataset"] == ds]
        aff = [r for r in d if r["n_contradicts_lines_rendered"] >= 1]
        elig = [r for r in aff if not r["cap_binding"]]
        res[ds] = {"n_questions": len(d), "n_affected": len(aff), "n_affected_cap_binding": len(aff) - len(elig),
                   "n_eligible": len(elig),
                   "eligible_pairs_per_question": dict(sorted(Counter(r["n_contradiction_pairs"] for r in elig).items())),
                   "eligible_total_pairs": sum(r["n_contradiction_pairs"] for r in elig),
                   "rendered_lines_equal_edges_when_uncapped": all(r["n_contradicts_lines_rendered"] == r["n_contradicts_edges"]
                                                                   for r in elig)}
    return res


def relation_reproducibility(campaign: Path) -> dict:
    a = {r["question_uid"]: r["prompt"]["user"] for r in iter_records(campaign / RUNS["confirm_v1_qwen_controls"], {"R4P_FO"})}
    b = {r["question_uid"]: r["prompt"]["user"] for r in iter_records(campaign / RUNS["confirm_v1_mistral"], {"R4P_FO"})}
    common = set(a) & set(b)
    return {"runs": [RUNS["confirm_v1_qwen_controls"], RUNS["confirm_v1_mistral"]], "n_common": len(common),
            "n_identical_R4P_FO_user_prompt": sum(a[q] == b[q] for q in common)}


def lengths(campaign: Path) -> dict:
    out = {}
    for name in ("confirm2_qwen", "confirm_v1_mistral"):
        recs = iter_records(campaign / RUNS[name], {"R4P_FO", "R4P_FO_NC"})
        d = {}
        for rep in ("R4P_FO", "R4P_FO_NC"):
            xs = [r for r in recs if r["condition"]["representation"] == rep]
            toks = sorted(r["generation"]["input_tokens"] for r in xs)
            d[rep] = {"n": len(xs), "max_input_tokens": toks[-1], "p99": toks[int(0.99 * (len(toks) - 1))],
                      "finish_reasons": dict(Counter(r["generation"]["finish_reason"] for r in xs)),
                      "max_new_tokens_hit": sum(r["generation"]["finish_reason"] == "length" for r in xs)}
        out[name] = d
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", type=Path, required=True)
    ap.add_argument("--revision", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n-sim", type=int, default=5000)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    fc = fc_module()
    res = {"run_dirs": RUNS,
           "predictions_sha256": {k: sha(a.campaign / v / "predictions.jsonl") for k, v in RUNS.items()},
           "package_v2": audit_package(fc, a.revision, a.campaign, a.out, a.n_sim),
           "expB_pool_confirm2": exp_b_pool(a.campaign, a.out),
           "relation_prediction_reproducibility": relation_reproducibility(a.campaign),
           "prompt_lengths": lengths(a.campaign)}
    (a.out / "stage0_audit.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
