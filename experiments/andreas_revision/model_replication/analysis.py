"""Experiment C analysis: third reader (OLMo-2) on confirm2_v1, R4P_FO vs R4P_FO_NC (protocol §C and §7).

The EM primary family is computed by scripts/revision/confirm2_analysis.py, unchanged, on the same run. This
script adds the lenient-match primary family (§7 amendment, Holm over the two datasets), the secondary metrics,
the full 3x3 transition tables, integrity checks against the Qwen confirm2 run, and the same-question comparison
with Qwen. Differences are R4P_FO - R4P_FO_NC (lines on minus lines off).

    PYTHONPATH=src python experiments/andreas_revision/model_replication/analysis.py <olmo_run> <qwen_confirm2_run> <out_dir>
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arlib import holm, lenient, load_records, n_contra_lines, paired_bootstrap_strat, sha256, state, transitions  # noqa: E402

OFF, ON = "R4P_FO_NC", "R4P_FO"


def lstate(r: dict) -> str:
    """Lenient-match analogue of state(): C if lenient match, W if answered otherwise, A if abstained/error."""
    s = state(r)
    return "A" if s == "A" else ("C" if lenient(r) == 1 else "W")


def metrics(recs: dict, qs: list) -> dict:
    """Per-condition rates over questions qs (each question counted once per condition)."""
    out = {}
    for c in (OFF, ON):
        st = [state(recs[q][c]) for q in qs]
        n = len(qs)
        out[c] = {"n": n, "em": st.count("C") / n, "lenient": sum(lenient(recs[q][c]) for q in qs) / n,
                  "coverage": 1 - st.count("A") / n, "abstention": st.count("A") / n, "wrong": st.count("W") / n,
                  "hit_max_new_tokens": sum(recs[q][c]["generation"]["finish_reason"] == "length" for q in qs),
                  "generation_errors": sum(bool(recs[q][c]["generation"].get("error")) for q in qs)}
    return out


def contrasts(recs: dict, qs: list) -> dict:
    f = {"em": lambda r: float(state(r) == "C"), "lenient": lenient, "abstention": lambda r: float(state(r) == "A"),
         "wrong": lambda r: float(state(r) == "W")}
    res = {m: paired_bootstrap_strat({q: g(recs[q][OFF]) for q in qs}, {q: g(recs[q][ON]) for q in qs}) for m, g in f.items()}
    both = [q for q in qs if state(recs[q][OFF]) != "A" and state(recs[q][ON]) != "A"]
    res["em_given_both_answered"] = paired_bootstrap_strat({q: float(state(recs[q][OFF]) == "C") for q in both},
                                                           {q: float(state(recs[q][ON]) == "C") for q in both})
    res["transitions_em (off->on)"] = transitions({q: state(recs[q][OFF]) for q in qs}, {q: state(recs[q][ON]) for q in qs})
    res["transitions_lenient (off->on)"] = transitions({q: lstate(recs[q][OFF]) for q in qs}, {q: lstate(recs[q][ON]) for q in qs})
    return res


def main(olmo_run: Path, qwen_run: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    olmo, qwen = load_records(olmo_run, {OFF, ON}), load_records(qwen_run, {OFF, ON})
    man = json.loads((olmo_run / "manifest.json").read_text())
    rep: dict = {"olmo_run": str(olmo_run), "olmo_predictions_sha256": sha256(olmo_run / "predictions.jsonl"),
                 "qwen_run": str(qwen_run), "qwen_predictions_sha256": sha256(qwen_run / "predictions.jsonl"),
                 "manifest_status": man.get("status"), "model": man.get("loaded_models"),
                 "wall_clock_s": man.get("wall_clock_s"), "n_generated_uncached": man.get("n_generated_uncached"),
                 "datasets": {}}
    rows, p_len, p_em = [], {}, {}
    for ds in sorted({d for d, _ in olmo}):
        qs_all = sorted(k for k in olmo if k[0] == ds)
        incomplete = [k for k in qs_all if set(olmo[k]) != {OFF, ON}]
        if incomplete:
            raise SystemExit(f"{ds}: {len(incomplete)} questions miss a condition; refusing to analyse a partial run")
        k_lines = {k: n_contra_lines(olmo[k][ON]["evidence"]["text"]) for k in qs_all}
        ident = {k: olmo[k][ON]["prompt"]["user"] == olmo[k][OFF]["prompt"]["user"] for k in qs_all}
        assert all((k_lines[k] == 0) == ident[k] for k in qs_all), "prompts identical exactly when no CONTRADICTS line"
        same_as_qwen = {c: sum(k in qwen and olmo[k][c]["prompt"]["user"] == qwen[k][c]["prompt"]["user"] for k in qs_all)
                        for c in (OFF, ON)}
        aff = [k for k in qs_all if k_lines[k] >= 1]
        d = {"n_questions": len(qs_all), "n_affected": len(aff), "n_identical_prompts": sum(ident.values()),
             "user_prompt_identical_to_qwen": same_as_qwen,
             "mean_contradiction_lines_affected": sum(k_lines[k] for k in aff) / max(1, len(aff)),
             "populations": {}}
        for pop, qs in (("affected", aff), ("all", qs_all)):
            d["populations"][pop] = {"rates": metrics(olmo, qs), "contrasts": contrasts(olmo, qs)}
        # sensitivity: drop questions where either condition hit the 64-token limit
        trunc = [k for k in aff if any(olmo[k][c]["generation"]["finish_reason"] == "length" for c in (OFF, ON))]
        keep = [k for k in aff if k not in set(trunc)]
        d["sensitivity_affected_excluding_truncated"] = {"n_excluded": len(trunc), "contrasts": {
            m: v for m, v in contrasts(olmo, keep).items() if m in ("em", "lenient", "abstention")}}
        # same-question comparison with Qwen (exploratory interaction: OLMo effect - Qwen effect)
        qa = [k for k in aff if k in qwen and set(qwen[k]) == {OFF, ON}]
        cmp = {}
        for m, g in (("em", lambda r: float(state(r) == "C")), ("lenient", lenient), ("abstention", lambda r: float(state(r) == "A"))):
            eq = {k: g(qwen[k][ON]) - g(qwen[k][OFF]) for k in qa}
            eo = {k: g(olmo[k][ON]) - g(olmo[k][OFF]) for k in qa}
            cmp[m] = {"qwen_effect": paired_bootstrap_strat({k: g(qwen[k][OFF]) for k in qa}, {k: g(qwen[k][ON]) for k in qa}),
                      "olmo_effect": paired_bootstrap_strat({k: g(olmo[k][OFF]) for k in qa}, {k: g(olmo[k][ON]) for k in qa}),
                      "olmo_minus_qwen": paired_bootstrap_strat(eq, eo)}
        d["comparison_with_qwen_same_questions"] = {"n": len(qa), **cmp,
                                                    "note": "exploratory interaction; reused questions, not independent samples"}
        p_len[ds] = d["populations"]["affected"]["contrasts"]["lenient"]["p_boot"]
        p_em[ds] = d["populations"]["affected"]["contrasts"]["em"]["p_boot"]
        rep["datasets"][ds] = d
    for fam, ps in (("lenient", p_len), ("em", p_em)):
        for ds, p in holm(ps).items():
            c = rep["datasets"][ds]["populations"]["affected"]["contrasts"][fam]
            c["p_holm"] = p
            c["decision"] = ("confirmed (lower with contradiction lines)" if p is not None and p < 0.05 and c["delta"] < 0
                             else "significant, opposite direction" if p is not None and p < 0.05 else "inconclusive")
    (out / "expC_olmo2_summary.json").write_text(json.dumps(rep, indent=1))
    for ds, d in rep["datasets"].items():
        for pop, v in d["populations"].items():
            for m in ("em", "lenient", "abstention", "wrong", "em_given_both_answered"):
                c = v["contrasts"][m]
                rows.append({"reader": "OLMo-2-1124-7B-Instruct", "dataset": ds, "population": pop, "metric": m, "n": c["n"],
                             "rate_off": v["rates"][OFF].get(m, ""), "rate_on": v["rates"][ON].get(m, ""),
                             "delta_on_minus_off": c["delta"], "ci_low": c["ci"][0] if c["ci"] else "",
                             "ci_high": c["ci"][1] if c["ci"] else "", "p_boot": c["p_boot"], "p_holm": c.get("p_holm", ""),
                             "decision": c.get("decision", "")})
    with open(out / "expC_olmo2_contrasts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(out / "expC_olmo2_transitions.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dataset", "population", "scoring", "off_state", "on_state", "n"])
        for ds, d in rep["datasets"].items():
            for pop, v in d["populations"].items():
                for sc in ("em", "lenient"):
                    for cell, n in v["contrasts"][f"transitions_{sc} (off->on)"].items():
                        a, b = cell.split("->")
                        w.writerow([ds, pop, sc, a, b, n])
    print(json.dumps({ds: {fam: {k: d["populations"]["affected"]["contrasts"][fam].get(k) for k in ("n", "delta", "ci", "p_holm", "decision")}
                           for fam in ("em", "lenient")} for ds, d in rep["datasets"].items()}, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
