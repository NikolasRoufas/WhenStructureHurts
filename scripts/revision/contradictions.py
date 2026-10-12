"""Revision-1: predicted-contradiction audit (EXPLORATORY; automatic diagnostics only).

export   : every predicted CONTRADICTS edge shown to the reader under R4P on the confirmatory sample, with
           both facts, their source titles, the NLI confidence, question metadata and the R4/R4P outcomes;
           automatic (heuristic) diagnostic categories; and a BLINDED human-verification package (no model
           outcomes, no automatic category) with a stratified sample.
import   : validate a completed package (allowed labels, every row labelled, annotator id, digests).
effects  : paired intervention effects from the fixed-order controls run (R4P_FO vs R4P_FO_NC, etc.),
           stratified by contradiction-line count, relation-line count, question type and hop count, plus a
           question-level linear model of the paired difference on contradiction lines, relation lines and
           evidence length (bootstrap CIs over questions).

Automatic categories are NOT human judgements and are never reported as precision/recall.

    PYTHONPATH=src python scripts/revision/contradictions.py export  <F_exp1_dir> <out_dir> [--sample 240]
    PYTHONPATH=src python scripts/revision/contradictions.py import  <package_dir>
    PYTHONPATH=src python scripts/revision/contradictions.py effects <controls_run_dir> <out_dir>
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

LABELS = ["genuine_contradiction", "compatible_different_entities", "compatible_different_times_or_values",
          "coreference_or_entity_resolution_error", "context_ambiguity", "uncertain"]
YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")
NUM = re.compile(r"\b\d+(?:[.,]\d+)?\b")
PRONOUN_START = re.compile(r"^(it|he|she|they|his|her|its|their|this|these|the film|the album|the movie)\b", re.I)


def load(run_dir: Path) -> list[dict]:
    recs = {}
    with open(run_dir / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            recs[r["record_key"]] = r
    return list(recs.values())


def state(r) -> str:
    if not r["failure"]["answered"]:
        return "A"
    return "C" if (r["eval"].get("em") or 0) == 1 else "W"


def facts_from_evidence(r) -> dict[str, dict]:
    """claim id -> {'eid', 'text', 'title'} from the rendered evidence (what the reader actually saw)."""
    out = {}
    lines = r["evidence"]["text"].split("\n")
    for eid, m in r["evidence"]["id_map"].items():
        cids = m.get("claim_ids") or []
        line = next((ln for ln in lines if ln.startswith(f"[{eid}]")), "")
        mt = re.match(r"\[E\d+\] \(source: (.*?)\) (.*)$", line)
        title, text = (mt.group(1), mt.group(2)) if mt else ("", line)
        for c in cids:
            out[c] = {"eid": eid, "text": text, "title": title}
    return out


def auto_category(a: dict, b: dict) -> str:
    """Heuristic triage only (NOT a judgement)."""
    if a["title"] and b["title"] and a["title"].lower() != b["title"].lower():
        return "auto:different_source_titles"
    ya, yb = set(YEAR.findall(a["text"])), set(YEAR.findall(b["text"]))
    if ya and yb and ya != yb:
        return "auto:same_title_different_years"
    if set(NUM.findall(a["text"])) != set(NUM.findall(b["text"])) and NUM.search(a["text"]) and NUM.search(b["text"]):
        return "auto:same_title_different_numbers"
    if PRONOUN_START.match(a["text"]) or PRONOUN_START.match(b["text"]):
        return "auto:same_title_pronoun_initial"
    return "auto:same_title_other"


def export(f_dir: Path, out: Path, sample: int = 240, seed: int = 0) -> None:
    recs = load(f_dir)
    by = defaultdict(dict)
    for r in recs:
        c = r["condition"]
        if r.get("unavailable") or c.get("protocol") != "A" or c.get("representation") not in ("R4", "R4P"):
            continue
        by[r["question_uid"]][c["representation"]] = r
    rows = []
    for q, d in sorted(by.items()):
        if "R4P" not in d or "R4" not in d:
            continue
        rp = d["R4P"]
        facts = facts_from_evidence(rp)
        seen_pairs = set()
        for e in rp["evidence"]["edges"]:
            if e["relation"] != "CONTRADICTS" or e["source"] not in facts or e["target"] not in facts:
                continue
            pair = tuple(sorted((e["source"], e["target"])))
            a, b = facts[e["source"]], facts[e["target"]]
            rows.append({
                "edge_id": hashlib.sha256(f"{q}|{e['source']}|{e['target']}".encode()).hexdigest()[:16],
                "pair_id": hashlib.sha256(f"{q}|{pair}".encode()).hexdigest()[:16],
                "first_direction_of_pair": pair not in seen_pairs,
                "dataset": rp["dataset"], "question_uid": q, "question": rp["question"],
                "question_type": rp.get("question_type"), "hop_count": rp.get("hop_count"),
                "source_claim": e["source"], "target_claim": e["target"],
                "source_eid": a["eid"], "target_eid": b["eid"], "source_title": a["title"], "target_title": b["title"],
                "source_text": a["text"], "target_text": b["text"],
                "same_passage": e["source"].split("#")[0] == e["target"].split("#")[0],
                "nli_confidence": e.get("confidence"),
                # visible = the rendered relation line is in the prompt (layouts cap relation lines at 40)
                "shown_to_reader": f"{a['eid']} CONTRADICTS {b['eid']}" in rp["evidence"]["text"],
                "auto_category": auto_category(a, b),
                "n_contradicts_lines_in_prompt": rp["evidence"]["text"].count(" CONTRADICTS "),
                "n_relation_lines_in_prompt": rp["evidence"]["n_relations"],
                "R4_state": state(d["R4"]), "R4P_state": state(rp),
                "R4_answer": (d["R4"].get("parsed") or {}).get("answer"), "R4P_answer": (rp.get("parsed") or {}).get("answer"),
                "gold": rp["gold_answers"],
            })
            seen_pairs.add(pair)
    out.mkdir(parents=True, exist_ok=True)
    cols = list(rows[0])
    with open(out / "predicted_contradictions_all.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in r.items()})
    summ = {"n_edges": len(rows), "n_edges_shown_to_reader": sum(r["shown_to_reader"] for r in rows),
            "n_contradicts_lines_rendered_by_dataset": dict(Counter(r["dataset"] for r in rows if r["shown_to_reader"])),
            "n_pairs": sum(r["first_direction_of_pair"] for r in rows),
            "n_questions_with_contradicts": len({r["question_uid"] for r in rows}),
            "by_dataset": dict(Counter(r["dataset"] for r in rows)),
            "auto_category_pairs": dict(Counter(r["auto_category"] for r in rows if r["first_direction_of_pair"])),
            "same_passage_pairs": sum(1 for r in rows if r["first_direction_of_pair"] and r["same_passage"]),
            "nli_confidence_quartiles": _quartiles([r["nli_confidence"] for r in rows if r["nli_confidence"] is not None])}
    # blinded, stratified human package: one row per unordered pair; strata = dataset x auto category;
    # high-impact cases (R4 correct, R4P abstained) are over-sampled to half of the package, but the
    # annotator never sees outcomes or categories, so labels are not conditioned on them.
    pairs = [r for r in rows if r["first_direction_of_pair"] and r["shown_to_reader"]]
    rng = random.Random(seed)
    hi = [r for r in pairs if r["R4_state"] == "C" and r["R4P_state"] == "A"]
    lo = [r for r in pairs if not (r["R4_state"] == "C" and r["R4P_state"] == "A")]
    rng.shuffle(hi)
    rng.shuffle(lo)
    take = hi[: sample // 2] + lo[: sample - min(len(hi), sample // 2)]
    rng.shuffle(take)
    pkg = out / "human_package_v1"
    pkg.mkdir(exist_ok=True)
    with open(pkg / "pairs_to_label.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "pair_id", "fact_A_source_title", "fact_A", "fact_B_source_title", "fact_B", "label", "notes", "annotator"])
        for i, r in enumerate(take, 1):
            w.writerow([i, r["pair_id"], r["source_title"], r["source_text"], r["target_title"], r["target_text"], "", "", ""])
    key = {r["pair_id"]: {k: r[k] for k in ("question_uid", "dataset", "auto_category", "R4_state", "R4P_state", "nli_confidence")}
           for r in take}
    (out / "human_package_v1_KEY_do_not_share_with_annotators.json").write_text(json.dumps(key, indent=1))
    (pkg / "GUIDE.md").write_text(GUIDE.format(labels="\n".join(f"- `{x}`" for x in LABELS), n=len(take)))
    summ["human_package"] = {"n_items": len(take), "n_high_impact_oversampled": min(len(hi), sample // 2),
                             "sha256_pairs_csv": hashlib.sha256((pkg / "pairs_to_label.csv").read_bytes()).hexdigest()}
    (out / "contradictions_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


def _quartiles(xs):
    xs = sorted(xs)
    if not xs:
        return None
    q = lambda p: xs[min(len(xs) - 1, int(p * len(xs)))]  # noqa: E731
    return {"min": xs[0], "q25": q(0.25), "median": q(0.5), "q75": q(0.75), "max": xs[-1], "n": len(xs)}


GUIDE = """# Human verification: predicted contradiction relations (package v1)

You will see {n} pairs of sentences. Each pair was labelled CONTRADICTS by an automatic relation predictor.
Both sentences come from Wikipedia passages that a dataset marks as supporting evidence for a question
(the question itself is not shown). Judge only whether the two sentences, read as they are, contradict
each other. Do not look anything up. Fill `label` with exactly one of:

{labels}

Definitions:
- genuine_contradiction: both sentences cannot be true of the same thing at the same time.
- compatible_different_entities: they describe different people/works/places, so no conflict.
- compatible_different_times_or_values: same entity, but different events, dates, roles or attributes that can all be true.
- coreference_or_entity_resolution_error: a conflict appears only because a pronoun or name is resolved to the wrong entity.
- context_ambiguity: cannot be decided without the surrounding passage.
- uncertain: none of the above can be decided.

Write your initials in `annotator` on every row, and anything unusual in `notes`. Labels must be your own
judgement; leave a row blank rather than guessing. Import with:
`PYTHONPATH=src python scripts/revision/contradictions.py import <this directory>`.
"""


def import_pkg(pkg: Path) -> dict:
    rows = list(csv.DictReader(open(pkg / "pairs_to_label.csv")))
    errors = []
    for r in rows:
        if r["label"] and r["label"] not in LABELS:
            errors.append(f"item {r['item']}: invalid label {r['label']!r}")
        if r["label"] and not r["annotator"].strip():
            errors.append(f"item {r['item']}: label without annotator")
    done = [r for r in rows if r["label"]]
    if errors:
        raise SystemExit("import refused:\n" + "\n".join(errors))
    rep = {"n_items": len(rows), "n_labelled": len(done), "labels": dict(Counter(r["label"] for r in done)),
           "annotators": sorted({r["annotator"].strip() for r in done}), "complete": len(done) == len(rows)}
    (pkg / "IMPORT_REPORT.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))
    return rep


# ---------------------------------------------------------------------------------------- effects

def _boot(vals, stat, n_boot=2000, seed=0):
    rng = random.Random(seed)
    n = len(vals)
    s = sorted(stat([vals[rng.randrange(n)] for _ in range(n)]) for _ in range(n_boot))
    return [s[int(0.025 * n_boot)], s[min(n_boot - 1, int(0.975 * n_boot) - 1)]]


def effects(run_dir: Path, out: Path) -> None:
    import numpy as np

    recs = load(run_dir)
    by = defaultdict(dict)
    for r in recs:
        if r.get("unavailable") or r["condition"].get("protocol") != "A":
            continue
        by[(r["dataset"], r["question_uid"])][r["condition"]["representation"]] = r
    contrasts = [("R4P_FO_NC", "R4P_FO", "remove contradiction lines (derived order)"),
                 ("R4P_NC", "R4P", "remove contradiction lines (predicted order)"),
                 ("R4N_FO", "R4P_FO", "relabel predicted lines as neutral (same pairs/count)"),
                 ("R5", "R4N_FO", "add neutral lines (count/overhead only)"),
                 ("R5", "R4P_FO", "add predicted lines at fixed order"),
                 ("R4", "R4P_FO", "derived vs predicted lines at fixed order"),
                 ("R5", "R5P", "order only: predicted vs derived order, no lines"),
                 ("R4P_FO", "R4P", "order only, with predicted lines"),
                 ("R4", "R4P", "original R4P - R4 (order + lines)")]
    em = lambda r: float((r["eval"].get("em") or 0) == 1)  # noqa: E731
    ab = lambda r: float(not r["failure"]["answered"])  # noqa: E731
    rows, strata = [], []
    for ds in sorted({k[0] for k in by}):
        for a, b, desc in contrasts:  # difference reported as b - a
            items = []
            for (d, q), v in by.items():
                if d != ds or a not in v or b not in v:
                    continue
                ra, rb = v[a], v[b]
                pred_edges = (v.get("R4P") or v.get("R4P_FO") or rb)["evidence"]["edges"]
                items.append({"d_em": em(rb) - em(ra), "d_ab": ab(rb) - ab(ra),
                              "identical": ra["evidence"]["text"] == rb["evidence"]["text"],
                              "n_contra": (v.get("R4P_FO") or rb)["evidence"]["text"].count(" CONTRADICTS "),
                              "n_rel_b": rb["evidence"]["n_relations"], "n_rel_a": ra["evidence"]["n_relations"],
                              "tok_b": rb["evidence"]["evidence_tokens"], "tok_a": ra["evidence"]["evidence_tokens"],
                              "qtype": rb.get("question_type"), "hops": rb.get("hop_count"),
                              "R4_correct": em(v["R4"]) if "R4" in v else None})
            if not items:
                continue
            mean = lambda xs, k: sum(x[k] for x in xs) / len(xs)  # noqa: E731
            row = {"dataset": ds, "contrast": f"{b}-{a}", "description": desc, "n": len(items),
                   "n_identical_prompts": sum(x["identical"] for x in items),
                   "d_em": mean(items, "d_em"), "d_em_ci": _boot(items, lambda xs: mean(xs, "d_em")),
                   "d_abst": mean(items, "d_ab"), "d_abst_ci": _boot(items, lambda xs: mean(xs, "d_ab")),
                   "mean_rel_lines_a": mean(items, "n_rel_a"), "mean_rel_lines_b": mean(items, "n_rel_b"),
                   "mean_tokens_a": mean(items, "tok_a"), "mean_tokens_b": mean(items, "tok_b")}
            rows.append(row)
            # strata: number of predicted contradiction lines, question type, hop count
            for key, fn in (("n_contra_lines", lambda x: "0" if x["n_contra"] == 0 else "1-2" if x["n_contra"] <= 2 else "3-5" if x["n_contra"] <= 5 else "6+"),
                            ("question_type", lambda x: str(x["qtype"])), ("hop_count", lambda x: str(x["hops"]))):
                g = defaultdict(list)
                for x in items:
                    g[fn(x)].append(x)
                for val, xs in sorted(g.items()):
                    if len(xs) < 20:
                        continue
                    strata.append({"dataset": ds, "contrast": f"{b}-{a}", "stratum": f"{key}={val}", "n": len(xs),
                                   "n_identical_prompts": sum(x["identical"] for x in xs),
                                   "d_em": mean(xs, "d_em"), "d_em_ci": _boot(xs, lambda ys: mean(ys, "d_em")),
                                   "d_abst": mean(xs, "d_ab"), "d_abst_ci": _boot(xs, lambda ys: mean(ys, "d_ab"))})
            # question-level linear model for the removal contrast: d = b0 + b1*n_contra + b2*d_rel_lines + b3*d_tokens/100
            if (a, b) == ("R4P_FO_NC", "R4P_FO"):
                for target in ("d_em", "d_ab"):
                    X = np.array([[1.0, x["n_contra"], x["n_rel_b"] - x["n_rel_a"] - x["n_contra"], (x["tok_b"] - x["tok_a"]) / 100]
                                  for x in items])
                    y = np.array([x[target] for x in items])
                    beta = np.linalg.lstsq(X, y, rcond=None)[0]
                    rng = np.random.default_rng(0)
                    bs = []
                    for _ in range(2000):
                        i = rng.integers(0, len(y), len(y))
                        bs.append(np.linalg.lstsq(X[i], y[i], rcond=None)[0])
                    bs = np.array(bs)
                    rows.append({"dataset": ds, "contrast": f"{b}-{a}", "description": f"OLS of {target} on predictors",
                                 "n": len(y), "coef_names": ["intercept", "n_contradiction_lines", "other_line_diff", "token_diff_per_100"],
                                 "coef": beta.tolist(), "coef_ci": [[float(np.quantile(bs[:, j], 0.025)), float(np.quantile(bs[:, j], 0.975))]
                                                                     for j in range(bs.shape[1])]})
    out.mkdir(parents=True, exist_ok=True)
    for name, data in (("relation_control_effects.csv", rows), ("relation_control_strata.csv", strata)):
        cols = list(dict.fromkeys(k for r in data for k in r))
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in data:
                w.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in r.items()})
    for r in rows:
        if "d_em" in r:
            print(f"{r['dataset'][:6]} {r['contrast']:18s} n={r['n']} ident={r['n_identical_prompts']} dEM={r['d_em']:+.4f} "
                  f"{[round(x, 4) for x in r['d_em_ci']]} dAbst={r['d_abst']:+.4f} {[round(x, 4) for x in r['d_abst_ci']]} "
                  f"lines {r['mean_rel_lines_a']:.1f}->{r['mean_rel_lines_b']:.1f} tok {r['mean_tokens_a']:.0f}->{r['mean_tokens_b']:.0f}  # {r['description']}")
        else:
            print(r["dataset"][:6], r["description"], [round(c, 4) for c in r["coef"]], [[round(x, 4) for x in c] for c in r["coef_ci"]])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[sys.argv.index("--sample") + 1]) if "--sample" in sys.argv else 240)
    elif cmd == "import":
        import_pkg(Path(sys.argv[2]))
    elif cmd == "effects":
        effects(Path(sys.argv[2]), Path(sys.argv[3]))
