"""Experiment 1 evaluation protocols (replace the retired 'min_matched' end-truncation mode).

Protocol A - information-controlled
    Every representation is built from the SAME fact set (the bundle's sentence-unit claims).
    For each record we store the exact facts (claim id -> text digest) and spans shown, the
    structural information a representation adds on top of the facts (e.g. gold reasoning
    order, gold dependency edges), and overhead = evidence tokens - content tokens. The fact
    sets of all representations of a question are checked to be identical; a mismatch raises
    ``InformationEquivalenceViolation`` (recorded as a pipeline error, never silently kept).

Protocol B - budget-controlled
    A representation-independent ranking of facts (``rank_facts``) is computed once per
    question. Policy 'shared' keeps the largest prefix of that ranking that fits the budget in
    EVERY representation, so all representations show the same facts and the cost of
    verbose formats is paid by all of them. Policy 'per_representation' keeps, for each
    representation, the largest prefix that fits its own rendering, so verbose formats keep
    fewer facts (the accuracy-cost trade-off). Facts are removed whole, never mid-sentence;
    every removal is logged with whether it was gold support or answer-bearing; whether the
    required (gold-support) facts fit at all is recorded per representation.
"""

from __future__ import annotations

from typing import Any, Callable

from ..data.schemas import AnnotationStatus, Edge, EvidenceBundle, Question
from ..hashing import stable_hash
from ..text import contains_phrase
from .serialization import Layout, SerializedEvidence, render


class InformationEquivalenceViolation(RuntimeError):
    pass


class BudgetViolation(RuntimeError):
    pass


# --- edge strata (Section 2 of the pilot protocol) ---

STRATUM_ORDER = ["A_human_verified", "B_dataset_supplied", "B_derived_exact_anchor", "C_derived_fallback_anchor",
                 "D_model_predicted", "corrupted"]


def edge_stratum(e: Edge) -> str:
    if e.status == AnnotationStatus.HUMAN_VERIFIED:
        return "A_human_verified"
    if e.status == AnnotationStatus.MODEL_PREDICTED:
        return "D_model_predicted"
    if e.status == AnnotationStatus.CORRUPTED:
        return "corrupted"
    if e.meta.get("anchor_match") == "fallback":
        return "C_derived_fallback_anchor"
    if e.status == AnnotationStatus.DATASET_SUPPLIED:
        return "B_dataset_supplied"
    return "B_derived_exact_anchor"


def bundle_edge_stratum(b: EvidenceBundle) -> str:
    """Weakest stratum among a bundle's edges ('no_edges' if it has none)."""
    if not b.edges:
        return "no_edges"
    return max((edge_stratum(e) for e in b.edges), key=STRATUM_ORDER.index)


# --- what each representation shows beyond the facts ---

def added_information(rep: str, b: EvidenceBundle) -> list[str]:
    """Structural information a representation adds on top of the shared fact set. R0/R1 use
    the dataset's own context order; R2 a random order; R3/R4/R5 add annotation-derived
    structure, named here with the status of the annotation it comes from."""
    edge_st = sorted({edge_stratum(e) for e in b.edges}) or ["none"]
    if rep in ("R0", "R1"):
        return []
    if rep == "R2":
        return ["order:random"]
    if rep == "R3":
        return [f"step_grouping_and_order:{b.path_status.value}"]
    if rep == "R5":
        return [f"passage_order_from_edges:{'+'.join(edge_st)}"]
    if rep in ("R4", "R4P"):
        return [f"passage_order_from_edges:{'+'.join(edge_st)}", f"explicit_relations:{'+'.join(edge_st)}"]
    from .relation_controls import ALL_CONTROL_REPS
    if rep in ALL_CONTROL_REPS:
        spec = ALL_CONTROL_REPS[rep]
        out = [f"order_from_{spec['order']}_graph"]
        if spec["relations"] != "none":
            out.append(f"explicit_relations:{spec['relations']}:{'+'.join(edge_st)}")
        return out
    return [f"unknown_representation:{rep}"]


def layout_facts(layout: Layout) -> dict[str, str]:
    """claim id -> text for every fact a layout shows (R0 units are per-sentence aligned)."""
    out: dict[str, str] = {}
    for u in layout.units:
        if len(u.claim_ids) == len(u.texts):
            out.update(zip(u.claim_ids, u.texts))
        else:  # passage without sentence segmentation: the whole passage is one fact
            for pid, t in zip(u.passage_ids, u.texts):
                out[f"{pid}#full"] = t
    return out


def information_profile(rep: str, layout: Layout, ser: SerializedEvidence, b: EvidenceBundle, q: Question,
                        count_tokens: Callable[[str], int]) -> dict[str, Any]:
    facts = layout_facts(layout)
    canonical = [c.claim_id for c in b.claims if c.claim_id in facts] + sorted(set(facts) - b.claim_map().keys())
    content = "\n".join(facts[c] for c in canonical)
    content_tokens = count_tokens(content)
    ev_tokens = ser.evidence_tokens if ser.evidence_tokens is not None else count_tokens(ser.text)
    cm = b.claim_map()
    return {
        "fact_ids": canonical,
        "fact_digest": stable_hash(sorted(facts.items())),
        "n_facts": len(facts),
        "added_information": added_information(rep, b),
        "content_tokens": content_tokens,
        "evidence_tokens": ev_tokens,
        "overhead_tokens": ev_tokens - content_tokens,
        "context_dependent_facts": sorted(c for c in facts if c in cm and _context_dependent(cm[c].text)),
        "passage_chars_outside_facts": _uncovered_chars(b),
        "edge_stratum": bundle_edge_stratum(b) if rep in ("R4", "R4P", "R5") else None,
    }


_PRONOUN_START = ("it ", "its ", "he ", "she ", "his ", "her ", "they ", "their ", "this ", "these ", "those ",
                  "the film ", "the album ", "the song ", "the company ", "the team ")


def _context_dependent(text: str) -> bool:
    """Heuristic: a sentence opening with a pronoun/definite back-reference needs its
    neighbours to be interpreted, so claim-level (reordered) layouts can lose its referent."""
    return text.strip().lower().startswith(_PRONOUN_START)


def _uncovered_chars(b: EvidenceBundle) -> int:
    """Non-whitespace passage characters not inside any shown sentence span (text the claim
    representations cannot show; R0 renders the same sentences, so it lacks them too)."""
    n = 0
    for pid, p in b.passages.items():
        spans = sorted((s.start, s.end) for c in b.claims if c.passage_id == pid for s in c.spans[:1])
        covered = [False] * len(p.text)
        for s, e in spans:
            for i in range(s, min(e, len(p.text))):
                covered[i] = True
        n += sum(1 for i, ch in enumerate(p.text) if not covered[i] and not ch.isspace())
    return n


def check_equivalence(profiles: dict[str, dict]) -> None:
    digests = {name: p["fact_digest"] for name, p in profiles.items()}
    if len(set(digests.values())) > 1:
        ref = next(iter(profiles))
        diff = {n: sorted(set(p["fact_ids"]) ^ set(profiles[ref]["fact_ids"])) for n, p in profiles.items()
                if p["fact_digest"] != profiles[ref]["fact_digest"]}
        raise InformationEquivalenceViolation(f"fact sets differ from {ref}: {diff}")


# --- Protocol B ---

def restrict_bundle(b: EvidenceBundle, keep: set[str]) -> EvidenceBundle:
    """Sub-bundle with only the kept claims; edges, path steps and conflicts touching removed
    claims are dropped; passage renderings show only kept sentences."""
    out = b.model_copy(deep=True)
    out.claims = [c for c in out.claims if c.claim_id in keep]
    out.edges = [e for e in out.edges if e.source in keep and e.target in keep]
    if out.path:
        for st in out.path:
            st.claim_ids = [c for c in st.claim_ids if c in keep]
        out.path = [st for st in out.path if st.claim_ids] or None
    for cs in out.conflicts:
        cs.claim_ids = [c for c in cs.claim_ids if c in keep]
    out.conflicts = [cs for cs in out.conflicts if len(cs.claim_ids) > 1]
    live = {c.passage_id for c in out.claims}
    out.passage_order = [p for p in out.passage_order if p in live]
    out.passages = {p: v for p, v in out.passages.items() if p in live}
    out.origin = {**out.origin, "passage_text": "in_scope_sentences_only", "restricted_to_n_facts": len(keep)}
    return out


def rank_facts(b: EvidenceBundle, q: Question, selection: str) -> list[str]:
    """Representation-independent fact priority.

    'relevance'     BM25 of (title + sentence) against the question; ties by context order.
                    Uses no gold information (deployable).
    'support_first' gold-supporting facts first (context order), then by relevance. Uses gold
                    support labels: an oracle-selection analysis, flagged as such in records.
    """
    from ..data.schemas import Passage
    from ..retrieval.bm25 import bm25_scores

    claims = b.claims
    docs = [Passage(passage_id=c.claim_id, title=c.title, text=f"{c.title}. {c.text}", sentence_spans=[(0, 1)],
                    segmentation="tmp", segmentation_status=c.status, position=0, lineage_id=c.lineage_id)
            for c in claims]
    s = bm25_scores(q.question, docs) if docs else []
    order = sorted(range(len(claims)), key=lambda i: (-s[i], i))
    if selection == "support_first":
        order = sorted(order, key=lambda i: not claims[i].is_gold_support)  # stable
    elif selection != "relevance":
        raise ValueError(f"unknown selection policy {selection}")
    return [claims[i].claim_id for i in order]


def parse_budget(spec: str, content_tokens_full: int) -> int:
    """'abs:<n>' (fixed tokens) or 'content:<f>' (f x content tokens of the full fact set)."""
    kind, _, v = spec.partition(":")
    if kind == "abs":
        return int(v)
    if kind == "content":
        return max(1, int(float(v) * content_tokens_full))
    raise ValueError(f"unknown budget spec {spec!r} (use abs:<n> or content:<fraction>)")


LayoutFn = Callable[[EvidenceBundle], Layout]
Variant = tuple[EvidenceBundle, LayoutFn]  # a representation's own bundle (same claims) + layout builder


def _fits(v: Variant, keep: list[str], budget: int, count_tokens) -> tuple[bool, tuple]:
    b, make = v
    sub = restrict_bundle(b, set(keep))
    lay = make(sub) if sub.claims else Layout(make(b).rep, [], show_source=b.provenance_visible)
    ser = render(lay)
    ser.evidence_tokens = count_tokens(ser.text)
    return ser.evidence_tokens <= budget, (sub, lay, ser)


def largest_fitting_prefix(variants: dict[str, Variant], ranking: list[str], budget: int, count_tokens) -> int:
    """Largest k such that the first k ranked facts fit the budget in every given variant."""
    for k in range(len(ranking), -1, -1):
        if all(_fits(v, ranking[:k], budget, count_tokens)[0] for v in variants.values()):
            return k
    return 0


def budget_select(variants: dict[str, Variant], q: Question, budget: int, ranking: list[str], policy: str,
                  count_tokens) -> dict[str, tuple[EvidenceBundle, Layout, SerializedEvidence, dict]]:
    """Return per representation (sub-bundle, layout, serialized evidence, accounting)."""
    if policy == "shared":
        k_shared = largest_fitting_prefix(variants, ranking, budget, count_tokens)
        ks = {name: k_shared for name in variants}
    elif policy == "per_representation":
        ks = {name: largest_fitting_prefix({name: v}, ranking, budget, count_tokens) for name, v in variants.items()}
    else:
        raise ValueError(f"unknown budget policy {policy}")
    out = {}
    for name, v in variants.items():
        b = v[0]
        cm = b.claim_map()
        required = [c for c in ranking if cm[c].is_gold_support]
        answer_bearing = {c for c in ranking if _answer_bearing(cm[c].text, q)}
        keep = ranking[:ks[name]]
        ok, (sub, lay, ser) = _fits(v, keep, budget, count_tokens)
        if not ok:
            raise BudgetViolation(f"{name}: {ser.evidence_tokens} tokens > budget {budget}")
        kept = set(keep)
        dropped = [c for c in ranking if c not in kept]
        ser.budget = budget
        ser.dropped = [{"claim_id": c, "kind": "fact", "gold_support": cm[c].is_gold_support,
                        "answer_bearing": c in answer_bearing} for c in dropped]
        acct = {
            "budget": budget, "policy": policy, "n_facts_total": len(ranking), "n_facts_kept": len(kept),
            "n_facts_dropped": len(dropped), "truncated": bool(dropped),
            "required_facts_total": len(required), "required_facts_dropped": sum(c not in kept for c in required),
            "required_facts_fit_budget": _fits(v, required, budget, count_tokens)[0] if required else None,
            "answer_bearing_facts_total": len(answer_bearing),
            "answer_bearing_facts_dropped": sum(c not in kept for c in answer_bearing),
            "kept_fact_digest": stable_hash(sorted(kept)),
        }
        out[name] = (sub, lay, ser, acct)
    return out


def _answer_bearing(text: str, q: Question) -> bool:
    return q.task == "qa" and q.answer_type == "span" and any(contains_phrase(text, a) for a in q.answers)

