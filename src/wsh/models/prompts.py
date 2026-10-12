"""Answer prompts. The instruction text is IDENTICAL for every representation of a task, so
prompt overhead is controlled; only the evidence block differs. The answer format is two
plain-text lines that small models can produce; it is requested, not required (parsing is
tolerant and format deviations are tracked separately). No JSON is required."""

from __future__ import annotations

from .. import PROMPT_VERSION
from .interfaces import GenerationRequest

SYSTEM = "You answer using only the evidence you are given."

_QA = """Use only the evidence below to answer the question. Each evidence item has an ID such as [E1]. Items may be grouped into steps or followed by a list of relations between items.

Evidence:
{evidence}

Question: {question}

Reply in exactly two lines:
Answer: <short answer: a name, date, number, short phrase, or yes/no>
Evidence: <IDs of the items you used, e.g. E1, E2>
If the evidence is not sufficient, reply "Answer: insufficient evidence"."""

_VERIFY = """Use only the evidence below to judge the claim. Each evidence item has an ID such as [E1]. Items may be grouped into steps or followed by a list of relations between items.

Evidence:
{evidence}

Claim: {question}

Reply in exactly two lines:
Answer: <one of: {labels}>
Evidence: <IDs of the items you used, e.g. E1, E2>"""

ANSWER_PREFILL = "Answer:"


_ABSTENTION_LINE = '\nIf the evidence is not sufficient, reply "Answer: insufficient evidence".'
PROMPT_VARIANTS = ("qa-v2", "qa-v2-noabst")


def build_request(question, evidence_text: str, max_new_tokens: int, variant: str = "qa-v2") -> GenerationRequest:
    """`variant` qa-v2 = the frozen prompt; qa-v2-noabst (revision-1, separate factor) = the same prompt
    without its last line offering 'insufficient evidence' (QA only)."""
    if variant not in PROMPT_VARIANTS:
        raise ValueError(f"unknown prompt variant {variant}")
    if question.task == "qa":
        user = _QA.format(evidence=evidence_text, question=question.question)
        if variant == "qa-v2-noabst":
            assert user.endswith(_ABSTENTION_LINE)
            user = user[: -len(_ABSTENTION_LINE)]
    else:
        labels = ", ".join(lab.replace("_", " ") for lab in question.label_set)
        user = _VERIFY.format(evidence=evidence_text, question=question.question, labels=labels)
    return GenerationRequest(system=SYSTEM, user=user, max_new_tokens=max_new_tokens, purpose="answer",
                             prefill=ANSWER_PREFILL)


def prompt_version(variant: str = "qa-v2") -> str:
    return PROMPT_VERSION if variant == "qa-v2" else variant


class PromptCompositionError(RuntimeError):
    pass


def assert_prompt_composition(question, req: GenerationRequest, evidence_text: str, variant: str = "qa-v2") -> None:
    """Leakage guard: the prompt must be exactly the fixed template filled with the evidence
    block and the question/claim text, so no gold answer, label or annotation can enter it
    through any other channel. (The template itself is identical for every question and
    representation; gold answers can only be present inside the evidence, by design.)"""
    expected = build_request(question, evidence_text, req.max_new_tokens, variant)
    if (req.system, req.user, req.prefill) != (expected.system, expected.user, expected.prefill):
        raise PromptCompositionError(f"{question.uid}: prompt differs from template(evidence, question)")
