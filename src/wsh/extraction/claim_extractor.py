"""Claim extractors. All produce ``Claim`` objects under one schema (paper Sec. 3.4).

* ``sentence``    : one claim per source sentence (dataset or regex segmentation). Text equals
                    the source span exactly. Not atomic; used as the *verified* claim unit.
* ``rule_atomic`` : deterministic split of a sentence on ';' and ', and ' (crude baseline).
* ``llm``         : the generator rewrites each sentence into short standalone facts.
                    Output is MODEL_PREDICTED. Each claim is checked against its source sentence
                    (lexical support); unsupported claims are kept but flagged, never repaired.

Provenance of atomic claims is the full source-sentence span (sub-sentence localisation is
not attempted).
"""

from __future__ import annotations

import re
from typing import Iterable

from ..data.provenance import atomic_claim_id, claim_overlaps_gold, sentence_claim_id, sentence_span
from ..data.schemas import AnnotationStatus, Claim, Passage, Span
from ..models.interfaces import GenerationRequest
from ..text import extract_entities, lexical_support

_NEG = re.compile(r"\b(not|never|no|n't|neither|nor|without)\b", re.IGNORECASE)

EXTRACTION_PROMPT_VERSION = "extract-v2"  # v2: assistant prefilled with "- "
EXTRACTION_SYSTEM = "You split sentences into short, simple facts."
EXTRACTION_USER = (
    "Rewrite the sentence below as a list of short facts.\n"
    "Rules: each fact is one complete sentence; name the subject instead of using pronouns; "
    "use only information stated in the sentence; write one fact per line starting with \"- \".\n\n"
    "Topic: {title}\nSentence: {sentence}\n\nFacts:"
)


def sentence_claim(p: Passage, i: int, gold_units: list[Span], status: AnnotationStatus | None = None) -> Claim:
    sp = sentence_span(p, i)
    text = p.text[sp.start:sp.end]
    c = Claim(
        claim_id=sentence_claim_id(p.passage_id, i), text=text, spans=[sp], passage_id=p.passage_id,
        title=p.title, lineage_id=p.lineage_id, status=status or p.segmentation_status,
        extraction_method=f"sentence:{p.segmentation}", extraction_confidence=1.0,
        negated=bool(_NEG.search(text)), entities=extract_entities(text), timestamp=p.timestamp,
        meta={"sentence_index": i},
    )
    c.is_gold_support = claim_overlaps_gold(c, gold_units)
    return c


def _selected(p: Passage, sentence_filter: dict[str, list[int]] | None) -> Iterable[int]:
    if sentence_filter is None or p.passage_id not in sentence_filter:
        return range(p.n_sentences)
    return sorted(set(sentence_filter[p.passage_id]))


class SentenceClaimExtractor:
    method = "sentence"

    def extract(self, passages: list[Passage], gold_units: list[Span],
                sentence_filter: dict[str, list[int]] | None = None) -> tuple[list[Claim], dict]:
        claims = [sentence_claim(p, i, gold_units) for p in passages for i in _selected(p, sentence_filter)
                  if p.sentence(i).strip()]
        return claims, {"method": self.method, "n_sentences": len(claims)}


class RuleAtomicExtractor:
    method = "rule_atomic"
    _SPLIT = re.compile(r";\s+|,\s+and\s+(?=[a-z])")

    def extract(self, passages: list[Passage], gold_units: list[Span],
                sentence_filter: dict[str, list[int]] | None = None) -> tuple[list[Claim], dict]:
        out: list[Claim] = []
        for p in passages:
            for i in _selected(p, sentence_filter):
                base = sentence_claim(p, i, gold_units)
                parts = [x.strip() for x in self._SPLIT.split(base.text) if len(x.split()) >= 3]
                if len(parts) <= 1:
                    out.append(base.model_copy(update={"extraction_method": "rule_atomic:unsplit"}))
                    continue
                for k, t in enumerate(parts):
                    out.append(base.model_copy(update={
                        "claim_id": atomic_claim_id(p.passage_id, i, k), "text": t,
                        "status": AnnotationStatus.DETERMINISTIC_DERIVED, "extraction_method": "rule_atomic",
                        "negated": bool(_NEG.search(t)), "entities": extract_entities(t),
                        "is_gold_support": base.is_gold_support,
                    }))
        return out, {"method": self.method}


def parse_fact_lines(text: str, limit: int) -> list[str]:
    facts = []
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[-*•]|\d+[.)])\s*(.+?)\s*$", line)
        if m:
            f = m.group(1).strip()
            if len(f.split()) >= 2 and f not in facts:
                facts.append(f)
    return facts[:limit]


class LLMClaimExtractor:
    method = "llm"

    def __init__(self, generator, max_new_tokens: int = 96, min_lexical_support: float = 0.6,
                 on_empty: str = "drop", max_claims_per_sentence: int = 6):
        self.gen = generator
        self.max_new_tokens = max_new_tokens
        self.min_support = min_lexical_support
        self.on_empty = on_empty
        self.limit = max_claims_per_sentence

    def extract(self, passages: list[Passage], gold_units: list[Span],
                sentence_filter: dict[str, list[int]] | None = None) -> tuple[list[Claim], dict]:
        out: list[Claim] = []
        stats = {"method": self.method, "model": self.gen.model_id, "revision": self.gen.revision,
                 "prompt_version": EXTRACTION_PROMPT_VERSION, "n_sentences": 0, "n_calls_uncached": 0,
                 "n_empty": 0, "n_claims": 0, "n_unsupported": 0, "n_truncated": 0, "latency_s": 0.0,
                 "input_tokens": 0, "output_tokens": 0}
        for p in passages:
            for i in _selected(p, sentence_filter):
                src = p.sentence(i)
                if not src.strip():
                    continue
                stats["n_sentences"] += 1
                base = sentence_claim(p, i, gold_units)
                res = self.gen.generate(GenerationRequest(
                    system=EXTRACTION_SYSTEM, user=EXTRACTION_USER.format(title=p.title, sentence=src),
                    max_new_tokens=self.max_new_tokens, purpose="claim_extraction", prefill="- "))
                stats["latency_s"] += res.latency_s
                stats["input_tokens"] += res.input_tokens
                stats["output_tokens"] += res.output_tokens
                stats["n_calls_uncached"] += int(not res.cached)
                stats["n_truncated"] += int(res.finish_reason == "length")
                facts = parse_fact_lines(res.text, self.limit) if res.finish_reason != "error" else []
                if not facts:
                    stats["n_empty"] += 1
                    if self.on_empty == "keep_sentence":
                        out.append(base.model_copy(update={"extraction_method": "llm:fallback_sentence"}))
                    continue
                for k, f in enumerate(facts):
                    sup = lexical_support(f, f"{p.title} {src}")
                    unsupported = sup < self.min_support
                    stats["n_unsupported"] += int(unsupported)
                    out.append(base.model_copy(update={
                        "claim_id": atomic_claim_id(p.passage_id, i, k), "text": f,
                        "status": AnnotationStatus.MODEL_PREDICTED, "extraction_method": "llm",
                        "extraction_confidence": round(sup, 4), "negated": bool(_NEG.search(f)),
                        "entities": extract_entities(f),
                        "meta": {"sentence_index": i, "lexical_support": round(sup, 4),
                                 "unsupported": unsupported, "finish_reason": res.finish_reason},
                    }))
                    stats["n_claims"] += 1
        return out, stats


def build_extractor(method: str, generator=None, cfg=None):
    if method == "sentence":
        return SentenceClaimExtractor()
    if method == "rule_atomic":
        return RuleAtomicExtractor()
    if method == "llm":
        if generator is None:
            raise ValueError("llm extraction requires a generator")
        return LLMClaimExtractor(generator, cfg.max_new_tokens, cfg.min_lexical_support, cfg.on_empty,
                                 cfg.max_claims_per_sentence)
    raise ValueError(method)
