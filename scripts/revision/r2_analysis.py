"""Revision-2 analyses (EXPLORATORY unless stated): paired contrasts across conditions, prompts and readers.

Every record is keyed by (reader, prompt version, representation, dataset, question). A condition is written
`rep`, `rep@prompt` or `rep@prompt@reader` (reader: qwen | mistral). Each contrast `A>B` reports B - A for:
EM (frozen parser), token F1, lenient match (pre-specified in docs/REVISION2_PROTOCOL.md §3), abstention,
wrong-answer rate, accuracy among questions answered under both, evidence tokens, plus C/W/A transitions and
the number of byte-identical prompts. Paired percentile bootstrap over questions (2,000 resamples, seed 0).

    PYTHONPATH=src python scripts/revision/r2_analysis.py <out.csv> --runs <dir> [<dir> ...] --contrasts A>B [...]
        [--datasets d1,d2] [--strata contra_lines] [--questions-from <run_dir>]

Interactions: a contrast written `(A>B)-(C>D)` reports (B - A) - (D - C) over questions present in all four.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from wsh.evaluation.answer_metrics import token_f1
from wsh.text import normalize_answer

READERS = {"Qwen/Qwen2.5-7B-Instruct": "qwen", "mistralai/Mistral-7B-Instruct-v0.3": "mistral"}
PREFIX = re.compile(r"^(\s*answer\s*:\s*)+", re.I)


def lenient(r: dict) -> float:
    """1 if a normalised gold alias occurs as a token span in the normalised answer (after stripping repeated
    'Answer:'); yes/no golds need an exact match; abstentions and unparsed answers score 0."""
    if not r["failure"]["answered"]:
        return 0.0
    ans = (r.get("parsed") or {}).get("answer") or ""
    a = f" {normalize_answer(PREFIX.sub('', ans))} "
    for g in r["gold_answers"]:
        ng = normalize_answer(g)
        if not ng:
            continue
        if ng in {"yes", "no"}:
            if a.strip() == ng:
                return 1.0
        elif f" {ng} " in a:
            return 1.0
    return 0.0


def state(r: dict) -> str:
    if r["generation"].get("error") or not r["failure"]["answered"]:
        return "A"
    return "C" if (r["eval"].get("em") or 0) == 1 else "W"


def load(runs: list[Path]) -> dict:
    recs: dict = {}
    for run in runs:
        with open(run / "predictions.jsonl") as f:
            for line in f:
                r = json.loads(line)
                c = r["condition"]
                if c["protocol"] != "A" or r.get("unavailable") or r["task"] != "qa" or c["representation"] == "R2":
                    continue
                key = (READERS.get(r["model_id"], r["model_id"]), r.get("prompt_version", "qa-v2"), c["representation"],
                       r["dataset"], r["question_uid"])
                if key in recs:
                    assert recs[key]["prompt"]["user"] == r["prompt"]["user"], f"different prompts for {key}"
                    continue
                recs[key] = r
    return recs


def parse_cond(s: str) -> tuple[str, str, str]:
    parts = s.split("@")
    rep = parts[0]
    prompt = parts[1] if len(parts) > 1 else "qa-v2"
    reader = parts[2] if len(parts) > 2 else "qwen"
    return reader, prompt, rep


METRICS = {"em": lambda r: float(state(r) == "C"), "f1": lambda r: float(token_f1((r.get("parsed") or {}).get("answer"), r["gold_answers"]))
           if r["failure"]["answered"] else 0.0, "lenient": lenient, "abst": lambda r: float(state(r) == "A"),
           "wrong": lambda r: float(state(r) == "W"), "tokens": lambda r: float(r["evidence"]["evidence_tokens"])}


def boot(diffs: list[float], n_boot: int = 2000, seed: int = 0) -> list[float] | None:
    if not diffs:
        return None
    rng = random.Random(seed)
    n = len(diffs)
    s = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    return [s[int(0.025 * n_boot)], s[min(n_boot - 1, int(0.975 * n_boot) - 1)]]


def n_contra(r: dict) -> int:
    return sum(1 for ln in r["evidence"]["text"].splitlines() if " CONTRADICTS " in f" {ln} ")


def contrast(recs: dict, ds: str, a: tuple, b: tuple, keep=None) -> dict:
    qa = {k[4]: v for k, v in recs.items() if k[:3] == a and k[3] == ds}
    qb = {k[4]: v for k, v in recs.items() if k[:3] == b and k[3] == ds}
    qs = sorted(set(qa) & set(qb) if keep is None else set(qa) & set(qb) & keep)
    if not qs:
        return {}
    out = {"n": len(qs), "n_identical_prompts": sum(qa[q]["prompt"]["user"] == qb[q]["prompt"]["user"] for q in qs)}
    for m, f in METRICS.items():
        d = [f(qb[q]) - f(qa[q]) for q in qs]
        out[f"{m}_a"] = sum(f(qa[q]) for q in qs) / len(qs)
        out[f"{m}_b"] = sum(f(qb[q]) for q in qs) / len(qs)
        out[f"d_{m}"] = sum(d) / len(d)
        out[f"d_{m}_ci"] = boot(d) if m != "tokens" else None
    both = [q for q in qs if state(qa[q]) != "A" and state(qb[q]) != "A"]
    d = [float(state(qb[q]) == "C") - float(state(qa[q]) == "C") for q in both]
    out.update({"n_both_answered": len(both), "d_acc_both_answered": sum(d) / len(d) if d else None,
                "d_acc_both_answered_ci": boot(d)})
    out["transitions"] = dict(Counter(f"{state(qa[q])}->{state(qb[q])}" for q in qs))
    return out


def interaction(recs: dict, ds: str, a, b, c, d) -> dict:
    get = lambda cond: {k[4]: v for k, v in recs.items() if k[:3] == cond and k[3] == ds}  # noqa: E731
    A, B, C, D = get(a), get(b), get(c), get(d)
    qs = sorted(set(A) & set(B) & set(C) & set(D))
    out = {"n": len(qs)}
    for m in ("em", "abst", "wrong", "lenient"):
        f = METRICS[m]
        diffs = [(f(B[q]) - f(A[q])) - (f(D[q]) - f(C[q])) for q in qs]
        out[f"d_{m}"] = sum(diffs) / len(diffs) if diffs else None
        out[f"d_{m}_ci"] = boot(diffs)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--contrasts", nargs="+", required=True)
    ap.add_argument("--datasets", default=None)
    ap.add_argument("--strata", default=None, choices=[None, "contra_lines"])
    ap.add_argument("--questions-from", default=None, help="restrict every contrast to the questions of this run")
    a = ap.parse_args()
    recs = load([Path(p) for p in a.runs])
    if a.questions_from:
        keep = {k[4] for k in load([Path(a.questions_from)])}
        recs = {k: v for k, v in recs.items() if k[4] in keep}
    dss = a.datasets.split(",") if a.datasets else sorted({k[3] for k in recs})
    rows = []
    for ds in dss:
        for spec in a.contrasts:
            m = re.fullmatch(r"\((.+)>(.+)\)-\((.+)>(.+)\)", spec)
            if m:
                res = interaction(recs, ds, *(parse_cond(x) for x in m.groups()))
                if res.get("n"):
                    rows.append({"dataset": ds, "contrast": spec, "stratum": "all", **res})
                continue
            x, y = (parse_cond(s) for s in spec.split(">"))
            strata = {"all": None}
            if a.strata == "contra_lines":
                ref = {k[4]: v for k, v in recs.items() if k[:3] == y and k[3] == ds}
                lines = {q: n_contra(r) for q, r in ref.items()}
                for lab, lo, hi in (("0", 0, 0), ("1-2", 1, 2), ("3-5", 3, 5), ("6+", 6, 10**9), (">=1", 1, 10**9)):
                    strata[f"contra_lines={lab}"] = {q for q, n in lines.items() if lo <= n <= hi}
            for st, keep in strata.items():
                res = contrast(recs, ds, x, y, keep)
                if res:
                    rows.append({"dataset": ds, "contrast": spec, "stratum": st, **res})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in r.items()})
    for r in rows:
        ci = r.get("d_em_ci")
        print(f"{r['dataset'][:6]} {r['contrast']:44s} {r['stratum']:16s} n={r['n']:5d} dEM={r['d_em']:+.4f} "
              f"{[round(v, 4) for v in ci] if ci else ''} dAbst={r['d_abst']:+.4f} dLen={r.get('d_lenient', 0) or 0:+.4f}"
              + (f" dTok={r['d_tokens']:+.1f}" if 'd_tokens' in r else ""))


if __name__ == "__main__":
    main()
