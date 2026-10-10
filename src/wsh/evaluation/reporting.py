"""Aggregate reports, recomputable from predictions.jsonl alone (``wsh report <run_dir>``).

Pre-specified primary metric (docs/PILOT_PROTOCOL.md): question-level exact match (QA) /
verdict accuracy (verification), coverage-adjusted. Token F1 is secondary. Contrasts are
listed in PRESPECIFIED_CONTRASTS with a role; only role 'primary' on the primary datasets,
under Protocol A, at stage 'full' and n >= MIN_N_CONFIRMATORY forms the confirmatory family
(Holm-corrected). Everything else - including every pilot result - is exploratory.
Exp1 protocols A and B are never pooled: ``protocol`` is part of every stratum.
"""

from __future__ import annotations

import csv
import json
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ..text import normalize_answer
from .statistics import MIN_N_CONFIRMATORY, by_question, holm, mean, paired_bootstrap

METRICS = ["em", "f1", "verdict_acc", "citation_validity", "citation_precision", "citation_recall",
           "citation_recall_passage", "support_coverage", "content_recall", "answer_in_evidence",
           "hop_answer_coverage", "evidence_sufficient", "grounded_lexical", "grounded_nli"]

PRIMARY_DATASETS = ("musique", "2wikimultihopqa")
STRUCTURAL_REPS = {"R3", "R4", "R4P", "R5"}

# (factor, a, b, role)
PRESPECIFIED_CONTRASTS = {
    "exp0": [("system", "B0", "B1", "secondary"), ("system", "B1", "B2", "secondary"), ("system", "B2", "B3", "secondary"),
             ("system", "B2", "B4", "secondary"), ("system", "B1", "B4", "secondary")],
    "exp1": [("representation", "R0", "R1", "primary"), ("representation", "R1", "R5", "primary"),
             ("representation", "R5", "R4", "primary"), ("representation", "R1", "R2", "secondary"),
             ("representation", "R5", "R3", "secondary"), ("representation", "R4", "R4P", "secondary")],
    "exp3": [("component_condition", "oracle", c, "secondary") for c in ("C1", "C2", "C3", "C4")],
}


def primary_metric(task: str) -> str:
    return "em" if task == "qa" else "verdict_acc"


def cond_label(c: dict, drop: tuple[str, ...] = ()) -> str:
    def fmt(v):
        return json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else str(v)
    return ",".join(f"{k}={fmt(v)}" for k, v in sorted(c.items()) if v is not None and k not in drop and k != "accepted_statuses")


def load_records(run_dir: str | Path) -> list[dict]:
    recs = {}
    with open(Path(run_dir) / "predictions.jsonl") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            recs[r["record_key"]] = r
    return list(recs.values())


def summarize_group(rs: list[dict]) -> dict[str, Any]:
    avail = [r for r in rs if not r.get("unavailable")]
    out: dict[str, Any] = {"n_records": len(rs), "n_unavailable": len(rs) - len(avail),
                           "n_questions": len({r["question_uid"] for r in avail})}
    if not avail:
        out["unavailable_reasons"] = dict(Counter(r["unavailable"].split(":")[0] for r in rs))
        return out
    out["coverage"] = mean([float(r["failure"]["answered"]) for r in avail])
    for m in METRICS:
        qa = by_question(avail, lambda r, m=m: r["eval"].get(m))
        if qa:
            out[f"{m}"] = mean(list(qa.values()))  # coverage-adjusted (unanswered scored 0 by evaluator)
            cond = by_question([r for r in avail if r["failure"]["answered"]], lambda r, m=m: r["eval"].get(m))
            out[f"{m}_conditional"] = mean(list(cond.values()))
            out[f"{m}_n"] = len(qa)
    gens = [r["generation"] for r in avail if "generation" in r]
    if gens:
        out["input_tokens_mean"] = mean([g["input_tokens"] for g in gens])
        out["output_tokens_mean"] = mean([g["output_tokens"] for g in gens])
        out["latency_s_mean"] = mean([g["latency_s"] for g in gens])
        out["latency_s_median"] = st.median([g["latency_s"] for g in gens])
        out["cached_fraction"] = mean([float(g["cached"]) for g in gens])
        out["evidence_tokens_mean"] = mean([r["evidence"]["evidence_tokens"] for r in avail if "evidence" in r])
        out["prompt_overhead_tokens_mean"] = mean([r["prompt"]["overhead_tokens"] for r in avail if "prompt" in r])
        out["finish_reasons"] = dict(Counter(g["finish_reason"] for g in gens))
    out["failure_primary"] = dict(Counter(r["failure"]["primary"] for r in avail))
    out["failure_flags"] = dict(Counter(f for r in avail for f in r["failure"]["flags"]))
    return out


def _metric_by_q(rs: list[dict], metric: str) -> dict[str, float]:
    return by_question([r for r in rs if not r.get("unavailable")], lambda r: r["eval"].get(metric))


def _edge_stratum(r: dict) -> str | None:
    info = r.get("info") or {}
    return info.get("question_edge_stratum") or info.get("oracle_edge_stratum")


def contrasts(records: list[dict], experiment: str, stage: str = "smoke") -> list[dict]:
    """Paired question-level contrasts. Strata = every condition key except the contrasted
    factor (so Exp1 protocol/budget/selection are always separate). Contrasts involving
    structural representations are reported pooled AND per edge stratum (A/B/C/D)."""
    specs = PRESPECIFIED_CONTRASTS.get(experiment, [])
    out = []
    by_ds = defaultdict(list)
    for r in records:
        by_ds[r["dataset"]].append(r)
    for ds, rs in sorted(by_ds.items()):
        task = rs[0]["task"]
        for factor, a, b, role in specs:
            strata = defaultdict(lambda: defaultdict(list))
            per_edge = factor == "component_condition" or bool({a, b} & STRUCTURAL_REPS)
            for r in rs:
                c = r["condition"]
                if c.get(factor) not in (a, b):
                    continue
                # R2 shuffle seeds are averaged within question by by_question(); exp0/exp3
                # systems differ in representation by design, so it is not a stratum key.
                drop = (factor, "shuffle_seed") if factor == "representation" else (factor, "shuffle_seed", "representation")
                label = cond_label(c, drop=drop)
                strata[(label, "all")][c[factor]].append(r)
                if per_edge:
                    strata[(label, f"edge_stratum={_edge_stratum(r)}")][c[factor]].append(r)
            for (stratum, edge), groups in sorted(strata.items()):
                if a not in groups or b not in groups:
                    continue
                for metric in (primary_metric(task), "f1" if task == "qa" else None):
                    if metric is None:
                        continue
                    res = paired_bootstrap(_metric_by_q(groups[a], metric), _metric_by_q(groups[b], metric))
                    ident = _identical_evidence_questions(groups[a], groups[b])
                    res["n_identical_evidence"] = len(ident)
                    # secondary, pre-specified (PILOT_PROTOCOL §7): the same contrast on pairs whose
                    # evidence differs. Selection uses inputs only, never outcomes.
                    ma, mb = _metric_by_q(groups[a], metric), _metric_by_q(groups[b], metric)
                    inf = paired_bootstrap({q: v for q, v in ma.items() if q not in ident},
                                           {q: v for q, v in mb.items() if q not in ident})
                    res["informative_pairs"] = {k: inf.get(k) for k in ("n_paired", "delta", "ci", "verdict")}
                    # format/generation failures can drive an EM difference: report the paired
                    # difference in coverage (answered rate) next to every contrast
                    ans = lambda rs: by_question([r for r in rs if not r.get("unavailable")],  # noqa: E731
                                                 lambda r: float(r["failure"]["answered"]))
                    cov = paired_bootstrap(ans(groups[a]), ans(groups[b]))
                    res["coverage_delta"] = {k: cov.get(k) for k in ("delta", "ci")}
                    protocol = (groups[a][0]["condition"].get("protocol"))
                    confirm = (role == "primary" and edge == "all" and ds in PRIMARY_DATASETS and protocol in ("A", None)
                               and metric == primary_metric(task) and stage == "full" and res["n_paired"] >= MIN_N_CONFIRMATORY)
                    out.append({"dataset": ds, "stratum": stratum, "edge_stratum": edge, "factor": factor, "a": a, "b": b,
                                "metric": metric, "role": role, "primary_metric": metric == primary_metric(task),
                                "confirmatory": confirm, **res})
    pv = holm({f"{i}": c["p_boot"] for i, c in enumerate(out) if c["confirmatory"]})
    for i, c in enumerate(out):
        c["p_holm"] = pv.get(f"{i}")
    return out


def _identical_evidence_questions(ra: list[dict], rb: list[dict]) -> set[str]:
    """Questions whose two conditions showed byte-identical evidence in every record (e.g.
    R5 = R1 when the graph order equals the context order, R4 = R5 without edges). Their
    difference can only be 0, so they dilute the contrast."""
    ta, tb = defaultdict(set), defaultdict(set)
    for r in ra:
        if "evidence" in r:
            ta[r["question_uid"]].add(r["evidence"]["text"])
    for r in rb:
        if "evidence" in r:
            tb[r["question_uid"]].add(r["evidence"]["text"])
    return {q for q in ta.keys() & tb.keys() if len(ta[q]) == 1 and ta[q] == tb[q]}


def protocol_accounting(records: list[dict]) -> list[dict]:
    """Exp1: per (dataset, condition) what evidence was actually shown and what it cost."""
    groups = defaultdict(list)
    for r in records:
        if r.get("unavailable") or "info" not in r or "information" not in (r.get("info") or {}):
            continue
        groups[(r["dataset"], cond_label(r["condition"]))].append(r)
    out = []
    for (ds, label), rs in sorted(groups.items()):
        inf = [r["info"]["information"] for r in rs]
        acc = [r["info"].get("budget_accounting") for r in rs if r["info"].get("budget_accounting")]
        row = {"dataset": ds, "condition": label, "n": len(rs),
               "facts_shown": mean([i["n_facts"] for i in inf]),
               "content_tokens": mean([i["content_tokens"] for i in inf]),
               "overhead_tokens": mean([i["overhead_tokens"] for i in inf]),
               "evidence_tokens": mean([i["evidence_tokens"] for i in inf]),
               "added_information": sorted({x for i in inf for x in i["added_information"]}),
               "context_dependent_facts": mean([len(i["context_dependent_facts"]) for i in inf]),
               "evidence_sufficient": mean([r["eval"]["evidence_sufficient"] for r in rs if r["eval"].get("evidence_sufficient") is not None]),
               "answer_in_evidence": mean([r["eval"]["answer_in_evidence"] for r in rs if r["eval"].get("answer_in_evidence") is not None]),
               "latency_s": mean([r["generation"]["latency_s"] for r in rs if "generation" in r])}
        if acc:
            row.update({"budget": mean([a["budget"] for a in acc]),
                        "facts_kept_frac": mean([a["n_facts_kept"] / a["n_facts_total"] for a in acc if a["n_facts_total"]]),
                        "truncated_frac": mean([float(a["truncated"]) for a in acc]),
                        "required_dropped": mean([a["required_facts_dropped"] for a in acc]),
                        "answer_bearing_dropped": mean([a["answer_bearing_facts_dropped"] for a in acc]),
                        "required_fit_budget_frac": mean([float(a["required_facts_fit_budget"]) for a in acc
                                                          if a["required_facts_fit_budget"] is not None]),
                        "selection_uses_gold_labels": any(a.get("selection_uses_gold_labels") for a in acc)})
        out.append(row)
    return out


def consistency(records: list[dict]) -> dict:
    """Paired conditions must share generator settings; any difference is flagged."""
    sigs = Counter()
    for r in records:
        if "generation" in r:
            sigs[json.dumps({"model": r["model_id"], "rev": r["model_revision"], "prompt": r["prompt_version"],
                             "decoding": r["generation"].get("decoding")}, sort_keys=True)] += 1
    return {"generator_settings_identical": len(sigs) <= 1, "n_distinct_settings": len(sigs),
            "settings": [{"signature": json.loads(k), "n_records": v} for k, v in sigs.items()]}


def exp2_sensitivity(records: list[dict]) -> list[dict]:
    """Per (dataset, representation, perturbation, params, pseed, rate>0): change vs the same
    question's rate-0 record. Accuracy deltas are reported only for label-preserving cases;
    for not_guaranteed/answer_removed cases, agreement with the unperturbed answer and the
    abstention rate are reported instead."""
    base: dict[tuple, dict] = {}
    groups: dict[tuple, list[tuple[dict, dict]]] = defaultdict(list)
    for r in records:
        if r.get("unavailable") or "eval" not in r:
            continue
        c = r["condition"]
        k = (r["dataset"], c["representation"], c["perturbation"], json.dumps(c["params"], sort_keys=True), c["pseed"])
        if c["rate"] == 0:
            base[k + (r["question_uid"],)] = r
    for r in records:
        if r.get("unavailable") or "eval" not in r or r["condition"]["rate"] == 0:
            continue
        c = r["condition"]
        k = (r["dataset"], c["representation"], c["perturbation"], json.dumps(c["params"], sort_keys=True), c["pseed"])
        b0 = base.get(k + (r["question_uid"],))
        if b0:
            groups[k + (c["rate"],)].append((b0, r))
    out = []
    for k, pairs in sorted(groups.items(), key=lambda x: str(x[0])):
        ds, rep, P, params, pseed, rate = k
        task = pairs[0][1]["task"]
        m = primary_metric(task)
        eff = Counter(p[1]["info"]["intervention"]["label_effect"] for p in pairs)
        pres = [(a, b) for a, b in pairs if b["info"]["intervention"]["label_effect"] == "preserved"
                and not b["info"]["intervention"].get("answer_introduced")]
        ans = lambda r: normalize_answer((r.get("parsed") or {}).get("answer") or "")  # noqa: E731
        row = {"dataset": ds, "representation": rep, "perturbation": P, "params": params, "pseed": pseed, "rate": rate,
               "n_pairs": len(pairs), "label_effects": dict(eff),
               "mean_k_affected": mean([p[1]["info"]["intervention"]["n_affected"] for p in pairs]),
               "answer_changed_rate": mean([float(ans(a) != ans(b)) for a, b in pairs]),
               "abstention_rate": mean([float(b["eval"].get("abstained", False)) for _, b in pairs]),
               "abstention_rate_base": mean([float(a["eval"].get("abstained", False)) for a, _ in pairs]),
               "n_label_preserved": len(pres),
               "n_answer_introduced": sum(bool(b["info"]["intervention"].get("answer_introduced")) for _, b in pairs)}
        if pres:
            pa = {a["question_uid"]: a["eval"][m] for a, _ in pres}
            pb = {b["question_uid"]: b["eval"][m] for _, b in pres}
            row[f"delta_{m}_label_preserved"] = paired_bootstrap(pa, pb)
        out.append(row)
    return out


def exp3_attribution(records: list[dict]) -> dict:
    """Classify each (question, condition) relative to the oracle: component evidence loss vs
    generation failure given preserved evidence."""
    by_q = defaultdict(dict)
    for r in records:
        if r.get("unavailable") or "eval" not in r:
            continue
        by_q[r["question_uid"]][r["condition"]["component_condition"]] = r
    out = defaultdict(Counter)
    for q, d in by_q.items():
        o = d.get("oracle")
        if not o:
            continue
        m = primary_metric(o["task"])
        stratum = _edge_stratum(o)
        for cond0, r in d.items():
            if cond0 == "oracle":
                continue
            cond = f"{cond0} | edge_stratum={stratum}"  # strata A/B/C are never pooled here
            lost = any((r["eval"].get(k) is not None and o["eval"].get(k) is not None and r["eval"][k] < o["eval"][k])
                       for k in ("answer_in_evidence", "hop_answer_coverage", "content_recall"))
            if not r["failure"]["answered"]:
                out[cond]["generation_format_failure"] += 1
            elif r["eval"][m] >= o["eval"][m]:
                out[cond]["no_degradation"] += 1
            elif lost:
                out[cond]["degraded_with_evidence_loss(component)"] += 1
            else:
                out[cond]["degraded_with_evidence_preserved(generation/structure)"] += 1
    dep = defaultdict(list)
    for d in by_q.values():
        r = d.get("C2")
        if r and "dep_gold_circularity" in (r.get("info") or {}):
            i = r["info"]
            dep[f"{r['dataset']} | gold={i['dep_gold_circularity']}"].append(i)
    c2 = {k: ({"n": len(v), "reported": False, "reason": "gold edges share the predictor's heuristic"}
              if any(i.get("dep_prf_suppressed") for i in v) else
              {"n": len(v), "reported": True, "dep_precision": mean([i["dep_precision"] for i in v if i["dep_precision"] is not None]),
               "dep_recall": mean([i["dep_recall"] for i in v if i["dep_recall"] is not None]),
               "caveat": None if k.endswith("none:human_verified") else "gold edges are automatically derived, not verified"})
          for k, v in sorted(dep.items())}
    return {**{k: dict(v) for k, v in out.items()}, "C2_depends_on_agreement_passage_level": c2}


def write_reports(ctx) -> dict:
    run_dir = Path(ctx.dir)
    records = load_records(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text())
    exp = manifest["experiment"]
    groups = defaultdict(list)
    for r in records:
        groups[(r["dataset"], cond_label(r["condition"]))].append(r)
    summary = {f"{ds} | {c}": summarize_group(rs) for (ds, c), rs in sorted(groups.items())}
    result: dict[str, Any] = {"experiment": exp, "stage": manifest["stage"], "n_records": len(records),
                              "groups": summary}
    result["consistency"] = consistency(records)
    if exp in PRESPECIFIED_CONTRASTS:
        result["paired_contrasts"] = contrasts(records, exp, manifest["stage"])
    if exp == "exp1":
        result["protocol_accounting"] = protocol_accounting(records)
    if exp == "exp2":
        result["sensitivity"] = exp2_sensitivity(records)
    if exp == "exp3":
        result["attribution"] = exp3_attribution(records)
    (run_dir / "metrics.json").write_text(json.dumps(result, indent=2, default=str))
    cols = ["group", "n_records", "n_unavailable", "n_questions", "coverage", "em", "f1", "verdict_acc",
            "citation_validity", "citation_recall", "support_coverage", "content_recall", "evidence_sufficient", "grounded_nli",
            "input_tokens_mean", "output_tokens_mean", "evidence_tokens_mean", "latency_s_mean"]
    with open(run_dir / "summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for g, s in summary.items():
            w.writerow({"group": g, **s})
    (run_dir / "report.md").write_text(render_markdown(result, manifest))
    return result


def _informative(c: dict) -> str:
    i = c.get("informative_pairs") or {}
    if not i.get("n_paired"):
        return "-"
    ci = f"[{i['ci'][0]:.3f}, {i['ci'][1]:.3f}]" if i.get("ci") else "-"
    return f"{i['n_paired']}, {_fmt(i.get('delta'))} {ci}"


def _fmt(x) -> str:
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.3f}"
    return str(x)


def render_markdown(result: dict, manifest: dict) -> str:
    L = [f"# {result['experiment']} - run {manifest['run_id']}", ""]
    if manifest["stage"] == "smoke":
        L += ["> **SMOKE TEST - software/pipeline validation only.** Sample sizes are tiny and the model is a",
              "> 0.5B development model. Nothing here is evidence for or against any hypothesis.", ""]
    elif manifest["stage"] in ("pilot", "gpu_pilot"):
        L += [f"> **{manifest['stage'].upper()} - exploratory.** Estimates effect sizes and variance for planning; "
              "no confirmatory claims.", ""]
    if not result.get("consistency", {}).get("generator_settings_identical", True):
        L += ["> **WARNING: generator settings differ between records of this run** (see metrics.json "
              "'consistency'); paired contrasts may be confounded.", ""]
    L += [f"- status: {manifest.get('status')}", f"- model: {manifest['model']}",
          f"- code: git={manifest.get('git_commit')} tree={manifest.get('source_tree_sha256', '')[:12]}",
          f"- wall clock: {manifest.get('wall_clock_s')} s; uncached generations: {manifest.get('n_generated_uncached')}",
          f"- records: {result['n_records']}", "",
          "## Per-condition summary (coverage-adjusted, question-level means; conditional in parentheses)", "",
          "| dataset | condition | n_q | unavail | coverage | EM | F1 | verdict | cit.valid | cit.recall | support cov | sufficient | grounded NLI | ev.tok | lat s | top failure |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for g, s in result["groups"].items():
        top = max(s.get("failure_primary", {"-": 0}).items(), key=lambda x: x[1])[0] if s.get("failure_primary") else "-"
        def cc(m):
            return f"{_fmt(s.get(m))} ({_fmt(s.get(m + '_conditional'))})" if m in s else "-"
        L.append(f"| {g} | {s.get('n_questions')} | {s.get('n_unavailable')} | {_fmt(s.get('coverage'))} | {cc('em')} | "
                 f"{cc('f1')} | {cc('verdict_acc')} | {_fmt(s.get('citation_validity'))} | {_fmt(s.get('citation_recall'))} | "
                 f"{_fmt(s.get('support_coverage'))} | {_fmt(s.get('evidence_sufficient'))} | {_fmt(s.get('grounded_nli'))} | {_fmt(s.get('evidence_tokens_mean'))} | "
                 f"{_fmt(s.get('latency_s_mean'))} | {top} |")
    if result.get("paired_contrasts"):
        L += ["", f"## Pre-specified paired contrasts (b - a, question-level bootstrap, 2000 resamples; n < "
              f"{MIN_N_CONFIRMATORY} => exploratory)", "",
              "| dataset | stratum | edges | a | b | role | metric | n | identical ev. | delta | 95% CI | verdict | "
              "informative pairs: n, delta [CI] | Δcoverage | confirmatory |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for c in result["paired_contrasts"]:
            ci = f"[{c['ci'][0]:.3f}, {c['ci'][1]:.3f}]" if c.get("ci") else "-"
            L.append(f"| {c['dataset']} | {c['stratum']} | {c['edge_stratum']} | {c['a']} | {c['b']} | {c['role']} | "
                     f"{c['metric']} | {c['n_paired']} | {c.get('n_identical_evidence')} | {_fmt(c.get('delta'))} | {ci} | {c.get('verdict')} | "
                     f"{_informative(c)} | {_fmt((c.get('coverage_delta') or {}).get('delta'))} | "
                     f"{'yes (Holm p=' + _fmt(c.get('p_holm')) + ')' if c['confirmatory'] else 'no (exploratory)'} |")
    if result.get("protocol_accounting"):
        L += ["", "## Evidence accounting (Exp1; protocols reported separately)", "",
              "| dataset | condition | n | facts | content tok | overhead tok | evidence tok | added information | "
              "sufficient | answer in ev. | kept frac | truncated | required dropped | answer-bearing dropped | lat s |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for a in result["protocol_accounting"]:
            L.append(f"| {a['dataset']} | {a['condition']} | {a['n']} | {_fmt(a['facts_shown'])} | {_fmt(a['content_tokens'])} | "
                     f"{_fmt(a['overhead_tokens'])} | {_fmt(a['evidence_tokens'])} | {', '.join(a['added_information']) or '-'} | "
                     f"{_fmt(a['evidence_sufficient'])} | {_fmt(a['answer_in_evidence'])} | {_fmt(a.get('facts_kept_frac'))} | "
                     f"{_fmt(a.get('truncated_frac'))} | {_fmt(a.get('required_dropped'))} | "
                     f"{_fmt(a.get('answer_bearing_dropped'))} | {_fmt(a['latency_s'])} |")
    if result.get("sensitivity"):
        L += ["", "## Perturbation sensitivity (vs. each question's unperturbed record)", "",
              "| dataset | rep | P | params | rate | n | mean k | label effects | answer changed | abstain (base->pert) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for s in result["sensitivity"]:
            L.append(f"| {s['dataset']} | {s['representation']} | {s['perturbation']} | {s['params']} | {s['rate']} | "
                     f"{s['n_pairs']} | {_fmt(s['mean_k_affected'])} | {s['label_effects']} | {_fmt(s['answer_changed_rate'])} | "
                     f"{_fmt(s['abstention_rate_base'])}->{_fmt(s['abstention_rate'])} |")
    if result.get("attribution"):
        L += ["", "## Component attribution (relative to oracle)", "", "```", json.dumps(result["attribution"], indent=2), "```"]
    L += ["", "Unavailable conditions are excluded from metric denominators and counted in 'unavail'.",
          "All numbers can be recomputed with `wsh report <run_dir>`."]
    return "\n".join(L) + "\n"
