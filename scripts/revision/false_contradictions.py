"""Revision-2: false-contradiction analysis (EXPLORATORY) and human package v2.

package   : a stratified, blinded two-annotator package of predicted CONTRADICTS pairs shown to the reader in the
            fixed-order controls (R4P_FO), with a sentence-only label and a with-context label per pair.
            Strata (per dataset, sampled without replacement, seed 0):
              high_confidence    NLI confidence in the top quartile
              low_confidence     NLI confidence in the bottom quartile (all predicted edges are >= 0.90)
              restored           R4P_FO abstained, R4P_FO_NC correct (removal restored the answer)
              abstained_other    R4P_FO abstained, not restored
              no_failure_control R4P_FO and R4P_FO_NC both correct
            The annotators never see the stratum, the question, the outcomes, the NLI score or the automatic
            category. The key stays outside the package.
import    : validate both annotators' files; agreement (raw, Cohen's kappa) on the sentence-only labels;
            per-stratum label distribution. Refuses incomplete or invalid files. Nothing is imported as a
            human label unless a named annotator wrote it.
mechanism : correlational: the paired effect of contradiction lines (R4P_FO - R4P_FO_NC) by the question's
            maximum NLI confidence, dominant automatic category, and same-passage pairs.

    PYTHONPATH=src python scripts/revision/false_contradictions.py package   <all_edges.csv> <controls_run> <F_exp1_run> <out>
    PYTHONPATH=src python scripts/revision/false_contradictions.py import    <package_dir> <key.json>
    PYTHONPATH=src python scripts/revision/false_contradictions.py mechanism <all_edges.csv> <controls_run> <out>

<all_edges.csv> is predicted_contradictions_all.csv written by contradictions.py export (revision-1).
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from wsh.evaluation.statistics import paired_bootstrap

LABELS = ["genuine_contradiction", "compatible_different_entities", "compatible_different_times_or_values",
          "coreference_or_entity_resolution_error", "context_ambiguity", "compatible_other", "uncertain"]
STRATA = ["restored", "abstained_other", "high_confidence", "low_confidence", "no_failure_control"]
PER_STRATUM = 30  # per dataset -> 300 pairs


def _load(run: Path, reps: set[str]) -> dict:
    by: dict = defaultdict(dict)
    with open(run / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            c = r["condition"]
            if c["protocol"] == "A" and c["representation"] in reps and not r.get("unavailable"):
                by[r["question_uid"]][c["representation"]] = r
    return by


def _state(r: dict) -> str:
    if not r["failure"]["answered"]:
        return "A"
    return "C" if (r["eval"].get("em") or 0) == 1 else "W"


def _edges(path: Path) -> list[dict]:
    rows = list(csv.DictReader(open(path)))
    for r in rows:
        r["nli_confidence"] = float(r["nli_confidence"]) if r["nli_confidence"] else None
        r["first_direction_of_pair"] = r["first_direction_of_pair"] == "True"
        r["same_passage"] = r["same_passage"] == "True"
    return rows


def _passages(r0: dict) -> dict[str, str]:
    """passage id -> rendered passage text of the R0 record (what the passage-format reader saw)."""
    lines = r0["evidence"]["text"].split("\n")
    out = {}
    for eid, m in r0["evidence"]["id_map"].items():
        line = next((ln for ln in lines if ln.startswith(f"[{eid}]")), "")
        for p in m.get("passage_ids") or []:
            out[p] = line.split(") ", 1)[1] if line.startswith(f"[{eid}] (source:") else line
    return out


def package(edges_csv: Path, ctrl: Path, f_run: Path, out: Path, seed: int = 0) -> None:
    edges = _edges(edges_csv)
    ctl = _load(ctrl, {"R4P_FO", "R4P_FO_NC"})
    r0 = _load(f_run, {"R0"})
    pairs = []
    for e in edges:
        q = e["question_uid"]
        if not e["first_direction_of_pair"] or q not in ctl or len(ctl[q]) < 2:
            continue
        fo = ctl[q]["R4P_FO"]
        if f"{e['source_eid']} CONTRADICTS {e['target_eid']}" not in fo["evidence"]["text"] and \
           f"{e['target_eid']} CONTRADICTS {e['source_eid']}" not in fo["evidence"]["text"]:
            continue  # not rendered in the fixed-order prompt
        e = dict(e, FO=_state(fo), NC=_state(ctl[q]["R4P_FO_NC"]))
        pairs.append(e)
    confs = sorted(p["nli_confidence"] for p in pairs if p["nli_confidence"] is not None)
    q25, q75 = confs[len(confs) // 4], confs[3 * len(confs) // 4]

    def stratum_of(p: dict) -> list[str]:
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

    rng = random.Random(seed)
    rng.shuffle(pairs)
    taken, used = [], set()
    for ds in sorted({p["dataset"] for p in pairs}):
        for st in STRATA:
            cand = [p for p in pairs if p["dataset"] == ds and st in stratum_of(p) and p["pair_id"] not in used]
            for p in cand[:PER_STRATUM]:
                taken.append(dict(p, stratum=st))
                used.add(p["pair_id"])
    rows = []
    for p in taken:
        ctx = _passages(r0[p["question_uid"]]["R0"]) if p["question_uid"] in r0 else {}
        rows.append({"pair_id": p["pair_id"], "fact_A_source_title": p["source_title"], "fact_A": p["source_text"],
                     "fact_B_source_title": p["target_title"], "fact_B": p["target_text"],
                     "passage_A": ctx.get(p["source_claim"].split("#")[0], ""),
                     "passage_B": ctx.get(p["target_claim"].split("#")[0], "")})
    pkg = out / "human_package_v2"
    pkg.mkdir(parents=True, exist_ok=True)
    cols = ["item", "pair_id", "fact_A_source_title", "fact_A", "fact_B_source_title", "fact_B",
            "label_sentences_only", "passage_A", "passage_B", "label_with_context", "notes", "annotator"]
    for a in (1, 2):
        order = rows[:]
        random.Random(100 + a).shuffle(order)  # each annotator sees a different order
        with open(pkg / f"pairs_annotator{a}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for i, r in enumerate(order, 1):
                w.writerow({**r, "item": i, "label_sentences_only": "", "label_with_context": "", "notes": "", "annotator": ""})
    key = {p["pair_id"]: {k: p[k] for k in ("stratum", "dataset", "question_uid", "question_type", "auto_category",
                                            "nli_confidence", "same_passage", "FO", "NC", "R4_state", "R4P_state")}
           for p in taken}
    (out / "human_package_v2_KEY_do_not_share_with_annotators.json").write_text(json.dumps(key, indent=1))
    (pkg / "GUIDE.md").write_text(GUIDE.format(n=len(rows), labels="\n".join(f"- `{x}`" for x in LABELS)))
    summ = {"n_pairs_rendered_in_R4P_FO": len(pairs), "nli_confidence_q25": q25, "nli_confidence_q75": q75,
            "n_items": len(rows), "by_stratum_dataset": dict(Counter(f"{p['dataset']}:{p['stratum']}" for p in taken)),
            "available_by_stratum_dataset": dict(Counter(f"{p['dataset']}:{s}" for p in pairs for s in stratum_of(p))),
            "sha256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(pkg.glob("*.csv"))}}
    (out / "human_package_v2_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


GUIDE = """# Human verification of predicted contradictions (package v2)

Two people label the same {n} sentence pairs **independently** (`pairs_annotator1.csv`, `pairs_annotator2.csv`;
the rows are in different orders). Do not discuss items until both files are complete.

Each pair was marked CONTRADICTS by an automatic relation predictor. Both sentences come from Wikipedia passages
that a dataset marks as supporting evidence for one question. You are not shown the question, the predictor's
score, or any model output.

**Step 1 (`label_sentences_only`).** Read only `fact_A` and `fact_B` (with their source titles) and decide whether
they contradict each other as written. Fill this column for the row before reading the passages.

**Step 2 (`label_with_context`).** Now read `passage_A` and `passage_B` (the full passages the sentences come
from) and label the pair again. It may change or stay the same.

Use exactly one of:

{labels}

- genuine_contradiction: both sentences cannot be true of the same thing at the same time.
- compatible_different_entities: they are about different people, works or places.
- compatible_different_times_or_values: same entity, different events, dates, roles or attributes that can all be true.
- coreference_or_entity_resolution_error: a conflict appears only if a pronoun or name is resolved to the wrong entity.
- context_ambiguity: cannot be decided from what you can see (use only in step 1 if the passage is needed).
- compatible_other: no conflict, for another reason (say which in `notes`).
- uncertain: you cannot decide.

Write your initials in `annotator` on every labelled row. Never guess to fill a row; leave it blank instead.
Do not use any AI tool to label. Validate with
`PYTHONPATH=src python scripts/revision/false_contradictions.py import <this directory> <key.json>`.
"""


def _kappa(a: list[str], b: list[str]) -> float | None:
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return None if pe == 1 else (po - pe) / (1 - pe)


def import_pkg(pkg: Path, key_path: Path) -> dict:
    key = json.loads(key_path.read_text())
    errors, files = [], {}
    for a in (1, 2):
        rows = list(csv.DictReader(open(pkg / f"pairs_annotator{a}.csv")))
        for r in rows:
            for col in ("label_sentences_only", "label_with_context"):
                if r[col] and r[col] not in LABELS:
                    errors.append(f"annotator{a} item {r['item']}: invalid {col} {r[col]!r}")
            if (r["label_sentences_only"] or r["label_with_context"]) and not r["annotator"].strip():
                errors.append(f"annotator{a} item {r['item']}: label without annotator")
            if r["pair_id"] not in key:
                errors.append(f"annotator{a} item {r['item']}: unknown pair_id")
        files[a] = {r["pair_id"]: r for r in rows}
    names = [{r["annotator"].strip() for r in files[a].values() if r["annotator"].strip()} for a in (1, 2)]
    if names[0] and names[1] and names[0] & names[1]:
        errors.append("the two files carry the same annotator id; labels must be independent")
    if errors:
        raise SystemExit("import refused:\n" + "\n".join(errors))
    both = [p for p in key if files[1][p]["label_sentences_only"] and files[2][p]["label_sentences_only"]]
    rep = {"n_items": len(key), "n_labelled_by_both": len(both), "complete": len(both) == len(key),
           "annotators": [sorted(n) for n in names]}
    for col in ("label_sentences_only", "label_with_context"):
        a = [files[1][p][col] for p in both if files[2][p][col] and files[1][p][col]]
        b = [files[2][p][col] for p in both if files[2][p][col] and files[1][p][col]]
        bin_a = ["genuine" if x == "genuine_contradiction" else "not" for x in a]
        bin_b = ["genuine" if x == "genuine_contradiction" else "not" for x in b]
        rep[col] = {"n": len(a), "raw_agreement": sum(x == y for x, y in zip(a, b)) / max(1, len(a)),
                    "kappa_7way": _kappa(a, b), "kappa_genuine_vs_not": _kappa(bin_a, bin_b),
                    "agreed_labels_by_stratum": {}}
        for p in both:
            x, y = files[1][p][col], files[2][p][col]
            if x and x == y:
                st = key[p]["stratum"]
                rep[col]["agreed_labels_by_stratum"].setdefault(st, Counter())[x] += 1
    (pkg / "IMPORT_REPORT.json").write_text(json.dumps(rep, indent=1, default=dict))
    print(json.dumps(rep, indent=1, default=dict))
    return rep


def mechanism(edges_csv: Path, ctrl: Path, out: Path) -> None:
    """Correlational only: which questions show the larger contradiction-line effect."""
    edges = _edges(edges_csv)
    ctl = _load(ctrl, {"R4P_FO", "R4P_FO_NC"})
    per_q: dict = defaultdict(list)
    for e in edges:
        if e["first_direction_of_pair"] and e["question_uid"] in ctl:
            per_q[e["question_uid"]].append(e)
    feats = {}
    for q, es in per_q.items():
        v = ctl[q]
        if len(v) < 2 or " CONTRADICTS " not in v["R4P_FO"]["evidence"]["text"]:
            continue
        cats = Counter(e["auto_category"] for e in es)
        feats[q] = {"dataset": es[0]["dataset"], "max_conf": max(e["nli_confidence"] or 0 for e in es),
                    "dominant_category": cats.most_common(1)[0][0], "any_same_passage": any(e["same_passage"] for e in es),
                    "em_on": float(_state(v["R4P_FO"]) == "C"), "em_off": float(_state(v["R4P_FO_NC"]) == "C"),
                    "ab_on": float(_state(v["R4P_FO"]) == "A"), "ab_off": float(_state(v["R4P_FO_NC"]) == "A")}
    rows = []
    groupers = {"max_conf": lambda f: "conf>=0.99" if f["max_conf"] >= 0.99 else "conf<0.99",
                "dominant_category": lambda f: f["dominant_category"],
                "any_same_passage": lambda f: f"same_passage={f['any_same_passage']}"}
    for ds in sorted({f["dataset"] for f in feats.values()}):
        for gname, g in groupers.items():
            groups = defaultdict(list)
            for q, f in feats.items():
                if f["dataset"] == ds:
                    groups[g(f)].append(q)
            for lev, qs in sorted(groups.items()):
                em = paired_bootstrap({q: feats[q]["em_off"] for q in qs}, {q: feats[q]["em_on"] for q in qs})
                ab = paired_bootstrap({q: feats[q]["ab_off"] for q in qs}, {q: feats[q]["ab_on"] for q in qs})
                rows.append({"dataset": ds, "grouping": gname, "level": lev, "n": len(qs), "d_em": em["delta"],
                             "d_em_ci": json.dumps(em["ci"]), "d_abst": ab["delta"], "d_abst_ci": json.dumps(ab["ci"])})
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "contradiction_mechanism_correlational.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['dataset'][:6]} {r['grouping']:18s} {r['level']:36s} n={r['n']:5d} dEM={r['d_em']:+.3f} {r['d_em_ci']} dAbst={r['d_abst']:+.3f}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "package":
        package(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    elif cmd == "import":
        import_pkg(Path(sys.argv[2]), Path(sys.argv[3]))
    elif cmd == "mechanism":
        mechanism(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
