"""Citation and evidence metrics, and groundedness.

Citation metrics are computed at two granularities so representations with different unit
sizes stay comparable:
  * unit level   : precision = cited items overlapping a gold unit / valid cited items;
                   recall    = gold units overlapped by a cited item / gold units.
                   (A passage-level R0 item overlaps every gold sentence inside it, so R0 unit
                   recall is structurally easier: compare with passage-level recall.)
  * passage level: gold passages hit by cited items / gold passages.
Corrupted claims never count as covering gold evidence.

Evidence coverage (of what was shown to the model, after any budget truncation):
  * support_coverage : fraction of gold units overlapped by faithful shown evidence
  * content_recall   : mean over gold units of the fraction of their content tokens present
                       in the faithful shown items that overlap them (catches lossy
                       extraction where spans overlap but facts are dropped)
  * answer_in_evidence: gold answer string occurs in faithful shown evidence (span answers)
  * hop_answer_coverage: fraction of decomposition sub-answers present (MuSiQue/2Wiki)

Groundedness (documented approximations, reported separately):
  * grounded_lexical: normalised answer occurs in the text of the cited items (span answers)
  * grounded_nli    : P(entailment) of hypothesis "The answer to the question '<q>' is <a>."
                      (QA) or the claim itself with the predicted verdict (verification),
                      premise = concatenated cited items; thresholded. Uses a DIFFERENT NLI
                      model from the relation classifier to avoid circularity.
"""

from __future__ import annotations

from typing import Any

from ..data.provenance import gold_units
from ..data.schemas import EvidenceBundle, Question, Span
from ..text import contains_phrase, content_tokens


def _faithful_spans(item: dict[str, Any], claim_map) -> list[Span]:
    spans = [Span(**s) for s in item["spans"]]
    cids = item["claim_ids"]
    if len(cids) == len(spans):
        return [s for c, s in zip(cids, spans) if not (claim_map.get(c) and claim_map[c].is_corrupted)]
    return [] if item.get("corrupted") else spans


def _item_texts(item: dict[str, Any], claim_map) -> list[str]:
    return [claim_map[c].text for c in item["claim_ids"] if c in claim_map and not claim_map[c].is_corrupted]


def citation_metrics(q: Question, id_map: dict[str, dict], cited: list[str], bundle: EvidenceBundle) -> dict[str, Any]:
    cm = bundle.claim_map()
    valid = [c for c in cited if c in id_map]
    units = gold_units(q)
    gold_p = set(q.gold_passage_ids())
    out: dict[str, Any] = {"n_cited": len(cited), "n_valid_cited": len(valid), "n_invalid_cited": len(cited) - len(valid),
                           "citation_validity": (len(valid) / len(cited)) if cited else None}
    if not units:
        out.update({"citation_precision": None, "citation_recall": None, "citation_recall_passage": None})
        return out
    item_hits = []
    covered = [False] * len(units)
    p_hit = set()
    for c in valid:
        sp = _faithful_spans(id_map[c], cm)
        hit = False
        for k, u in enumerate(units):
            if any(s.overlaps(u) for s in sp):
                covered[k] = True
                hit = True
        item_hits.append(hit)
        p_hit |= {s.passage_id for s in sp} & gold_p
    out["citation_precision"] = (sum(item_hits) / len(valid)) if valid else None
    out["citation_recall"] = sum(covered) / len(units)
    out["citation_recall_passage"] = len(p_hit) / len(gold_p) if gold_p else None
    return out


def _passage_order_segments(spans: list[Span], bundle: EvidenceBundle, q: Question) -> list[str]:
    by_p: dict[str, set[tuple[int, int]]] = {}
    for s in spans:
        by_p.setdefault(s.passage_id, set()).add((s.start, s.end))
    out = []
    for pid, offs in by_p.items():
        p = bundle.passages.get(pid) or next((x for x in q.passages if x.passage_id == pid), None)
        if p is not None:
            out.append(" ".join(p.text[a:b] for a, b in sorted(offs)))
    return out


def evidence_coverage(q: Question, id_map: dict[str, dict], bundle: EvidenceBundle) -> dict[str, Any]:
    cm = bundle.claim_map()
    units = gold_units(q)
    shown_spans: list[Span] = []
    texts: list[str] = []
    for item in id_map.values():
        shown_spans += _faithful_spans(item, cm)
        texts += _item_texts(item, cm) or ([] if item.get("corrupted") else [])
    # passage-level items (R0) carry sentence spans but may have no bundle claims for them
    for item in id_map.values():
        if not _item_texts(item, cm) and not item.get("corrupted"):
            for s in item["spans"]:
                p = bundle.passages.get(s["passage_id"])
                if p is not None:
                    texts.append(p.text[s["start"]:s["end"]])
    joined = " ".join(texts)
    # Presence checks must not depend on display order (R1 vs R2 differ only in order): test each
    # shown text on its own and each passage's shown spans re-joined in original passage order.
    segments = texts + _passage_order_segments(shown_spans, bundle, q)
    out: dict[str, Any] = {}
    if units:
        cov = [any(s.overlaps(u) for s in shown_spans) for u in units]
        out["support_coverage"] = sum(cov) / len(units)
        shown_tok = set(content_tokens(joined))
        recalls = []
        for u in units:
            p = q.passage(u.passage_id)
            ut = content_tokens(p.text[u.start:u.end])
            recalls.append(sum(t in shown_tok for t in ut) / len(ut) if ut else 1.0)
        out["content_recall"] = sum(recalls) / len(recalls)
    else:
        out["support_coverage"] = out["content_recall"] = None
    if q.task == "qa" and q.answer_type == "span":
        out["answer_in_evidence"] = float(any(contains_phrase(t, a) for t in segments for a in q.answers))
    else:
        out["answer_in_evidence"] = None
    subs = [s.sub_answer for s in q.reasoning_steps if s.sub_answer]
    out["hop_answer_coverage"] = (sum(any(contains_phrase(t, a) for t in segments) for a in subs) / len(subs)) if subs else None
    return out


def cited_text(id_map: dict[str, dict], cited: list[str], bundle: EvidenceBundle) -> str:
    cm = bundle.claim_map()
    parts = []
    for c in cited:
        if c not in id_map:
            continue
        t = _item_texts(id_map[c], cm)
        if not t:
            for s in id_map[c]["spans"]:
                p = bundle.passages.get(s["passage_id"])
                if p is not None:
                    t.append(p.text[s["start"]:s["end"]])
        parts += t
    return " ".join(parts)


def grounded_lexical(answer: str | None, q: Question, text: str) -> float | None:
    if answer is None or q.task != "qa" or q.answer_type != "span":
        return None
    return float(bool(text) and contains_phrase(text, answer))


def nli_hypothesis(q: Question, answer: str | None, verdict: str | None) -> str | None:
    if q.task == "qa":
        return None if answer is None else f'The answer to the question "{q.question}" is {answer}.'
    if verdict in ("SUPPORTS", "SUPPORTED"):
        return q.question
    return None  # refutation/NEI groundedness is not expressible as a single entailment check
