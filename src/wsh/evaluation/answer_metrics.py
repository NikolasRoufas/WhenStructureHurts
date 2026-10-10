"""Answer correctness: SQuAD-style EM / token F1 (max over gold aliases) and verdict accuracy."""

from __future__ import annotations

from collections import Counter

from ..text import answer_tokens, normalize_answer


def exact_match(pred: str | None, golds: list[str]) -> float:
    if pred is None:
        return 0.0
    p = normalize_answer(pred)
    return float(any(p == normalize_answer(g) for g in golds))


def token_f1(pred: str | None, golds: list[str]) -> float:
    if pred is None:
        return 0.0
    best = 0.0
    pt = answer_tokens(pred)
    for g in golds:
        gt = answer_tokens(g)
        # yes/no/noanswer must match exactly (SQuAD/HotpotQA convention)
        if normalize_answer(g) in {"yes", "no"} or normalize_answer(pred) in {"yes", "no"}:
            best = max(best, float(normalize_answer(pred) == normalize_answer(g)))
            continue
        common = Counter(pt) & Counter(gt)
        same = sum(common.values())
        if same == 0:
            continue
        prec, rec = same / len(pt), same / len(gt)
        best = max(best, 2 * prec * rec / (prec + rec))
    return best


def yes_no_normalize(pred: str | None) -> str | None:
    """Map 'Yes, they were.' -> 'yes' for yes/no questions (leading token only)."""
    if pred is None:
        return None
    t = normalize_answer(pred).split()
    return t[0] if t and t[0] in {"yes", "no"} else pred


def verdict_accuracy(verdict: str | None, gold: str) -> float:
    return float(verdict is not None and verdict == gold)
