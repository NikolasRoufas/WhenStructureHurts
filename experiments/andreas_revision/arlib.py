"""Shared helpers for the journal-revision experiments (experiments/andreas_revision).

Outcome states, lenient match, paired / stratified / clustered bootstrap, Cohen's kappa, Wilson intervals,
transition matrices and the 7 -> 3 class label mapping. Everything is deterministic (seeded) and fails fast
on invalid input instead of silently dropping records.
"""
from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable

# ---------------------------------------------------------------- labels -------------------------------------

LABELS7 = ["genuine_contradiction", "compatible_different_entities", "compatible_different_times_or_values",
           "coreference_or_entity_resolution_error", "context_ambiguity", "compatible_other", "uncertain"]
TO3 = {"genuine_contradiction": "genuine",
       "compatible_different_entities": "false", "compatible_different_times_or_values": "false",
       "coreference_or_entity_resolution_error": "false", "compatible_other": "false",
       "context_ambiguity": "ambiguous", "uncertain": "ambiguous"}
CLASSES3 = ["genuine", "false", "ambiguous"]
# optional error-category tag at the start of `notes`, e.g. "[time] different years of two events"
NOTE_TAGS = ["entity", "time", "number", "negation", "context", "coreference", "genuine-conflict", "other"]
TAG_RE = re.compile(r"^\s*\[([a-z\-]+)\]")


def to3(label7: str) -> str:
    if label7 not in TO3:
        raise ValueError(f"invalid label {label7!r}")
    return TO3[label7]


def note_tag(notes: str) -> str | None:
    m = TAG_RE.match(notes or "")
    return m.group(1) if m and m.group(1) in NOTE_TAGS else None


# ---------------------------------------------------------------- outcomes -----------------------------------

PREFIX = re.compile(r"^(\s*answer\s*:\s*)+", re.I)


def state(r: dict) -> str:
    """C / W / A exactly as scripts/revision/confirm2_analysis.py (errors and unparsed answers count as A)."""
    if r["generation"].get("error") or not r["failure"]["answered"]:
        return "A"
    return "C" if (r["eval"].get("em") or 0) == 1 else "W"


def lenient(r: dict) -> float:
    """Identical to scripts/revision/r2_analysis.py lenient()."""
    from wsh.text import normalize_answer

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


def load_records(run: Path, reps: set[str] | None = None) -> dict[tuple[str, str], dict[str, dict]]:
    """(dataset, question_uid) -> representation -> record (Protocol A; last write wins on resume)."""
    recs = {}
    with open(run / "predictions.jsonl") as f:
        for line in f:
            r = json.loads(line)
            recs[r["record_key"]] = r
    by: dict = defaultdict(dict)
    for r in recs.values():
        c = r["condition"]
        if c.get("protocol") == "A" and (reps is None or c["representation"] in reps):
            if r.get("unavailable"):
                raise ValueError(f"{r['question_uid']} {c['representation']}: unavailable record ({r['unavailable']})")
            by[(r["dataset"], r["question_uid"])][c["representation"]] = r
    return by


def n_contra_lines(text: str) -> int:
    return sum(1 for ln in text.splitlines() if " CONTRADICTS " in f" {ln} ")


def transitions(sa: dict[str, str], sb: dict[str, str]) -> dict[str, int]:
    """Full 3x3 table a->b over common keys (all 9 cells present)."""
    t = {f"{x}->{y}": 0 for x in "CWA" for y in "CWA"}
    for q in sorted(set(sa) & set(sb)):
        t[f"{sa[q]}->{sb[q]}"] += 1
    return t


# ---------------------------------------------------------------- statistics ---------------------------------

def _pct(boots: list[float], alpha: float) -> list[float]:
    boots = sorted(boots)
    n = len(boots)
    return [boots[int(math.floor(alpha / 2 * n))], boots[min(n - 1, int(math.ceil((1 - alpha / 2) * n)) - 1)]]


def paired_bootstrap_strat(a: dict, b: dict, strata: dict | None = None, n_boot: int = 2000, seed: int = 0,
                           alpha: float = 0.05) -> dict:
    """Mean of b[q] - a[q]; percentile CI resampling questions within strata (one stratum if None).
    Two-sided bootstrap p as in wsh.evaluation.statistics.paired_bootstrap. Keys must match exactly."""
    if set(a) != set(b):
        raise ValueError(f"paired keys differ: {len(set(a) ^ set(b))} unmatched")
    qs = sorted(a)
    if not qs:
        return {"n": 0, "delta": None, "ci": None, "p_boot": None}
    d = {q: b[q] - a[q] for q in qs}
    groups: dict = defaultdict(list)
    for q in qs:
        groups[(strata or {}).get(q, "_")].append(q)
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        tot = 0.0
        for g in groups.values():
            tot += sum(d[g[rng.randrange(len(g))]] for _ in range(len(g)))
        boots.append(tot / len(qs))
    p = 2 * min(sum(x <= 0 for x in boots), sum(x >= 0 for x in boots)) / n_boot
    delta = sum(d.values()) / len(qs)
    ci = _pct(boots, alpha)
    return {"n": len(qs), "delta": delta, "ci": ci, "p_boot": min(1.0, p), "n_boot": n_boot, "seed": seed,
            "n_b_better": sum(x > 0 for x in d.values()), "n_a_better": sum(x < 0 for x in d.values()),
            "n_tied": sum(x == 0 for x in d.values()),
            "verdict": "inconclusive (CI contains 0)" if ci[0] <= 0 <= ci[1] else ("b > a" if delta > 0 else "b < a")}


def holm(p: dict) -> dict:
    items = sorted(((k, v) for k, v in p.items() if v is not None), key=lambda x: x[1])
    out, run = {k: None for k in p}, 0.0
    for i, (k, v) in enumerate(items):
        run = max(run, min(1.0, (len(items) - i) * v))
        out[k] = run
    return out


def wilson(k: int, n: int, z: float = 1.959964) -> list[float] | None:
    if n == 0:
        return None
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [max(0.0, c - h), min(1.0, c + h)]


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    if len(a) != len(b):
        raise ValueError("kappa: unequal lengths")
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def cluster_bootstrap(items: list, cluster: Callable, stat: Callable[[list], float | None], strata: Callable | None = None,
                      n_boot: int = 2000, seed: int = 0, alpha: float = 0.05) -> list[float] | None:
    """Percentile CI of stat(items), resampling whole clusters (e.g. questions), within strata if given."""
    by: dict = defaultdict(lambda: defaultdict(list))
    for it in items:
        by[strata(it) if strata else "_"][cluster(it)].append(it)
    groups = {s: list(c.values()) for s, c in by.items()}
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        sample = []
        for cl in groups.values():
            for _ in range(len(cl)):
                sample.extend(cl[rng.randrange(len(cl))])
        v = stat(sample)
        if v is not None:
            boots.append(v)
    return _pct(boots, alpha) if len(boots) >= 0.9 * n_boot else None


def confusion(a: Iterable[str], b: Iterable[str], labels: list[str]) -> dict[str, dict[str, int]]:
    m = {x: {y: 0 for y in labels} for x in labels}
    for x, y in zip(a, b):
        m[x][y] += 1
    return m


def sha256(p: Path) -> str:
    import hashlib

    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
