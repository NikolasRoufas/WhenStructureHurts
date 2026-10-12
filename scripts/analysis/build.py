"""Reproducible analysis of the GPU-pilot campaign: reads saved predictions + manifests only.

    python scripts/analysis/build.py --runs research_outputs/experiments/runs.json \
        --out research_outputs [--paper paper]

runs.json maps a label (e.g. "A_exp1", "C_exp2") to a run directory that contains
manifest.json, resolved config, predictions.jsonl(.gz). Every output table carries the run label,
and research_outputs/analysis/provenance.json holds the sha256 of every input file, so each
published number traces back to a run.

Statistics are the FROZEN procedure of docs/PILOT_PROTOCOL.md §7, taken from
wsh.evaluation (question-level paired percentile bootstrap, 2000 resamples, seed 0; R2 seeds
averaged within question; protocols, datasets and edge strata never pooled). Additions here are
labelled secondary/exploratory: the exact McNemar test on discordant pairs (binary per-question
EM only), the paired standardised effect d_z, per-hop / per-type breakdowns and an automatic
error taxonomy. Nothing is selected on outcomes.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

from wsh.evaluation.reporting import (PRIMARY_DATASETS, cond_label, consistency, contrasts, exp2_sensitivity,
                                      exp3_attribution, primary_metric, protocol_accounting, summarize_group)
from wsh.evaluation.statistics import bootstrap_ci, by_question, paired_bootstrap
from wsh.text import normalize_answer

REPS = ["R0", "R1", "R2", "R3", "R4", "R4P", "R5"]
PRIMARY = [("R0", "R1"), ("R1", "R5"), ("R5", "R4")]
SECONDARY = [("R1", "R2"), ("R5", "R3"), ("R4", "R4P")]
DS_NAME = {"musique": "MuSiQue", "2wikimultihopqa": "2Wiki", "hotpotqa": "HotpotQA", "hover": "HoVer", "fever": "FEVER"}
DS_ORDER = ["musique", "2wikimultihopqa", "hotpotqa", "hover", "fever"]


# ----------------------------------------------------------------------------- loading

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_run(d: Path) -> tuple[list[dict], dict, dict]:
    p = d / "predictions.jsonl"
    opener = open
    if not p.exists():
        p, opener = d / "predictions.jsonl.gz", gzip.open
    recs = {}
    with opener(p, "rt") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            recs[r["record_key"]] = r  # last write wins = resume-safe, same as wsh.reporting
    man = json.loads((d / "manifest.json").read_text())
    prov = {"run_dir": d.name, "experiment": man["experiment"], "stage": man["stage"], "config_hash": man["config_hash"],
            "git_commit": man.get("git_commit"), "status": man.get("status"), "n_records": len(recs),
            "files": {f.name: sha256(f) for f in sorted(d.iterdir()) if f.is_file()}}
    return list(recs.values()), man, prov


# ----------------------------------------------------------------------------- helpers

def setting(c: dict) -> str:
    if c.get("protocol") == "A":
        return "A"
    if c.get("protocol") == "B":
        return f"B {c['budget'].replace('content:', '')}x {c['policy']}"
    return "-"


def em_map(rs: list[dict], metric: str) -> dict[str, float]:
    return by_question([r for r in rs if not r.get("unavailable")], lambda r: r["eval"].get(metric))


def mcnemar_exact(n01: int, n10: int) -> float | None:
    """Two-sided exact McNemar (binomial on discordant pairs)."""
    n = n01 + n10
    if n == 0:
        return None
    k = min(n01, n10)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def paired_extra(a: dict[str, float], b: dict[str, float]) -> dict:
    qs = sorted(set(a) & set(b))
    d = [b[q] - a[q] for q in qs]
    out = {"d_z": None, "mcnemar_p": None, "binary": False}
    if len(d) > 1 and st.pstdev(d) > 0:
        out["d_z"] = (sum(d) / len(d)) / st.stdev(d)
    if all(a[q] in (0.0, 1.0) and b[q] in (0.0, 1.0) for q in qs):
        out["binary"] = True
        out["mcnemar_p"] = mcnemar_exact(sum(x > 0 for x in d), sum(x < 0 for x in d))
    return out


def fmt(x, nd=3):
    if x is None:
        return "--"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in r.items()})


def latex_table(path: Path, header: list[str], rows: list[list[str]], caption: str, label: str, colspec: str,
                size: str = "\\small", star: bool = False) -> None:
    env = "table*" if star else "table"
    lines = [f"\\begin{{{env}}}[t]", "\\centering", size, f"\\begin{{tabular}}{{{colspec}}}", "\\toprule",
             " & ".join(header) + " \\\\", "\\midrule"]
    for r in rows:
        lines.append("\\midrule" if r == ["MIDRULE"] else " & ".join(r) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", f"\\end{{{env}}}"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def ci_str(c, nd=3):
    return "--" if not c else f"[{c[0]:+.{nd}f}, {c[1]:+.{nd}f}]"


# ----------------------------------------------------------------------------- Exp1

def exp1_absolute(records: list[dict], run: str) -> list[dict]:
    rows = []
    g = defaultdict(list)
    for r in records:
        g[(r["dataset"], setting(r["condition"]), r["condition"]["representation"])].append(r)
    for (ds, s, rep), rs in sorted(g.items()):
        m = primary_metric(rs[0]["task"])
        summ = summarize_group(rs)
        vals = list(em_map(rs, m).values())
        prov = [r.get("info", {}).get("information", {}) for r in rs if not r.get("unavailable")]
        rows.append({"run": run, "dataset": ds, "setting": s, "representation": rep, "metric": m,
                     "n_questions": summ.get("n_questions"), "n_records": summ["n_records"],
                     "n_unavailable": summ["n_unavailable"], "score": summ.get(m), "score_ci": bootstrap_ci(vals),
                     "f1": summ.get("f1"), "coverage": summ.get("coverage"),
                     "evidence_tokens": summ.get("evidence_tokens_mean"), "input_tokens": summ.get("input_tokens_mean"),
                     "output_tokens": summ.get("output_tokens_mean"),
                     "overhead_tokens": st.mean([p["overhead_tokens"] for p in prov if "overhead_tokens" in p]) if prov else None,
                     "content_tokens": st.mean([p["content_tokens"] for p in prov if "content_tokens" in p]) if prov else None,
                     "answer_in_evidence": summ.get("answer_in_evidence"), "evidence_sufficient": summ.get("evidence_sufficient"),
                     "latency_s_mean": summ.get("latency_s_mean"), "cached_fraction": summ.get("cached_fraction"),
                     "failure_primary": summ.get("failure_primary"), "finish_reasons": summ.get("finish_reasons")})
    return rows


def exp1_contrasts(records: list[dict], stage: str, run: str) -> list[dict]:
    out = []
    by_ds = defaultdict(list)
    for r in records:
        by_ds[r["dataset"]].append(r)
    for c in contrasts(records, "exp1", stage):
        # rebuild the setting from the stratum label (protocol/budget/policy are never pooled)
        lab = dict(kv.split("=", 1) for kv in c["stratum"].split(",") if "=" in kv)
        s = "A" if lab.get("protocol") == "A" else f"B {lab.get('budget', '').replace('content:', '')}x {lab.get('policy')}"
        rs = [r for r in by_ds[c["dataset"]] if setting(r["condition"]) == s]
        edge = c["edge_stratum"]
        def sel(rep):
            xs = [r for r in rs if r["condition"]["representation"] == rep]
            if edge != "all":
                xs = [r for r in xs if f"edge_stratum={(r.get('info') or {}).get('question_edge_stratum')}" == edge]
            return em_map(xs, c["metric"])
        extra = paired_extra(sel(c["a"]), sel(c["b"]))
        out.append({"run": run, "dataset": c["dataset"], "setting": s, "edge_stratum": edge, "contrast": f"{c['b']}-{c['a']}",
                    "a": c["a"], "b": c["b"], "metric": c["metric"], "role": c["role"], "n_paired": c["n_paired"],
                    "n_only_a": c["n_only_a"], "n_only_b": c["n_only_b"], "delta": c["delta"], "ci": c["ci"],
                    "p_boot": c["p_boot"], "verdict": c["verdict"], "n_b_better": c.get("n_b_better"),
                    "n_a_better": c.get("n_a_better"), "n_tied": c.get("n_tied"),
                    "n_identical_evidence": c["n_identical_evidence"],
                    "informative_n": c["informative_pairs"]["n_paired"], "informative_delta": c["informative_pairs"]["delta"],
                    "informative_ci": c["informative_pairs"]["ci"], "coverage_delta": c["coverage_delta"]["delta"],
                    "coverage_ci": c["coverage_delta"]["ci"], "d_z": extra["d_z"], "mcnemar_p_secondary": extra["mcnemar_p"],
                    "confirmatory": c["confirmatory"]})
    return out


def exp1_subgroups(records: list[dict], run: str) -> list[dict]:
    """Exploratory: primary contrasts (Protocol A) within hop count (MuSiQue, HoVer) and
    question type (2Wiki, HotpotQA), as annotated by the datasets."""
    out = []
    for ds in DS_ORDER:
        rs = [r for r in records if r["dataset"] == ds and setting(r["condition"]) == "A"]
        if not rs:
            continue
        key = "hop_count" if ds in ("musique", "hover") else "question_type"
        m = primary_metric(rs[0]["task"])
        for val in sorted({str(r.get(key)) for r in rs}):
            sub = [r for r in rs if str(r.get(key)) == val]
            for a, b in PRIMARY:
                pa = em_map([r for r in sub if r["condition"]["representation"] == a], m)
                pb = em_map([r for r in sub if r["condition"]["representation"] == b], m)
                if not pa or not pb:
                    continue
                res = paired_bootstrap(pa, pb)
                out.append({"run": run, "dataset": ds, "subgroup": f"{key}={val}", "contrast": f"{b}-{a}", "metric": m,
                            "n_paired": res["n_paired"], "score_a": st.mean(pa.values()), "score_b": st.mean(pb.values()),
                            "delta": res["delta"], "ci": res["ci"], "verdict": res["verdict"]})
    return out


def error_taxonomy(records: list[dict], run: str) -> list[dict]:
    """Automatic, conservative classification of every non-correct record (none removed).
    missing_evidence: the gold answer string is absent from what was shown;
    generation_failure: unparseable/empty/overflow/abstained;
    evaluation_mismatch_candidate: wrong under EM but token F1 >= 0.5 (needs manual check);
    reasoning_error_evidence_present: answered, wrong, answer present in the evidence."""
    g = defaultdict(Counter)
    for r in records:
        if r.get("unavailable") or "eval" not in r:
            continue
        m = primary_metric(r["task"])
        if r["eval"].get(m) == 1:
            continue
        prim = r["failure"]["primary"]
        if not r["failure"]["answered"]:
            cat = "generation_failure" if prim != "abstained" else "abstained"
        elif r["eval"].get("answer_in_evidence") == 0:
            cat = "missing_evidence"
        elif (r["eval"].get("f1") or 0) >= 0.5:
            cat = "evaluation_mismatch_candidate"
        else:
            cat = "reasoning_error_evidence_present"
        g[(r["dataset"], setting(r["condition"]), r["condition"].get("representation") or r["condition"].get("system"))][cat] += 1
    return [{"run": run, "dataset": k[0], "setting": k[1], "condition": k[2], **dict(v), "n_incorrect": sum(v.values())}
            for k, v in sorted(g.items())]


def discordant_examples(records: list[dict], a: str, b: str, ds: str, s: str = "A", k: int = 6) -> list[dict]:
    """Questions where exactly one of the two representations is correct (Protocol A),
    with the evidence each saw and both outputs; deterministic order (by uid)."""
    by = defaultdict(dict)
    for r in records:
        c = r["condition"]
        if r["dataset"] == ds and setting(c) == s and c["representation"] in (a, b) and c.get("shuffle_seed") in (None, 0):
            by[r["question_uid"]][c["representation"]] = r
    out = []
    for q in sorted(by):
        d = by[q]
        if a in d and b in d and d[a]["eval"].get("em") != d[b]["eval"].get("em"):
            out.append({"question_uid": q, "question": d[a]["question"], "gold": d[a]["gold_answers"],
                        "edge_stratum": (d[b].get("info") or {}).get("question_edge_stratum"),
                        a: {"em": d[a]["eval"]["em"], "answer": (d[a].get("parsed") or {}).get("answer"),
                            "evidence": d[a]["evidence"]["text"], "failure": d[a]["failure"]["primary"]},
                        b: {"em": d[b]["eval"]["em"], "answer": (d[b].get("parsed") or {}).get("answer"),
                            "evidence": d[b]["evidence"]["text"], "failure": d[b]["failure"]["primary"]}})
    return out[:k] if k else out


# ----------------------------------------------------------------------------- Exp0 / Exp2 / Exp3

def exp0_tables(records: list[dict], stage: str, run: str) -> tuple[list[dict], list[dict]]:
    g = defaultdict(list)
    for r in records:
        g[(r["dataset"], r["condition"]["system"])].append(r)
    absr = []
    for (ds, sysn), rs in sorted(g.items()):
        m = primary_metric(rs[0]["task"])
        summ = summarize_group(rs)
        info = [r.get("info") or {} for r in rs]
        absr.append({"run": run, "dataset": ds, "system": sysn, "metric": m, "n_questions": summ.get("n_questions"),
                     "n_unavailable": summ["n_unavailable"], "score": summ.get(m),
                     "score_ci": bootstrap_ci(list(em_map(rs, m).values())), "f1": summ.get("f1"),
                     "coverage": summ.get("coverage"), "evidence_tokens": summ.get("evidence_tokens_mean"),
                     "input_tokens": summ.get("input_tokens_mean"), "latency_s_mean": summ.get("latency_s_mean"),
                     "support_coverage": summ.get("support_coverage"), "answer_in_evidence": summ.get("answer_in_evidence"),
                     "n_units_mean": st.mean([r["evidence"]["n_units"] for r in rs if "evidence" in r]) if any("evidence" in r for r in rs) else None,
                     "extraction_calls_mean": st.mean([i.get("n_extraction_calls", 0) for i in info]) if info else None,
                     "failure_primary": summ.get("failure_primary")})
    cons = []
    for c in contrasts(records, "exp0", stage):
        cons.append({"run": run, "dataset": c["dataset"], "contrast": f"{c['b']}-{c['a']}", "metric": c["metric"],
                     "n_paired": c["n_paired"], "delta": c["delta"], "ci": c["ci"], "p_boot": c["p_boot"],
                     "verdict": c["verdict"], "n_identical_evidence": c["n_identical_evidence"],
                     "coverage_delta": c["coverage_delta"]["delta"]})
    return absr, cons


def exp2_tables(records: list[dict], run: str) -> list[dict]:
    rows = []
    for s in exp2_sensitivity(records):
        m = "em" if s["dataset"] not in ("hover", "fever") else "verdict_acc"
        d = s.get(f"delta_{m}_label_preserved") or {}
        rows.append({"run": run, "dataset": s["dataset"], "representation": s["representation"], "perturbation": s["perturbation"],
                     "params": s["params"], "rate": s["rate"], "n_pairs": s["n_pairs"], "label_effects": s["label_effects"],
                     "n_label_preserved": s["n_label_preserved"], "n_answer_introduced": s["n_answer_introduced"],
                     "mean_k_affected": s["mean_k_affected"], "answer_changed_rate": s["answer_changed_rate"],
                     "abstention_rate": s["abstention_rate"], "abstention_rate_base": s["abstention_rate_base"],
                     "metric": m, "delta_label_preserved": d.get("delta"), "ci": d.get("ci"),
                     "n_paired_label_preserved": d.get("n_paired"), "verdict": d.get("verdict")})
    return rows


# ----------------------------------------------------------------------------- figures

def figures(exp1_abs: list[dict], exp2_rows: list[dict], outdirs: list[Path]) -> list[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 8, "font.family": "serif", "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42})
    made = []

    def save(fig, name):
        for d in outdirs:
            d.mkdir(parents=True, exist_ok=True)
            fig.savefig(d / f"{name}.pdf", bbox_inches="tight")
            fig.savefig(d / f"{name}.png", bbox_inches="tight", dpi=200)
        plt.close(fig)
        made.append(name)

    # Fig 2: Protocol A score by representation, per dataset, with 95% bootstrap CIs
    dss = [d for d in DS_ORDER if any(r["dataset"] == d and r["setting"] == "A" for r in exp1_abs)]
    if dss:
        fig, axes = plt.subplots(1, len(dss), figsize=(1.55 * len(dss) + 0.4, 1.9), sharey=False, squeeze=False)
        for ax, ds in zip(axes[0], dss):
            rows = {r["representation"]: r for r in exp1_abs if r["dataset"] == ds and r["setting"] == "A"}
            reps = [x for x in REPS if x in rows]
            ys = [rows[x]["score"] for x in reps]
            lo = [rows[x]["score"] - rows[x]["score_ci"][0] for x in reps]
            hi = [rows[x]["score_ci"][1] - rows[x]["score"] for x in reps]
            ax.errorbar(range(len(reps)), ys, yerr=[lo, hi], fmt="o", ms=3, capsize=2, color="#2b5d8a")
            ax.set_xticks(range(len(reps)), reps, rotation=0, fontsize=6.5)
            ax.set_title(DS_NAME[ds], fontsize=8)
            ax.set_ylabel("EM" if ds not in ("hover", "fever") else "verdict acc.", fontsize=7)
            ax.grid(axis="y", lw=0.3, alpha=0.5)
        fig.tight_layout()
        save(fig, "fig2_representations_protocolA")

    # Fig 3: score vs evidence tokens (Protocol A and B), primary datasets
    pds = [d for d in PRIMARY_DATASETS if any(r["dataset"] == d for r in exp1_abs)]
    if pds:
        fig, axes = plt.subplots(1, len(pds), figsize=(3.3 * len(pds), 2.3), squeeze=False)
        marks = {"A": "o", "B 1.0x shared": "s", "B 1.0x per_representation": "D", "B 0.5x shared": "^",
                 "B 0.5x per_representation": "v"}
        cols = dict(zip(REPS, ["#1b1b1b", "#2b5d8a", "#7fa7c9", "#b5651d", "#a3241e", "#e08c86", "#4f8a3a"]))
        for ax, ds in zip(axes[0], pds):
            for r in exp1_abs:
                if r["dataset"] != ds or r["setting"] not in marks:
                    continue
                ax.scatter(r["evidence_tokens"], r["score"], marker=marks[r["setting"]], s=14,
                           color=cols[r["representation"]], alpha=0.85, linewidths=0)
            ax.set_xlabel("mean evidence tokens shown")
            ax.set_ylabel("EM")
            ax.set_title(DS_NAME[ds], fontsize=8)
            ax.grid(lw=0.3, alpha=0.5)
        from matplotlib.lines import Line2D
        h1 = [Line2D([], [], color=cols[x], marker="o", ls="", ms=4, label=x) for x in REPS]
        h2 = [Line2D([], [], color="gray", marker=v, ls="", ms=4, label=k) for k, v in marks.items()]
        fig.legend(handles=h1 + h2, loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=6.5, frameon=False)
        fig.tight_layout()
        save(fig, "fig3_accuracy_vs_tokens")

    # Fig 4: Exp2 label-preserved change in score vs perturbation rate
    if exp2_rows:
        dss = [d for d in DS_ORDER if any(r["dataset"] == d for r in exp2_rows)]
        perts = sorted({(r["perturbation"], r["params"]) for r in exp2_rows})
        fig, axes = plt.subplots(len(dss), 2, figsize=(6.6, 1.45 * len(dss) + 0.5), squeeze=False, sharex=True)
        pal = ["#2b5d8a", "#a3241e", "#4f8a3a", "#b5651d", "#6b4c9a", "#1b1b1b", "#d4a017", "#7fa7c9"]
        for i, ds in enumerate(dss):
            for j, rep in enumerate(("R1", "R4")):
                ax = axes[i][j]
                for k, (P, params) in enumerate(perts):
                    pts = sorted((r["rate"], r["delta_label_preserved"], r["ci"]) for r in exp2_rows
                                 if r["dataset"] == ds and r["representation"] == rep and r["perturbation"] == P
                                 and r["params"] == params and r["delta_label_preserved"] is not None)
                    if not pts:
                        continue
                    lab = P + ("" if params in ("{}", "null") else " " + ",".join(f"{v}" for v in json.loads(params).values()))
                    xs = [0.0] + [p[0] for p in pts]
                    ys = [0.0] + [p[1] for p in pts]
                    ax.plot(xs, ys, marker="o", ms=2.5, lw=0.9, color=pal[k % len(pal)], label=lab)
                ax.axhline(0, color="gray", lw=0.4)
                ax.set_title(f"{DS_NAME[ds]} / {rep}", fontsize=7.5)
                ax.grid(lw=0.3, alpha=0.5)
                if j == 0:
                    ax.set_ylabel("Δ score")
        for ax in axes[-1]:
            ax.set_xlabel("perturbation rate")
        hs, ls = [], []
        for ax in axes.flat:
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in ls:
                    hs.append(h)
                    ls.append(l)
        fig.legend(hs, ls, loc="upper center", ncol=4, fontsize=6.5, frameon=False, bbox_to_anchor=(0.5, 1.04))
        fig.tight_layout()
        save(fig, "fig4_perturbation_sensitivity")
    return made


# ----------------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--paper")
    ap.add_argument("--figures-exp1", default=None, help="run label whose Exp1 results are plotted")
    ap.add_argument("--figures-exp2", default=None, help="run label whose Exp2 results are plotted")
    a = ap.parse_args()
    out = Path(a.out)
    runs = json.loads(Path(a.runs).read_text())
    base = Path(a.runs).parent
    prov, res = {}, {}
    for label, d in runs.items():
        recs, man, p = load_run((base / d).resolve() if not Path(d).is_absolute() else Path(d))
        prov[label] = p
        res[label] = (recs, man)
    an = out / "analysis"
    an.mkdir(parents=True, exist_ok=True)
    (an / "provenance.json").write_text(json.dumps(prov, indent=1))
    summary = {}
    fig_exp1, fig_exp2 = [], []
    for label, (recs, man) in res.items():
        exp, stage = man["experiment"], man["stage"]
        summary[label] = {"experiment": exp, "stage": stage, "n_records": len(recs),
                          "n_unavailable": sum(1 for r in recs if r.get("unavailable")),
                          "n_generation_error": sum(1 for r in recs if (r.get("generation") or {}).get("finish_reason") == "error"),
                          "n_pipeline_error": sum(1 for r in recs if "pipeline_error" in ((r.get("failure") or {}).get("flags") or [])),
                          "finish_reasons": dict(Counter((r.get("generation") or {}).get("finish_reason") for r in recs if r.get("generation"))),
                          "consistency": consistency(recs)["generator_settings_identical"],
                          "wall_clock_s": man.get("wall_clock_s"), "status": man.get("status"),
                          "unavailable_reasons": dict(Counter(r["unavailable"].split(":")[0] for r in recs if r.get("unavailable")))}
        if exp == "exp1":
            ab = exp1_absolute(recs, label)
            write_csv(an / f"{label}_absolute.csv", ab)
            if label == a.figures_exp1:
                fig_exp1 = ab
            write_csv(an / f"{label}_contrasts.csv", exp1_contrasts(recs, stage, label))
            write_csv(an / f"{label}_subgroups.csv", exp1_subgroups(recs, label))
            write_csv(an / f"{label}_protocol_accounting.csv", protocol_accounting(recs))
            write_csv(an / f"{label}_error_taxonomy.csv", error_taxonomy(recs, label))
            ex = {f"{ds}:{b}-{a}": discordant_examples(recs, a, b, ds, k=0)
                  for ds in DS_ORDER for a, b in PRIMARY if any(r["dataset"] == ds for r in recs)}
            (an / f"{label}_discordant_examples.json").write_text(json.dumps(ex, indent=1))
        elif exp == "exp0":
            ab, co = exp0_tables(recs, stage, label)
            write_csv(an / f"{label}_absolute.csv", ab)
            write_csv(an / f"{label}_contrasts.csv", co)
            write_csv(an / f"{label}_error_taxonomy.csv", error_taxonomy(recs, label))
        elif exp == "exp2":
            rows = exp2_tables(recs, label)
            write_csv(an / f"{label}_sensitivity.csv", rows)
            if label == a.figures_exp2:
                fig_exp2 = rows
        elif exp == "exp3":
            (an / f"{label}_attribution.json").write_text(json.dumps(exp3_attribution(recs), indent=1, default=str))
    (an / "run_summary.json").write_text(json.dumps(summary, indent=1))
    dirs = [out / "figures"] + ([Path(a.paper) / "figures"] if a.paper else [])
    summary["_figures"] = figures(fig_exp1, fig_exp2, dirs)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
