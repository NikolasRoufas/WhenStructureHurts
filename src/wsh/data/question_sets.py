"""Frozen question sets and exclusion guards.

A frozen set is decided BEFORE any generation: eligibility rules are fixed in code
(``ELIGIBILITY``), the pool is filtered, excluded questions (smoke / prompt-development) are
removed, and a seeded stratified sample is written to JSON together with the rules, pool
sizes, strata counts and dataset file hashes. Pilot/full configs load questions only from
such a file (``datasets[*].qids_file``), and ``assert_no_excluded`` refuses any run whose
questions overlap the exclusion list.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any, Callable

from ..config import repo_path
from ..hashing import file_sha256
from .loaders import DEFAULT_DATA_ROOT, iter_questions, load_registry
from .schemas import AnnotationStatus, Question


class ExcludedQuestionError(RuntimeError):
    pass


def load_excluded(path: str | Path | None) -> dict[str, str]:
    """uid -> reason."""
    if not path or not repo_path(path).exists():
        return {}
    raw = json.loads(repo_path(path).read_text())
    return {e["uid"]: e["reason"] for e in raw["excluded"]}


def assert_no_excluded(questions: dict[str, list[Question]], excluded: dict[str, str], stage: str) -> None:
    if stage == "smoke":
        return
    hits = [q.uid for qs in questions.values() for q in qs if q.uid in excluded]
    if hits:
        raise ExcludedQuestionError(f"{len(hits)} excluded question(s) selected for a {stage} run "
                                    f"(e.g. {hits[0]}: {excluded[hits[0]]})")


def _gold_evidence_available(q: Question) -> bool:
    from ..representations.evidence import EvidenceUnavailable, gold_bundle

    try:
        gold_bundle(q)
        return True
    except EvidenceUnavailable:
        return False


def _has_reasoning_order(q: Question) -> bool:
    return q.annotations.get("reasoning_order", AnnotationStatus.UNAVAILABLE) != AnnotationStatus.UNAVAILABLE


# Pre-specified eligibility (documented in docs/PILOT_PROTOCOL.md section 3).
ELIGIBILITY: dict[str, list[tuple[str, Callable[[Question], bool]]]] = {
    "musique": [("gold_evidence_available", _gold_evidence_available), ("reasoning_order_available", _has_reasoning_order)],
    "2wikimultihopqa": [("gold_evidence_available", _gold_evidence_available), ("reasoning_order_available", _has_reasoning_order)],
    "hotpotqa": [("gold_evidence_available", _gold_evidence_available), ("reasoning_order_available", _has_reasoning_order)],
    "hover": [("gold_evidence_available", _gold_evidence_available)],
    "fever": [("gold_evidence_available", _gold_evidence_available)],
}


def freeze(spec: dict[str, dict[str, Any]], seed: int, excluded: dict[str, str], split: str = "dev",
           data_root: Path = DEFAULT_DATA_ROOT) -> dict[str, Any]:
    """spec: dataset -> {"n": int, "stratify_by": attr|None}."""
    reg = load_registry()
    out: dict[str, Any] = {"created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "split": split, "seed": seed,
                           "datasets": {}, "details": {}}
    for name, s in spec.items():
        rules = ELIGIBILITY[name]
        pool, n_seen, n_excl, fails = [], 0, 0, {r: 0 for r, _ in rules}
        for q in iter_questions(name, split, data_root):
            n_seen += 1
            if q.uid in excluded:
                n_excl += 1
                continue
            bad = [r for r, f in rules if not f(q)]
            for r in bad:
                fails[r] += 1
            if not bad:
                pool.append(q)
        rng = random.Random(seed)
        order = list(range(len(pool)))
        rng.shuffle(order)
        key = s.get("stratify_by")
        strata: dict[str, list[int]] = {}
        for i in order:
            strata.setdefault(str(getattr(pool[i], key)) if key else "all", []).append(i)
        picked: list[int] = []
        while len(picked) < min(s["n"], len(pool)):
            for k in sorted(strata):
                if strata[k] and len(picked) < s["n"]:
                    picked.append(strata[k].pop(0))
        chosen = [pool[i] for i in picked]
        out["datasets"][name] = [q.qid for q in chosen]
        counts: dict[str, int] = {}
        for q in chosen:
            k = str(getattr(q, key)) if key else "all"
            counts[k] = counts.get(k, 0) + 1
        dfile = reg[name].file_for(split, data_root)
        out["details"][name] = {
            "n_requested": s["n"], "n_selected": len(chosen), "stratify_by": key, "strata_counts": counts,
            "n_in_split": n_seen, "n_excluded": n_excl, "n_eligible": len(pool),
            "eligibility_rules": [r for r, _ in rules], "n_failing_rule": fails,
            "dataset_file_sha256": file_sha256(dfile) if dfile.exists() else None,
        }
    return out
