"""Per-example evaluation: parsing, correctness, citations, coverage, groundedness, failures.

Unanswered examples receive 0 on every applicable correctness metric (so coverage-adjusted
means include them); metrics that do not apply to the example are None.
"""

from __future__ import annotations

from typing import Any

from ..data.schemas import EvidenceBundle, Question
from ..representations.serialization import SerializedEvidence
from .answer_metrics import exact_match, token_f1, verdict_accuracy, yes_no_normalize
from .failure_analysis import classify
from .grounding import citation_metrics, cited_text, evidence_coverage, grounded_lexical, nli_hypothesis
from .parsing import parse_output


def evaluate(q: Question, text: str | None, finish_reason: str | None, ser: SerializedEvidence | None,
             bundle: EvidenceBundle | None, grounding_nli=None, nli_threshold: float = 0.5,
             pipeline_error: bool = False) -> dict[str, Any]:
    ev: dict[str, Any] = {}
    parsed = None
    if not pipeline_error and ser is not None:
        parsed = parse_output(text or "", set(ser.id_map), q.label_set)
    pred = parsed.answer if parsed else None
    if q.task == "qa":
        p = yes_no_normalize(pred) if q.answer_type == "yes_no" else pred
        ev["em"] = exact_match(p, q.answers)
        ev["f1"] = token_f1(p, q.answers)
        primary = ev["em"]
    else:
        ev["verdict_acc"] = verdict_accuracy(parsed.verdict if parsed else None, q.answers[0])
        primary = ev["verdict_acc"]
    fail = classify(pipeline_error=pipeline_error, finish_reason=finish_reason, text=text, parsed=parsed,
                    task=q.task, primary_score=primary)
    if not fail["answered"]:
        for k in ("em", "f1", "verdict_acc"):
            if k in ev:
                ev[k] = 0.0
    if ser is not None and bundle is not None:
        cited = parsed.cited if parsed else []
        cm = citation_metrics(q, ser.id_map, cited if fail["answered"] else [], bundle)
        ev.update(cm)
        ev.update(evidence_coverage(q, ser.id_map, bundle))
        ev["citation_status"] = citation_status(parsed, fail["answered"])
        ev["evidence_sufficient"] = evidence_sufficient(ev)
        ctext = cited_text(ser.id_map, cited, bundle) if fail["answered"] else ""
        gl = grounded_lexical(pred if fail["answered"] else None, q, ctext)
        ev["grounded_lexical"] = gl if gl is not None else (0.0 if (q.task == "qa" and q.answer_type == "span") else None)
        ev["grounded_nli"] = None
        if grounding_nli is not None:
            hyp = nli_hypothesis(q, pred, parsed.verdict if parsed else None) if fail["answered"] else None
            if hyp and ctext:
                pr = grounding_nli.predict([(ctext, hyp)])[0]
                ev["grounded_nli_p"] = pr["entailment"]
                ev["grounded_nli"] = float(pr["entailment"] >= nli_threshold)
            elif fail["answered"] and hyp:
                ev["grounded_nli"] = 0.0  # answer without any valid cited evidence
    ev["abstained"] = bool(parsed and parsed.abstained)
    return {"parsed": parsed.to_dict() if parsed else None, "eval": ev, "failure": fail}


def citation_status(parsed, answered: bool) -> str:
    """Missing and invalid citations are different failures and are never merged."""
    if not answered or parsed is None:
        return "not_applicable"
    n_invalid = len(parsed.invalid_cited)  # parsed.cited lists every cited id, valid or not
    n_valid = len(parsed.cited) - n_invalid
    if n_valid == 0 and n_invalid == 0:
        return "none_given"
    if n_invalid == 0:
        return "all_valid"
    return "some_invalid" if n_valid else "all_invalid"


def evidence_sufficient(ev: dict[str, Any]) -> float | None:
    """Lexical sufficiency proxy of the SHOWN evidence: every gold support unit is shown, the
    answer string is present (span answers) and every decomposition sub-answer is present
    (MuSiQue/2Wiki). None when none of these is defined (e.g. no gold support annotation)."""
    parts = [ev.get(k) for k in ("support_coverage", "answer_in_evidence", "hop_answer_coverage")]
    parts = [x for x in parts if x is not None]
    return float(all(x >= 1.0 for x in parts)) if parts else None
