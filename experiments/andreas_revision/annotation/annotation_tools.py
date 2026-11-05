"""Experiment A (and the Experiment B label workflow): two-annotator validation, agreement, adjudication,
final labels and precision of predicted contradictions.

Works on any package in the v2 format (pairs_annotator1.csv / pairs_annotator2.csv + a key JSON mapping
pair_id -> {question_uid, dataset, ...}). Nothing here creates a label: every label must come from a named
human in the CSV files. Incomplete, invalid or unsigned files are refused (fail fast).

    PYTHONPATH=src python experiments/andreas_revision/annotation/annotation_tools.py validate   <pkg> <key.json>
    ... agreement  <pkg> <key.json> <out_dir>          # needs both files complete; writes adjudication package
    ... finalize   <pkg> <key.json> <adjudication.csv> <out_dir>   # adjudication.csv may be '-' if no disagreement
    ... precision  <final_labels.csv> <out_dir> [--population <population.csv>]

Primary label column: label_with_context (protocol §A); label_sentences_only is reported as secondary.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arlib import (CLASSES3, LABELS7, NOTE_TAGS, cluster_bootstrap, cohen_kappa, confusion, note_tag,  # noqa: E402
                   sha256, to3, wilson)

COLS = ["item", "pair_id", "fact_A_source_title", "fact_A", "fact_B_source_title", "fact_B",
        "label_sentences_only", "passage_A", "passage_B", "label_with_context", "notes", "annotator"]
LABEL_COLS = ("label_with_context", "label_sentences_only")
PRIMARY = "label_with_context"


class RefusedImport(SystemExit):
    pass


def read_pkg(pkg: Path, key: dict) -> dict[int, dict[str, dict]]:
    errors, files = [], {}
    for a in (1, 2):
        p = pkg / f"pairs_annotator{a}.csv"
        if not p.exists():
            raise RefusedImport(f"missing {p}")
        with open(p, newline="") as f:
            rd = csv.DictReader(f)
            if rd.fieldnames != COLS:
                errors.append(f"annotator{a}: columns {rd.fieldnames} != {COLS}")
                continue
            rows = list(rd)
        ids = [r["pair_id"] for r in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"annotator{a}: duplicate pair_id rows")
        if set(ids) != set(key):
            errors.append(f"annotator{a}: pair ids differ from the key ({len(set(ids) ^ set(key))} mismatched)")
        for r in rows:
            for c in LABEL_COLS:
                if r[c].strip() and r[c].strip() not in LABELS7:
                    errors.append(f"annotator{a} item {r['item']}: invalid {c} {r[c]!r}")
            if any(r[c].strip() for c in LABEL_COLS) and not r["annotator"].strip():
                errors.append(f"annotator{a} item {r['item']}: label without annotator id")
            if r["notes"].strip().startswith("[") and note_tag(r["notes"]) is None:
                errors.append(f"annotator{a} item {r['item']}: unknown notes tag (allowed: {NOTE_TAGS})")
        files[a] = {r["pair_id"]: r for r in rows}
    if errors:
        raise RefusedImport("import refused:\n" + "\n".join(errors[:50]))
    ids = [{r["annotator"].strip() for r in files[a].values() if r["annotator"].strip()} for a in (1, 2)]
    if ids[0] & ids[1]:
        raise RefusedImport(f"the two files share annotator id(s) {sorted(ids[0] & ids[1])}; labels must be independent")
    return files


def completeness(files: dict, key: dict) -> dict:
    out = {}
    for a in (1, 2):
        out[f"annotator{a}"] = {c: sum(bool(files[a][p][c].strip()) for p in key) for c in LABEL_COLS}
        out[f"annotator{a}"]["ids"] = sorted({r["annotator"].strip() for r in files[a].values() if r["annotator"].strip()})
    out["n_items"] = len(key)
    out["complete_primary"] = all(out[f"annotator{a}"][PRIMARY] == len(key) for a in (1, 2))
    return out


def cmd_validate(pkg: Path, key_p: Path) -> dict:
    key = json.loads(key_p.read_text())
    files = read_pkg(pkg, key)
    rep = completeness(files, key)
    print(json.dumps(rep, indent=1))
    return rep


def _agree_block(files: dict, key: dict, col: str) -> dict:
    ps = sorted(p for p in key if files[1][p][col].strip() and files[2][p][col].strip())
    a7 = [files[1][p][col].strip() for p in ps]
    b7 = [files[2][p][col].strip() for p in ps]
    a3, b3 = [to3(x) for x in a7], [to3(x) for x in b7]
    items = [{"q": key[p]["question_uid"], "ds": key[p].get("dataset", "_"), "a": x, "b": y}
             for p, x, y in zip(ps, a3, b3)]
    raw = lambda it: sum(i["a"] == i["b"] for i in it) / len(it) if it else None  # noqa: E731
    kap = lambda it: cohen_kappa([i["a"] for i in it], [i["b"] for i in it])  # noqa: E731
    clu, strat = (lambda i: i["q"]), (lambda i: i["ds"])
    return {"n": len(ps),
            "raw_agreement_3": raw(items), "raw_agreement_3_ci_cluster": cluster_bootstrap(items, clu, raw, strat),
            "kappa_3": kap(items), "kappa_3_ci_cluster": cluster_bootstrap(items, clu, kap, strat),
            "raw_agreement_7": sum(x == y for x, y in zip(a7, b7)) / len(ps) if ps else None,
            "kappa_7": cohen_kappa(a7, b7),
            "kappa_genuine_vs_not": cohen_kappa(["g" if x == "genuine" else "n" for x in a3],
                                                ["g" if x == "genuine" else "n" for x in b3]),
            "confusion_3 (rows annotator1, cols annotator2)": confusion(a3, b3, CLASSES3),
            "confusion_7": confusion(a7, b7, LABELS7),
            "marginals_3": {"annotator1": dict(Counter(a3)), "annotator2": dict(Counter(b3))},
            "by_dataset_raw_agreement_3": {ds: raw([i for i in items if i["ds"] == ds])
                                           for ds in sorted({i["ds"] for i in items})}}


def cmd_agreement(pkg: Path, key_p: Path, out: Path) -> dict:
    key = json.loads(key_p.read_text())
    files = read_pkg(pkg, key)
    comp = completeness(files, key)
    if not comp["complete_primary"]:
        raise RefusedImport(f"agreement refused: primary labels incomplete {comp}")
    rep = {"package": str(pkg), "key_sha256": sha256(key_p),
           "csv_sha256": {a: sha256(pkg / f"pairs_annotator{a}.csv") for a in (1, 2)}, "completeness": comp,
           "primary": _agree_block(files, key, PRIMARY), "secondary_sentences_only": _agree_block(files, key, "label_sentences_only"),
           "note": "CIs: percentile bootstrap resampling questions within dataset (2,000, seed 0)."}
    # adjudication package: every 3-class disagreement (required) and 'false' subtype disagreements (category only)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in sorted(key):
        x, y = files[1][p][PRIMARY].strip(), files[2][p][PRIMARY].strip()
        if to3(x) != to3(y):
            reason = "3-class disagreement (required)"
        elif x != y:
            reason = "subtype disagreement only (category analysis)"
        else:
            continue
        r = files[1][p]
        rows.append({"pair_id": p, "reason": reason, "fact_A_source_title": r["fact_A_source_title"], "fact_A": r["fact_A"],
                     "fact_B_source_title": r["fact_B_source_title"], "fact_B": r["fact_B"], "passage_A": r["passage_A"],
                     "passage_B": r["passage_B"], "label_annotator1": x, "notes_annotator1": files[1][p]["notes"],
                     "label_annotator2": y, "notes_annotator2": files[2][p]["notes"], "adjudicated_label": "",
                     "adjudicator": "", "rationale": ""})
    with open(out / "adjudication_package.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["pair_id", "reason", "adjudicated_label", "adjudicator", "rationale"])
        w.writeheader()
        w.writerows(rows)
    rep["n_adjudication_required"] = sum(r["reason"].startswith("3-class") for r in rows)
    rep["n_adjudication_subtype_only"] = sum(r["reason"].startswith("subtype") for r in rows)
    (out / "agreement_report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: rep["primary"][k] for k in ("n", "raw_agreement_3", "kappa_3", "kappa_3_ci_cluster")}, indent=1))
    return rep


def cmd_finalize(pkg: Path, key_p: Path, adj: str, out: Path) -> Path:
    key = json.loads(key_p.read_text())
    files = read_pkg(pkg, key)
    if not completeness(files, key)["complete_primary"]:
        raise RefusedImport("finalize refused: primary labels incomplete")
    adjud = {}
    if adj != "-":
        for r in csv.DictReader(open(adj, newline="")):
            lab = r["adjudicated_label"].strip()
            if lab:
                if lab not in LABELS7:
                    raise RefusedImport(f"adjudication {r['pair_id']}: invalid label {lab!r}")
                if not r["adjudicator"].strip():
                    raise RefusedImport(f"adjudication {r['pair_id']}: label without adjudicator id")
                adjud[r["pair_id"]] = (lab, r["adjudicator"].strip(), r.get("rationale", ""))
    rows, missing = [], []
    for p in sorted(key):
        x, y = files[1][p][PRIMARY].strip(), files[2][p][PRIMARY].strip()
        if to3(x) == to3(y):
            src = "agreed" if x == y else "agreed_3class"
            lab7 = adjud[p][0] if p in adjud else (x if x == y else "")   # subtype unresolved unless adjudicated
            if p in adjud and to3(adjud[p][0]) != to3(x):
                raise RefusedImport(f"{p}: adjudicated subtype changes an agreed 3-class label")
            lab3 = to3(x)
        elif p in adjud:
            src, lab7 = "adjudicated", adjud[p][0]
            lab3 = to3(lab7)
        else:
            missing.append(p)
            continue
        tags = {note_tag(files[1][p]["notes"]), note_tag(files[2][p]["notes"])} - {None}
        rows.append({"pair_id": p, "question_uid": key[p]["question_uid"], "dataset": key[p].get("dataset", ""),
                     "label3": lab3, "label7": lab7, "source": src, "label7_annotator1": x, "label7_annotator2": y,
                     "note_tags": "|".join(sorted(tags))})
    if missing:
        raise RefusedImport(f"finalize refused: {len(missing)} 3-class disagreements without an adjudicated label")
    out.mkdir(parents=True, exist_ok=True)
    fp = out / "final_labels.csv"
    with open(fp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{fp}: {len(rows)} final labels; {dict(Counter(r['label3'] for r in rows))}; sha256 {sha256(fp)}")
    return fp


def _props(rows: list[dict]) -> dict:
    n = len(rows)
    c = Counter(r["label3"] for r in rows)
    g, fa, am = c["genuine"], c["false"], c["ambiguous"]
    return {"n": n, "n_genuine": g, "n_false": fa, "n_ambiguous": am,
            "precision_strict": g / n if n else None, "precision_strict_wilson": wilson(g, n),
            "precision_excl_ambiguous": g / (g + fa) if g + fa else None, "precision_excl_ambiguous_wilson": wilson(g, g + fa),
            "bounds": [g / n, (g + am) / n] if n else None}


def cmd_precision(final: Path, out: Path, population: Path | None) -> dict:
    rows = list(csv.DictReader(open(final, newline="")))
    rep = {"final_labels": str(final), "final_labels_sha256": sha256(final),
           "denominators": "strict: all labelled pairs; excl_ambiguous: genuine+false; bounds: [genuine, genuine+ambiguous]/all",
           "sample": _props(rows),
           "sample_question_clustered_ci_strict": cluster_bootstrap(
               rows, lambda r: r["question_uid"], lambda it: sum(r["label3"] == "genuine" for r in it) / len(it),
               lambda r: r["dataset"]),
           "by_dataset": {ds: _props([r for r in rows if r["dataset"] == ds]) for ds in sorted({r["dataset"] for r in rows})}}
    if population is not None:
        pop = {r["pair_id"]: r for r in csv.DictReader(open(population, newline=""))}
        miss = [r["pair_id"] for r in rows if r["pair_id"] not in pop]
        if miss:
            raise RefusedImport(f"{len(miss)} labelled pairs are not in the population file")
        for r in rows:
            r["pi"] = float(pop[r["pair_id"]]["pi_hat"])
            r["stratum"] = pop[r["pair_id"]]["package_stratum"]
        if any(r["pi"] <= 0 for r in rows):
            raise RefusedImport("a sampled pair has estimated inclusion probability 0")
        rep["by_dataset_stratum"] = {f"{ds}:{st}": _props([r for r in rows if r["dataset"] == ds and r["stratum"] == st])
                                     for ds, st in sorted({(r["dataset"], r["stratum"]) for r in rows})}

        def hajek(it: list, cls: str = "genuine", excl_amb: bool = False) -> float | None:
            it = [r for r in it if not (excl_amb and r["label3"] == "ambiguous")]
            w = sum(1 / r["pi"] for r in it)
            return sum((r["label3"] == cls) / r["pi"] for r in it) / w if w else None

        n_pop = len(pop)
        n_cov = sum(1 for r in pop.values() if r["strata"])
        clu, strat = (lambda r: r["question_uid"]), (lambda r: r["dataset"])
        rep["design_weighted"] = {
            "target_population": f"rendered R4P_FO contradiction pairs in >= 1 sampling stratum: {n_cov} of {n_pop}",
            "excluded_pairs_without_stratum": n_pop - n_cov,
            "precision_strict": hajek(rows), "precision_strict_ci": cluster_bootstrap(rows, clu, hajek, strat),
            "precision_excl_ambiguous": hajek(rows, excl_amb=True),
            "precision_excl_ambiguous_ci": cluster_bootstrap(rows, clu, lambda it: hajek(it, excl_amb=True), strat),
            "share_false": hajek(rows, "false"), "share_ambiguous": hajek(rows, "ambiguous"),
            "per_dataset": {ds: {"precision_strict": hajek([r for r in rows if r["dataset"] == ds]),
                                 "ci": cluster_bootstrap([r for r in rows if r["dataset"] == ds], clu, hajek)}
                            for ds in sorted({r["dataset"] for r in rows})},
            "estimator": "Hajek, weights 1/pi_hat (pi_hat from 2,000 simulations of the package sampler); "
                         "CI: bootstrap resampling questions within dataset"}
    cats = Counter(r["label7"] or "subtype_unresolved" for r in rows)
    tags = Counter(t for r in rows for t in r["note_tags"].split("|") if t)
    rep["error_categories_label7"] = {k: {"n": v, "share": v / len(rows), "wilson": wilson(v, len(rows)),
                                          "describe_only": v < 20} for k, v in cats.most_common()}
    rep["note_tags"] = {k: {"n": v, "describe_only": v < 20} for k, v in tags.most_common()}
    out.mkdir(parents=True, exist_ok=True)
    (out / "precision_report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep["sample"], indent=1))
    return rep


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    v = sp.add_parser("validate"); v.add_argument("pkg", type=Path); v.add_argument("key", type=Path)  # noqa: E702
    g = sp.add_parser("agreement"); g.add_argument("pkg", type=Path); g.add_argument("key", type=Path); g.add_argument("out", type=Path)  # noqa: E702
    f = sp.add_parser("finalize"); f.add_argument("pkg", type=Path); f.add_argument("key", type=Path)  # noqa: E702
    f.add_argument("adjudication"); f.add_argument("out", type=Path)  # noqa: E702
    p = sp.add_parser("precision"); p.add_argument("final", type=Path); p.add_argument("out", type=Path)  # noqa: E702
    p.add_argument("--population", type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "validate":
        cmd_validate(a.pkg, a.key)
    elif a.cmd == "agreement":
        cmd_agreement(a.pkg, a.key, a.out)
    elif a.cmd == "finalize":
        cmd_finalize(a.pkg, a.key, a.adjudication, a.out)
    else:
        cmd_precision(a.final, a.out, a.population)


if __name__ == "__main__":
    main()
