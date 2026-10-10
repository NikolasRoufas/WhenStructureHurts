"""Failure taxonomy. Every attempted example is classified; nothing leaves the denominator.

Flags (several may apply) and the primary failure (first applicable in PRECEDENCE):
    pipeline_error      evidence construction raised (before generation)
    context_overflow    prompt exceeded max_input_tokens; not generated
    generation_error    generator raised
    timeout             wall-clock limit hit
    empty_output        no text produced
    truncated           max_new_tokens reached (answer may still parse; scored if it does)
    unparseable         no answer could be extracted
    unparseable_verdict verification output maps to no label
    format_deviation    answer found only by fallback (no 'Answer:' field)
    invalid_citation    cites ids absent from the prompt (answer still scored)
    missing_citation    no citation at all
    abstained           model declined to answer
    wrong_answer        parsed, scored 0 on the primary metric
'answered' (coverage numerator) = an answer/verdict was parsed and the model did not abstain,
regardless of citations. Unanswered = hard failure or abstention; wrong = answered and scored 0.
"""

from __future__ import annotations

PRECEDENCE = [
    "pipeline_error", "context_overflow", "generation_error", "timeout", "empty_output", "unparseable",
    "unparseable_verdict", "abstained", "wrong_answer", "invalid_citation", "missing_citation", "truncated",
    "format_deviation",
]
HARD_FAILURES = {"pipeline_error", "context_overflow", "generation_error", "timeout", "empty_output",
                 "unparseable", "unparseable_verdict"}


def classify(*, pipeline_error: bool = False, finish_reason: str | None = None, text: str | None = None,
             parsed=None, task: str = "qa", primary_score: float | None = None) -> dict:
    flags: list[str] = []
    if pipeline_error:
        flags.append("pipeline_error")
    elif finish_reason == "skipped_overflow":
        flags.append("context_overflow")
    elif finish_reason == "error":
        flags.append("generation_error")
    else:
        if finish_reason == "time":
            flags.append("timeout")
        if finish_reason == "length":
            flags.append("truncated")
        if not (text or "").strip():
            flags.append("empty_output")
        elif parsed is None or parsed.answer is None:
            flags.append("unparseable")
        else:
            if task == "verification" and parsed.verdict is None:
                flags.append("unparseable_verdict")
            if parsed.answer_source == "fallback_line":
                flags.append("format_deviation")
            if parsed.invalid_cited:
                flags.append("invalid_citation")
            if not parsed.cited:
                flags.append("missing_citation")
            if parsed.abstained:
                flags.append("abstained")
            elif primary_score is not None and primary_score == 0.0 and not (set(flags) & HARD_FAILURES):
                flags.append("wrong_answer")
    # an abstention is a failure to answer, not an incorrect answer: it leaves coverage, and is
    # scored 0 in coverage-adjusted metrics like every other unanswered example
    answered = not (set(flags) & HARD_FAILURES) and "abstained" not in flags
    primary = next((f for f in PRECEDENCE if f in flags), "none")
    return {"flags": flags, "primary": primary, "answered": answered}
