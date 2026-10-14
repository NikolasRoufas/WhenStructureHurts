"""Revision-1 (EXPLORATORY): retrieved-evidence experiment analysis (docs/REVISION_PROTOCOL.md §2).

Paired contrasts per dataset and protocol setting, overall and by retrospective retrieval strata. Gold labels
are used only to define the strata, never to select evidence:
  retrieval = complete (all gold support sentences shown under Protocol A) / partial / none,
  distractor_heavy = at most 1 of the 4 retrieved passages contains a gold support sentence,
  long_evidence = Protocol A R1 evidence tokens above the dataset median,
  hop count.
    PYTHONPATH=src python scripts/revision/retrieval_analysis.py <run_dir> <out_dir>
"""
from __future__ import annotations

import csv
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

from wsh.evaluation.statistics import paired_bootstrap

CONTRASTS = [("R0", "R1"), ("R1", "R5"), ("R5", "R4"), ("R4", "R4P"), ("R4P_NC", "R4P"), ("R5", "R4P_FO")]


def setting(c):
    return "A" if c.get("protocol") == "A" else f"B {c['budget'].replace('content:', '')}x {c['policy']}"


def main():
    run, out = Path(sys.argv[1]), Path(sys.argv[2])
    recs = {}
    for line in open(run / "predictions.jsonl"):
        r = json.loads(line)
        recs[r["record_key"]] = r
    recs = [r for r in recs.values() if not r.get("unavailable") and "eval" in r]
    by = defaultdict(lambda: defaultdict(dict))  # (ds, setting) -> qid -> rep -> rec
    for r in recs:
        by[(r["dataset"], setting(r["condition"]))][r["question_uid"]][r["condition"]["representation"]] = r
    # retrospective strata from Protocol A R1 records (all retrieved sentences shown)
    strata = {}
    for (ds, s), qs in by.items():
        if s != "A":
            continue
        toks = [v["R1"]["evidence"]["evidence_tokens"] for v in qs.values() if "R1" in v]
        med = st.median(toks) if toks else 0
        for q, v in qs.items():
            r1 = v.get("R1")
            if not r1:
                continue
            sc = r1["eval"].get("support_coverage")
            gold_pass = {c["claim_id"].split("#")[0] for c in r1["evidence"]["claims"] if c["gold"]}
            strata[q] = {"retrieval": "complete" if sc == 1 else "none" if not sc else "partial",
                         "distractor_heavy": str(len(gold_pass) <= 1),
                         "long_evidence": str(r1["evidence"]["evidence_tokens"] > med),
                         "hops": str(r1.get("hop_count"))}
    rows = []
    em = lambda r: float((r["eval"].get("em") or 0) == 1)  # noqa: E731
    ab = lambda r: float(not r["failure"]["answered"])  # noqa: E731
    for (ds, s), qs in sorted(by.items()):
        for a, b in CONTRASTS:
            groups = {"all": list(qs)}
            for key in ("retrieval", "distractor_heavy", "long_evidence", "hops"):
                for q in qs:
                    if q in strata:
                        groups.setdefault(f"{key}={strata[q][key]}", []).append(q)
            for g, members in groups.items():
                pairs = [(qs[q][a], qs[q][b]) for q in members if a in qs[q] and b in qs[q]]
                if len(pairs) < 20:
                    continue
                A = {i: em(x) for i, (x, _) in enumerate(pairs)}
                B = {i: em(y) for i, (_, y) in enumerate(pairs)}
                res = paired_bootstrap(A, B)
                abst = paired_bootstrap({i: ab(x) for i, (x, _) in enumerate(pairs)}, {i: ab(y) for i, (_, y) in enumerate(pairs)})
                rows.append({"dataset": ds, "setting": s, "contrast": f"{b}-{a}", "stratum": g, "n": len(pairs),
                             "n_identical_prompts": sum(x["evidence"]["text"] == y["evidence"]["text"] for x, y in pairs),
                             "em_a": st.mean(A.values()), "em_b": st.mean(B.values()), "d_em": res["delta"], "d_em_ci": res["ci"],
                             "d_abst": abst["delta"], "d_abst_ci": abst["ci"],
                             "tokens_a": st.mean(x["evidence"]["evidence_tokens"] for x, _ in pairs),
                             "tokens_b": st.mean(y["evidence"]["evidence_tokens"] for _, y in pairs),
                             "answer_in_evidence_a": st.mean(float(x["eval"].get("answer_in_evidence") or 0) for x, _ in pairs),
                             "answer_in_evidence_b": st.mean(float(y["eval"].get("answer_in_evidence") or 0) for _, y in pairs)})
    # absolute table per representation
    absr = []
    for (ds, s), qs in sorted(by.items()):
        reps = sorted({rep for v in qs.values() for rep in v})
        for rep in reps:
            rs = [v[rep] for v in qs.values() if rep in v]
            ba = [r["info"].get("budget_accounting") for r in rs if r["info"].get("budget_accounting")]
            absr.append({"dataset": ds, "setting": s, "representation": rep, "n": len(rs), "em": st.mean(map(em, rs)),
                         "coverage": 1 - st.mean(map(ab, rs)), "evidence_tokens": st.mean(r["evidence"]["evidence_tokens"] for r in rs),
                         "answer_in_evidence": st.mean(float(r["eval"].get("answer_in_evidence") or 0) for r in rs),
                         "support_coverage": st.mean(float(r["eval"].get("support_coverage") or 0) for r in rs),
                         "facts_kept": st.mean(b["n_facts_kept"] / b["n_facts_total"] for b in ba) if ba else None,
                         "relation_lines": st.mean(r["evidence"]["n_relations"] for r in rs)})
    dist = defaultdict(lambda: defaultdict(int))
    for q, sdict in strata.items():
        dist[q.split("/")[0]][sdict["retrieval"]] += 1
    out.mkdir(parents=True, exist_ok=True)
    for name, data in (("retrieval_contrasts.csv", rows), ("retrieval_absolute.csv", absr)):
        cols = list(dict.fromkeys(k for r in data for k in r))
        with open(out / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in data:
                w.writerow({k: json.dumps(v) if isinstance(v, list) else v for k, v in r.items()})
    (out / "retrieval_strata_counts.json").write_text(json.dumps({k: dict(v) for k, v in dist.items()}, indent=1))
    print(json.dumps({k: dict(v) for k, v in dist.items()}))
    for r in absr:
        print(f"{r['dataset'][:6]} {r['setting']:24s} {r['representation']:7s} n={r['n']} EM={r['em']:.3f} cov={r['coverage']:.3f} tok={r['evidence_tokens']:.0f} aie={r['answer_in_evidence']:.3f} kept={r['facts_kept']} lines={r['relation_lines']:.1f}")
    for r in rows:
        if r["stratum"] == "all" or r["stratum"].startswith("retrieval="):
            print(f"{r['dataset'][:6]} {r['setting']:24s} {r['contrast']:10s} {r['stratum']:20s} n={r['n']} ident={r['n_identical_prompts']} "
                  f"dEM={r['d_em']:+.3f} [{r['d_em_ci'][0]:+.3f},{r['d_em_ci'][1]:+.3f}] dAbst={r['d_abst']:+.3f}")


if __name__ == "__main__":
    main()
