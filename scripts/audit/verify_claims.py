"""Independent audit of the paper's numerical claims (revision-1, Phase 1).

Re-derives every central number from the saved predictions WITHOUT using scripts/analysis/build.py:
own record loading, own per-question aggregation, own paired bootstrap (both the frozen algorithm,
re-implemented, and an independent numpy bootstrap with a different seed), own Holm, own TOST,
own exact McNemar. Checks counts, uniqueness, disjointness, model/decoding consistency, cache
reuse, Protocol A fact identity, Protocol B accounting, run timing and protocol timestamps.

    python scripts/audit/verify_claims.py --runs <runs.json> --out <dir>   (run from the repo root)
Writes <dir>/audit.json and <dir>/claims_check.csv. Pure read-only on the run directories.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def load(d: Path) -> list[dict]:
    recs = {}
    with open(d / "predictions.jsonl") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            recs[r["record_key"]] = r
    return list(recs.values())


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def metric(r):
    return "em" if r["task"] == "qa" else "verdict_acc"


def per_q(rs, value):
    acc = defaultdict(list)
    for r in rs:
        v = value(r)
        if v is not None:
            acc[r["question_uid"]].append(float(v))
    return {q: sum(v) / len(v) for q, v in acc.items()}


def frozen_bootstrap(a, b, n_boot=2000, seed=0, alpha=0.05):
    """Re-implementation of the frozen procedure (PILOT_PROTOCOL §7), written independently."""
    qs = sorted(set(a) & set(b))
    d = [b[q] - a[q] for q in qs]
    n = len(d)
    rng = random.Random(seed)
    boots = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    lo = boots[int(math.floor(alpha / 2 * n_boot))]
    hi = boots[min(n_boot - 1, int(math.ceil((1 - alpha / 2) * n_boot)) - 1)]
    p = min(1.0, 2 * min(sum(x <= 0 for x in boots), sum(x >= 0 for x in boots)) / n_boot)
    return {"n": n, "delta": sum(d) / n, "ci": [lo, hi], "p": p, "d": d}


def numpy_bootstrap(d, n_boot=20000, seed=12345, alpha=0.05):
    x = np.asarray(d)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    m = x[idx].mean(axis=1)
    return [float(np.quantile(m, alpha / 2)), float(np.quantile(m, 1 - alpha / 2))]


def tost_p(d, margin=0.02):
    """Paired TOST with a normal approximation (secondary check of the bootstrap 90% CI rule)."""
    x = np.asarray(d)
    se = x.std(ddof=1) / math.sqrt(len(x))
    if se == 0:
        return 0.0
    from math import erf
    phi = lambda z: 0.5 * (1 + erf(z / math.sqrt(2)))  # noqa: E731
    p1 = 1 - phi((x.mean() + margin) / se)
    p2 = phi((x.mean() - margin) / se)
    return float(max(p1, p2))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [None] * len(ps), 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - k) * ps[i]))
        adj[i] = run
    return adj


def mcnemar(n01, n10):
    n = n01 + n10
    if not n:
        return None
    k = min(n01, n10)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    runs = json.loads(Path(a.runs).read_text())
    audit = {"runs": {}, "checks": {}, "claims": []}
    data = {}
    for lab, d in runs.items():
        d = Path(d)
        recs = load(d)
        man = json.loads((d / "manifest.json").read_text())
        data[lab] = (recs, man)
        keys = Counter()
        with open(d / "predictions.jsonl") as f:
            for line in f:
                try:
                    keys[json.loads(line)["record_key"]] += 1
                except json.JSONDecodeError:
                    keys["<corrupt line>"] += 1
        gens = [r["generation"] for r in recs if r.get("generation")]
        dec = Counter(json.dumps({"m": r["model_id"], "rev": r["model_revision"], "p": r["prompt_version"],
                                  "dec": (r.get("generation") or {}).get("decoding")}, sort_keys=True)
                      for r in recs if r.get("generation"))
        audit["runs"][lab] = {
            "dir": str(d), "stage": man["stage"], "experiment": man["experiment"], "status": man.get("status"),
            "git_commit": man.get("git_commit"), "started_at": man.get("started_at"), "finished_at": man.get("finished_at"),
            "wall_clock_s": man.get("wall_clock_s"), "gpu_hours": round((man.get("wall_clock_s") or 0) / 3600, 3),
            "n_lines_in_file": sum(keys.values()), "n_unique_keys": len(recs),
            "duplicate_lines": sum(v - 1 for v in keys.values() if v > 1),
            "questions_per_dataset": {ds: len({r["question_uid"] for r in recs if r["dataset"] == ds})
                                      for ds in sorted({r["dataset"] for r in recs})},
            "n_unavailable": sum(1 for r in recs if r.get("unavailable")),
            "n_generation_error": sum(1 for g in gens if g.get("finish_reason") == "error"),
            "finish_reasons": dict(Counter(g.get("finish_reason") for g in gens)),
            "n_cached": sum(1 for g in gens if g.get("cached")),
            "distinct_generator_signatures": len(dec),
            "generator_signatures": [json.loads(k) for k in dec],
            "device": man.get("device"), "gpu_pci_bus": (man.get("environment", {}).get("cuda", {}).get("devices") or [{}])[0].get("pci_bus_id"),
            "mps_pipe": man.get("environment", {}).get("cuda", {}).get("mps_control_pipe"),
            "predictions_sha256": sha(d / "predictions.jsonl"),
        }
        # cache consistency: identical full prompts must have identical outputs within a run
        byprompt = defaultdict(set)
        for r in recs:
            if r.get("prompt") and r.get("generation"):
                byprompt[(r["prompt"]["system"], r["prompt"]["user"])].add(r["generation"]["text"])
        audit["runs"][lab]["prompts_with_divergent_outputs"] = sum(1 for v in byprompt.values() if len(v) > 1)

    # ---------------------------------------------------------------- question sets and disjointness
    pil = json.loads(Path("configs/question_sets/pilot_v1.json").read_text())["datasets"]
    con = json.loads(Path("configs/question_sets/confirm_v1.json").read_text())["datasets"]
    smoke = {e["uid"] for e in json.loads(Path("configs/excluded_questions.json").read_text())["excluded"]}
    pu = {f"{ds}/{q}" for ds, qs in pil.items() for q in qs}
    cu = {f"{ds}/{q}" for ds, qs in con.items() for q in qs}
    F = {r["question_uid"] for r in data["F_exp1"][0]}
    C = {r["question_uid"] for r in data["C_exp1"][0]}
    audit["checks"]["disjointness"] = {
        "pilot_set_size": len(pu), "confirm_set_size": len(cu),
        "pilot_vs_confirm_overlap": len(pu & cu), "smoke_vs_confirm_overlap": len(smoke & cu),
        "smoke_vs_pilot_overlap": len(smoke & pu),
        "F_exp1_questions_equal_confirm_set": F == cu, "F_exp1_vs_pilot_overlap": len(F & pu),
        "C_exp1_questions_equal_pilot_set": C == pu,
        "confirm_unique_ids": all(len(v) == len(set(v)) for v in con.values()),
        "splits": sorted({r["split"] for lab in data for r in data[lab][0]}),
        "pilot_sha256": sha(Path("configs/question_sets/pilot_v1.json")),
        "confirm_sha256": sha(Path("configs/question_sets/confirm_v1.json")),
    }

    # ---------------------------------------------------------------- Protocol A fact identity
    fid = {}
    for lab in ("C_exp1", "F_exp1"):
        recs = data[lab][0]
        g = defaultdict(set)
        outside = Counter()
        for r in recs:
            c = r["condition"]
            if r.get("unavailable") or c.get("protocol") != "A":
                continue
            inf = r["info"]["information"]
            g[r["question_uid"]].add(inf["fact_digest"])
            if inf.get("passage_chars_outside_facts"):
                outside[c["representation"]] += 1
        fid[lab] = {"questions": len(g), "questions_with_more_than_one_fact_digest": sum(1 for v in g.values() if len(v) > 1),
                    "records_with_passage_chars_outside_facts_by_rep": dict(outside)}
    audit["checks"]["protocolA_fact_identity"] = fid

    # ---------------------------------------------------------------- primary contrasts (confirmatory)
    def rep_map(recs, ds, rep, prot="A", value=None):
        rs = [r for r in recs if r["dataset"] == ds and not r.get("unavailable") and r["condition"].get("protocol") == prot
              and r["condition"].get("representation") == rep]
        return per_q(rs, value or (lambda r: r["eval"].get(metric(r))))

    recs = data["F_exp1"][0]
    rows = []
    for ds in ("musique", "2wikimultihopqa"):
        for a_, b_ in (("R0", "R1"), ("R1", "R5"), ("R5", "R4")):
            A, B = rep_map(recs, ds, a_), rep_map(recs, ds, b_)
            fb = frozen_bootstrap(A, B)
            ci90 = frozen_bootstrap(A, B, alpha=0.10)["ci"]
            n01 = sum(1 for x in fb["d"] if x > 0)
            n10 = sum(1 for x in fb["d"] if x < 0)
            rows.append({"dataset": ds, "contrast": f"{b_}-{a_}", "n": fb["n"], "delta": fb["delta"], "ci95_frozen": fb["ci"],
                         "ci95_numpy_indep": numpy_bootstrap(fb["d"]), "p_boot": fb["p"], "ci90": ci90,
                         "equiv_bootstrap90_within_0.02": -0.02 <= ci90[0] and ci90[1] <= 0.02, "tost_p_normal": tost_p(fb["d"]),
                         "mcnemar_p": mcnemar(n01, n10), "b_better": n01, "a_better": n10})
    adj = holm([r["p_boot"] for r in rows])
    for r, p in zip(rows, adj):
        r["p_holm"] = p
    tost_adj = holm([r["tost_p_normal"] for r in rows])
    for r, p in zip(rows, tost_adj):
        r["tost_p_holm"] = p
    audit["checks"]["confirmatory_primary"] = rows

    # per-representation EM and coverage on the confirmatory sample
    absr = {}
    for ds in ("musique", "2wikimultihopqa"):
        for rep in ("R0", "R1", "R2", "R3", "R4", "R4P", "R5"):
            em = rep_map(recs, ds, rep)
            cov = rep_map(recs, ds, rep, value=lambda r: float(r["failure"]["answered"]))
            absr[f"{ds}/{rep}"] = {"n_q": len(em), "em": sum(em.values()) / len(em), "coverage": sum(cov.values()) / len(cov)}
    audit["checks"]["confirmatory_absolute"] = absr

    # secondary: R4P - R4
    sec = []
    for ds in ("musique", "2wikimultihopqa"):
        for a_, b_ in (("R4", "R4P"), ("R1", "R2"), ("R5", "R3")):
            fb = frozen_bootstrap(rep_map(recs, ds, a_), rep_map(recs, ds, b_))
            cv = frozen_bootstrap(rep_map(recs, ds, a_, value=lambda r: float(r["failure"]["answered"])),
                                  rep_map(recs, ds, b_, value=lambda r: float(r["failure"]["answered"])))
            sec.append({"dataset": ds, "contrast": f"{b_}-{a_}", "n": fb["n"], "delta": fb["delta"], "ci95": fb["ci"],
                        "coverage_delta": cv["delta"]})
    audit["checks"]["confirmatory_secondary"] = sec

    # ---------------------------------------------------------------- Protocol B accounting (pilot)
    pb = {}
    for r in data["C_exp1"][0]:
        c = r["condition"]
        if r.get("unavailable") or c.get("protocol") != "B" or r["dataset"] not in ("musique", "2wikimultihopqa"):
            continue
        ba = r["info"].get("budget_accounting")
        k = f"{r['dataset']}|{c['budget']}|{c['policy']}|{c['representation']}"
        e = pb.setdefault(k, {"n": 0, "kept": 0.0, "ans_drop": 0.0, "ovh": 0.0})
        e["n"] += 1
        e["kept"] += ba["n_facts_kept"] / ba["n_facts_total"]
        e["ans_drop"] += ba["answer_bearing_facts_dropped"]
        e["ovh"] += r["info"]["information"]["overhead_tokens"]
    audit["checks"]["protocolB_accounting"] = {k: {"n": v["n"], "kept": v["kept"] / v["n"], "answer_bearing_dropped": v["ans_drop"] / v["n"],
                                                   "overhead_tokens": v["ovh"] / v["n"]} for k, v in sorted(pb.items())}

    # ---------------------------------------------------------------- protocol timestamps
    def commit_time(c):
        return git("show", "-s", "--format=%cI", c)
    audit["checks"]["timeline"] = {
        "pilot_protocol_first_commit": git("log", "--diff-filter=A", "--format=%h %cI", "--", "docs/PILOT_PROTOCOL.md"),
        "pilot_set_first_commit": git("log", "--diff-filter=A", "--format=%h %cI", "--", "configs/question_sets/pilot_v1.json"),
        "confirm_protocol_first_commit": git("log", "--diff-filter=A", "--format=%h %cI", "--", "docs/CONFIRMATORY_PROTOCOL.md"),
        "confirm_set_first_commit": git("log", "--diff-filter=A", "--format=%h %cI", "--", "configs/question_sets/confirm_v1.json"),
        "confirm_config_first_commit": git("log", "--diff-filter=A", "--format=%h %cI", "--", "configs/confirm.yaml"),
        "run_starts": {lab: v["started_at"] for lab, v in audit["runs"].items()},
        "pilot_protocol_changes_after_first_pilot_run": git("log", "--format=%h %cI %s", "--since=2026-10-12T09:52:00+00:00", "--", "docs/PILOT_PROTOCOL.md"),
        "confirm_protocol_changes": git("log", "--format=%h %cI %s", "--", "docs/CONFIRMATORY_PROTOCOL.md"),
    }
    audit["checks"]["gpu_hours_total"] = round(sum(v["gpu_hours"] for v in audit["runs"].values()), 3)
    (out / "audit.json").write_text(json.dumps(audit, indent=1, default=str))

    # ---------------------------------------------------------------- claim table (paper values vs recomputed)
    P = {(r["dataset"], r["contrast"]): r for r in rows}
    S = {(r["dataset"], r["contrast"]): r for r in sec}
    claims = [
        ("Abstract/§6.1", "2Wiki R1-R0 ΔEM", -0.017, P[("2wikimultihopqa", "R1-R0")]["delta"]),
        ("Abstract/§6.1", "2Wiki R1-R0 CI low", -0.029, P[("2wikimultihopqa", "R1-R0")]["ci95_frozen"][0]),
        ("Abstract/§6.1", "2Wiki R1-R0 CI high", -0.005, P[("2wikimultihopqa", "R1-R0")]["ci95_frozen"][1]),
        ("§6.1", "2Wiki R1-R0 p_Holm", 0.018, P[("2wikimultihopqa", "R1-R0")]["p_holm"]),
        ("§6.1", "MuSiQue R1-R0 ΔEM", -0.001, P[("musique", "R1-R0")]["delta"]),
        ("§6.1", "MuSiQue R5-R1 ΔEM", -0.011, P[("musique", "R5-R1")]["delta"]),
        ("§6.1", "2Wiki R5-R1 ΔEM", -0.008, P[("2wikimultihopqa", "R5-R1")]["delta"]),
        ("§6.1", "MuSiQue R4-R5 ΔEM", 0.010, P[("musique", "R4-R5")]["delta"]),
        ("§6.1", "2Wiki R4-R5 ΔEM", 0.006, P[("2wikimultihopqa", "R4-R5")]["delta"]),
        ("§6.3/abstract", "2Wiki R4P-R4 ΔEM", -0.036, S[("2wikimultihopqa", "R4P-R4")]["delta"]),
        ("§6.3/abstract", "MuSiQue R4P-R4 ΔEM", -0.045, S[("musique", "R4P-R4")]["delta"]),
        ("§6.3", "2Wiki R2-R1 ΔEM", -0.024, S[("2wikimultihopqa", "R2-R1")]["delta"]),
    ]
    with open(out / "claims_check.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["location", "claim", "paper_value", "recomputed", "abs_diff", "matches_to_rounding"])
        for loc, name, pv, rv in claims:
            w.writerow([loc, name, pv, round(rv, 4), round(abs(rv - pv), 4), abs(rv - pv) <= 0.0005 + 1e-9])
    print(json.dumps({"disjointness": audit["checks"]["disjointness"], "fact_identity": fid,
                      "gpu_hours_total": audit["checks"]["gpu_hours_total"]}, indent=1))
    for r in rows:
        print(r["dataset"], r["contrast"], round(r["delta"], 4), [round(x, 4) for x in r["ci95_frozen"]],
              "numpy", [round(x, 4) for x in r["ci95_numpy_indep"]], "p", r["p_boot"], "holm", round(r["p_holm"], 4),
              "ci90", [round(x, 4) for x in r["ci90"]], "equiv", r["equiv_bootstrap90_within_0.02"],
              "tost", round(r["tost_p_normal"], 4), "tost_holm", round(r["tost_p_holm"], 4))


if __name__ == "__main__":
    main()
