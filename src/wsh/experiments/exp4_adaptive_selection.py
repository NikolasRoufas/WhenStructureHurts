"""Experiment 4 - Evidence-Preserving Adaptive RAG: SCAFFOLDING ONLY.

Status: interfaces and offline evaluation are implemented; the method is NOT trained or
benchmarked. It is gated behind ``exp4.enabled`` (to be set only if Experiments 1-3 show a
reproducible effect). ``--plumbing-check`` runs the code path on existing records and labels
every output as a software check, not a result.

Pipeline (offline, over Experiment-1 records of the SAME questions under each representation):
    features(question, evidence store)  ->  selector  ->  chosen representation  ->  its outcome
Selectors:
    fixed:<R>  one representation for every question (baselines)
    rule       hand-written, interpretable thresholds (fixed a priori, not tuned on test data)
    logistic   one-vs-rest L2 logistic regression on deployable features, trained on the train
               split only (labels = best representation per training question by F1)
    oracle     per-question best representation using outcomes: DIAGNOSTIC UPPER BOUND, never
               deployable
Leakage controls: question-level train/test split by seeded hash; deployable features may not
use gold annotations or evaluation outcomes (enforced by name check); oracle is flagged.
Cost accounting: evidence tokens of the chosen representation + the cost of computing
features (relation-dependent features require building the graph, counted per question).
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any

from ..evaluation.statistics import bootstrap_ci, mean
from ..hashing import derive_seed
from ..text import content_tokens, extract_entities

FORBIDDEN_FEATURE_PATTERNS = re.compile(r"gold|answer|em$|f1|support_coverage|citation|correct|oracle|label", re.I)
DEPLOYABLE_FEATURES = [
    "q_tokens", "q_entities", "q_bridge_cues", "n_claims", "n_passages", "mean_extraction_conf",
    "n_edges", "mean_edge_conf", "n_contradicts", "evidence_tokens_R0",
]
RELATION_FEATURES = {"n_edges", "mean_edge_conf", "n_contradicts"}  # require graph construction


class LeakageError(RuntimeError):
    pass


def check_features(names: list[str]) -> None:
    bad = [n for n in names if FORBIDDEN_FEATURE_PATTERNS.search(n)]
    if bad:
        raise LeakageError(f"non-deployable features requested: {bad}")


def question_features(question: str, by_rep: dict[str, dict]) -> dict[str, float]:
    """Deployable features from the question text and the evidence store as recorded (claims,
    predicted/derived edges, token costs). Never reads eval fields or gold flags."""
    ev_any = next(iter(by_rep.values()))["evidence"]
    # Only MODEL-PREDICTED edges (R4P) are deployable; dataset-derived R4 edges would leak
    # annotation information into the selector.
    edges = by_rep["R4P"]["evidence"].get("edges", []) if "R4P" in by_rep else []
    claims = ev_any.get("claims", [])
    q_low = question.lower()
    f = {
        "q_tokens": float(len(content_tokens(question))),
        "q_entities": float(len(extract_entities(question))),
        "q_bridge_cues": float(sum(q_low.count(c) for c in (" of the ", " whose ", " that ", " who ", " which "))),
        "n_claims": float(len(claims)),
        "n_passages": float(len({c["claim_id"].split("#")[0] for c in claims})),
        "mean_extraction_conf": mean([c.get("extraction_confidence", 1.0) for c in claims]) or 0.0,
        "n_edges": float(len(edges)),
        "mean_edge_conf": mean([e["confidence"] for e in edges]) or 0.0,
        "n_contradicts": float(sum(e["relation"] == "CONTRADICTS" for e in edges)),
        "evidence_tokens_R0": float(by_rep.get("R0", {}).get("evidence", {}).get("evidence_tokens") or 0),
    }
    return f


def outcome(rec: dict) -> float:
    return float(rec["eval"].get("f1", rec["eval"].get("verdict_acc", 0.0)) or 0.0)


class FixedSelector:
    deployable = True

    def __init__(self, rep: str):
        self.rep = rep
        self.name = f"fixed:{rep}"

    def fit(self, X, y) -> None:
        return None

    def select(self, f: dict[str, float], available: list[str]) -> str:
        return self.rep if self.rep in available else available[0]


class RuleSelector:
    """A priori thresholds (not tuned): complex questions with confident, conflict-free graphs ->
    R4; complex otherwise -> R3; very large evidence -> R1; else R0."""
    deployable = True
    name = "rule"

    def fit(self, X, y) -> None:
        return None

    def select(self, f: dict[str, float], available: list[str]) -> str:
        complex_q = f["q_bridge_cues"] >= 2 or f["q_entities"] >= 3
        for rep, ok in (("R4", complex_q and f["n_contradicts"] == 0 and f["mean_edge_conf"] >= 0.7 and f["n_edges"] > 0),
                        ("R3", complex_q), ("R1", f["n_claims"] > 30), ("R0", True)):
            if ok and rep in available:
                return rep
        return available[0]


class LogisticSelector:
    """One-vs-rest L2 logistic regression with standardised features (pure numpy-free python)."""
    deployable = True
    name = "logistic"

    def __init__(self, features: list[str], l2: float = 1.0, epochs: int = 300, lr: float = 0.1):
        check_features(features)
        self.features, self.l2, self.epochs, self.lr = features, l2, epochs, lr
        self.models: dict[str, list[float]] = {}
        self.mu: list[float] = []
        self.sd: list[float] = []

    def _x(self, f: dict[str, float]) -> list[float]:
        return [1.0] + [(f[k] - m) / s for k, m, s in zip(self.features, self.mu, self.sd)]

    def fit(self, X: list[dict[str, float]], y: list[str]) -> None:
        if not X:
            raise ValueError("no training data")
        cols = [[x[k] for x in X] for k in self.features]
        self.mu = [sum(c) / len(c) for c in cols]
        self.sd = [max(1e-6, math.sqrt(sum((v - m) ** 2 for v in c) / len(c))) for c, m in zip(cols, self.mu)]
        Z = [self._x(x) for x in X]
        for cls in sorted(set(y)):
            t = [1.0 if v == cls else 0.0 for v in y]
            w = [0.0] * len(Z[0])
            for _ in range(self.epochs):
                g = [0.0] * len(w)
                for z, ti in zip(Z, t):
                    p = 1 / (1 + math.exp(-sum(a * b for a, b in zip(w, z))))
                    for j in range(len(w)):
                        g[j] += (p - ti) * z[j]
                w = [wj - self.lr * (gj / len(Z) + (self.l2 * wj / len(Z) if j else 0.0)) for j, (wj, gj) in enumerate(zip(w, g))]
            self.models[cls] = w

    def select(self, f: dict[str, float], available: list[str]) -> str:
        z = self._x(f)
        scored = [(sum(a * b for a, b in zip(self.models[r], z)), r) for r in available if r in self.models]
        return max(scored)[1] if scored else available[0]


class OracleSelector:
    deployable = False  # diagnostic upper bound only
    name = "oracle"

    def __init__(self):
        self.outcomes: dict[str, dict[str, float]] = {}

    def fit(self, X, y) -> None:
        return None

    def select_for(self, qid: str, available: list[str], costs: dict[str, float]) -> str:
        o = self.outcomes[qid]
        return max(available, key=lambda r: (o[r], -costs.get(r, 0.0)))


def split_questions(qids: list[str], train_fraction: float, seed: int) -> tuple[list[str], list[str]]:
    train = [q for q in qids if (derive_seed("exp4-split", seed, q) % 10_000) / 10_000 < train_fraction]
    test = [q for q in qids if q not in set(train)]
    if set(train) & set(test):
        raise LeakageError("train/test overlap")
    return train, test


def evaluate_selectors(records: list[dict], selectors: list[str], train_fraction: float, seed: int,
                       protocol: str = "A") -> dict[str, Any]:
    by_q: dict[str, dict[str, dict]] = defaultdict(dict)
    questions: dict[str, str] = {}
    for r in records:
        c = r.get("condition", {})
        if r.get("unavailable") or c.get("protocol") != protocol or "eval" not in r:
            continue
        if c.get("representation") == "R2" and c.get("shuffle_seed") not in (0, None):
            continue
        by_q[r["question_uid"]][c["representation"]] = r
        questions[r["question_uid"]] = r["question"]
    reps = sorted({rep for d in by_q.values() for rep in d})
    qids = sorted(q for q, d in by_q.items() if set(d) == set(reps))  # complete cases only
    train, test = split_questions(qids, train_fraction, seed)
    feats = {q: question_features(questions[q], by_q[q]) for q in qids}
    costs = {q: {rep: float(by_q[q][rep]["evidence"].get("evidence_tokens") or 0) for rep in reps} for q in qids}
    best = {q: max(reps, key=lambda rep: (outcome(by_q[q][rep]), -costs[q][rep])) for q in qids}
    out: dict[str, Any] = {"n_questions_complete": len(qids), "n_train": len(train), "n_test": len(test),
                           "representations": reps, "selectors": {}}
    for name in selectors:
        if name.startswith("fixed:"):
            sel = FixedSelector(name.split(":", 1)[1])
        elif name == "rule":
            sel = RuleSelector()
        elif name == "logistic":
            sel = LogisticSelector(DEPLOYABLE_FEATURES)
        elif name == "oracle":
            sel = OracleSelector()
            sel.outcomes = {q: {rep: outcome(by_q[q][rep]) for rep in reps} for q in qids}
        else:
            raise ValueError(name)
        if isinstance(sel, LogisticSelector):
            if len({best[q] for q in train}) < 2:
                out["selectors"][name] = {"status": "not trained: fewer than two classes in train split"}
                continue
            sel.fit([feats[q] for q in train], [best[q] for q in train])
        scores, toks, picks = [], [], defaultdict(int)
        for q in test:
            rep = sel.select_for(q, reps, costs[q]) if isinstance(sel, OracleSelector) else sel.select(feats[q], reps)
            picks[rep] += 1
            scores.append(outcome(by_q[q][rep]))
            toks.append(costs[q][rep])
        out["selectors"][name] = {
            "deployable": sel.deployable, "n_test": len(test), "mean_outcome_f1": mean(scores),
            "ci": bootstrap_ci(scores), "mean_evidence_tokens": mean(toks), "picks": dict(picks),
            # feature cost: these selectors need the predicted graph for every test question
            "graph_builds_required": len(test) if isinstance(sel, (RuleSelector, LogisticSelector)) else 0,
        }
    sources = {r["condition"].get("evidence_source") for q in qids for r in by_q[q].values()}
    if "gold" in sources:
        out["warning"] = ("features computed on GOLD evidence records: not an estimate of deployable performance; "
                          "use Experiment-1 records with evidence_source=retrieved")
    return out
