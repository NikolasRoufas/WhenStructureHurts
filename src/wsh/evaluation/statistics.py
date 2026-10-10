"""Paired, question-level statistics.

* The resampling unit is the QUESTION. Repeated runs of a question (seeds, shuffles) are first
  averaged within the question, so they are never treated as independent examples.
* Paired comparisons use only questions present in both conditions; n is always reported.
* Coverage-adjusted means count unanswered examples as 0 over ALL attempted examples;
  conditional means are over answered examples only and are reported with their n.
* Interpretation guards: an interval containing 0 is reported as "inconclusive" (never as
  equivalence); comparisons with n < min_n_confirmatory are tagged "underpowered/exploratory".
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any, Callable, Iterable

MIN_N_CONFIRMATORY = 100  # below this, results are exploratory by construction


def mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def by_question(records: Iterable[dict], value: Callable[[dict], float | None]) -> dict[str, float]:
    """Average a per-record value within each question (None values are skipped)."""
    acc: dict[str, list[float]] = defaultdict(list)
    for r in records:
        v = value(r)
        if v is not None:
            acc[r["question_uid"]].append(float(v))
    return {q: sum(v) / len(v) for q, v in acc.items()}


def bootstrap_ci(values: list[float], n_boot: int = 2000, seed: int = 0, alpha: float = 0.05) -> tuple[float, float] | None:
    if not values:
        return None
    rng = random.Random(seed)
    n = len(values)
    stats = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    lo = stats[int(math.floor(alpha / 2 * n_boot))]
    hi = stats[min(n_boot - 1, int(math.ceil((1 - alpha / 2) * n_boot)) - 1)]
    return lo, hi


def paired_bootstrap(a: dict[str, float], b: dict[str, float], n_boot: int = 2000, seed: int = 0,
                     alpha: float = 0.05) -> dict[str, Any]:
    """Difference b - a over questions present in both. Percentile CI; two-sided bootstrap
    p-value approximated as 2*min(P(d<=0), P(d>=0))."""
    qs = sorted(set(a) & set(b))
    n = len(qs)
    out: dict[str, Any] = {"n_paired": n, "n_only_a": len(set(a) - set(b)), "n_only_b": len(set(b) - set(a))}
    if n == 0:
        out.update({"delta": None, "ci": None, "p_boot": None, "verdict": "no paired data"})
        return out
    d = [b[q] - a[q] for q in qs]
    rng = random.Random(seed)
    boots = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    lo = boots[int(math.floor(alpha / 2 * n_boot))]
    hi = boots[min(n_boot - 1, int(math.ceil((1 - alpha / 2) * n_boot)) - 1)]
    p = 2 * min(sum(x <= 0 for x in boots), sum(x >= 0 for x in boots)) / n_boot
    delta = sum(d) / n
    out.update({
        "delta": delta, "ci": [lo, hi], "p_boot": min(1.0, p), "n_boot": n_boot, "seed": seed,
        "n_b_better": sum(x > 0 for x in d), "n_a_better": sum(x < 0 for x in d), "n_tied": sum(x == 0 for x in d),
    })
    if lo <= 0 <= hi:
        out["verdict"] = "inconclusive (CI contains 0; not evidence of equivalence)"
    else:
        out["verdict"] = "b > a" if delta > 0 else "b < a"
    out["power_note"] = ("underpowered/exploratory" if n < MIN_N_CONFIRMATORY else "adequate n for a confirmatory test "
                         "only if pre-registered")
    return out


def holm(pvals: dict[str, float | None]) -> dict[str, float | None]:
    """Holm-Bonferroni adjusted p-values for a pre-specified family of comparisons."""
    items = sorted(((k, p) for k, p in pvals.items() if p is not None), key=lambda x: x[1])
    m = len(items)
    adj: dict[str, float | None] = {k: None for k in pvals}
    running = 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        adj[k] = running
    return adj


def coverage_summary(records: list[dict], metric: str) -> dict[str, Any]:
    """Coverage-adjusted vs conditional mean of an eval metric, with explicit denominators.
    Question-level: seeds are averaged within question first."""
    n_att = len({r["question_uid"] for r in records})
    # The evaluator scores unanswered examples 0 on every applicable metric and None where the
    # metric does not apply, so the coverage-adjusted mean is simply the mean of non-None values.
    cov_adj = by_question(records, lambda r: r["eval"].get(metric))
    cond = by_question([r for r in records if r["failure"]["answered"]], lambda r: r["eval"].get(metric))
    return {
        "n_attempted_questions": n_att, "n_records": len(records),
        "n_answered_records": sum(r["failure"]["answered"] for r in records),
        "coverage": mean([float(r["failure"]["answered"]) for r in records]),
        f"{metric}_coverage_adjusted": mean(list(cov_adj.values())),
        f"{metric}_coverage_adjusted_ci": bootstrap_ci(list(cov_adj.values())),
        f"{metric}_conditional": mean(list(cond.values())), "n_conditional_questions": len(cond),
    }
