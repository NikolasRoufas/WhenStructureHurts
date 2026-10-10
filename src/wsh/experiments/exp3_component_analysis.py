"""Experiment 3 - component-level replacement (which transformation causes failures?).

               claims      relations   selection
    oracle     verified    verified    verified
    C1         predicted   verified    verified
    C2         verified    predicted   verified
    C3         verified    verified    predicted
    C4         predicted   predicted   predicted

"Verified" means one of the statuses in exp3.accepted_statuses (recorded per record): by default
dataset-supplied or deterministically derived, i.e. NOT verified by this project's annotators.
With ``verified_annotations`` configured, questions with a human-verified record use those
edges/order (stratum A). Every record carries the oracle's edge stratum
(A human-verified / B exact-anchor derived / C fallback-anchor derived), and analyses keep the
strata separate. C2 agreement with HotpotQA-derived edges is suppressed (same heuristic).

* verified claims    : sentence units of the gold passages (dataset text)
* predicted claims   : LLM atomic claims extracted from the same passages (C1) or from
                       retrieved passages (C4)
* verified relations : DEPENDS_ON edges derived from the dataset reasoning annotation. For C1
                       they are projected onto predicted claims through provenance (edge
                       lost if extraction produced no claim for an endpoint sentence).
                       Other relation types have no verified annotation.
* predicted relations: RelationClassifier (NLI + heuristics)
* verified selection : the gold passages, no further selection
* predicted selection: EG-RAG belief/utility selection over sentence claims of the whole
                       candidate pool (C3, relation-agnostic to avoid leaking gold edges into
                       selection) or over retrieved predicted claims (C4). The token budget
                       equals the oracle evidence length of the same question.
All conditions are serialized as R4 and generated identically.
"""

from __future__ import annotations

from ..data.provenance import gold_units
from ..data.schemas import AnnotationStatus, Edge, EvidenceBundle, Question, RelationType
from ..egrag.pipeline import score_and_select, subset_bundle
from ..extraction.claim_extractor import SentenceClaimExtractor
from ..representations.evidence import EvidenceUnavailable, gold_bundle
from ..representations.protocols import bundle_edge_stratum
from ..representations.serialization import render
from ..retrieval.reranking import retrieve
from ..text import contains_phrase
from .common import ConditionUnavailable, Runner, make_layout


def eligibility(q: Question, accepted: list[str], human_verified: bool = False) -> str | None:
    """Return None if eligible, else the reason. With a human-verified record for the question,
    its reasoning order and DEPENDS_ON edges count as HUMAN_VERIFIED."""
    acc = {AnnotationStatus(s) for s in accepted}
    hv = AnnotationStatus.HUMAN_VERIFIED
    needs = {"reasoning_order": hv if human_verified else q.annotations.get("reasoning_order"),
             "depends_on_edges": hv if human_verified else q.annotations.get("depends_on_edges")}
    bad = {k: (v.value if v else None) for k, v in needs.items() if v not in acc}
    sp = q.annotations.get("supporting_passages")  # dataset-supplied support is acceptable evidence
    if sp not in acc | {AnnotationStatus.DATASET_SUPPLIED, hv}:
        bad["supporting_passages"] = sp.value if sp else None
    if bad:
        return f"verified annotations unavailable: {bad}"
    if not q.gold_facts():
        return "no gold supporting facts"
    if not any(s.depends_on for s in q.reasoning_steps):
        return "no verified dependency structure (parallel/comparison question)"
    return None


def project_edges(verified: list[Edge], pred_claims, anchors_ok: bool = True) -> tuple[list[Edge], int]:
    """Map sentence-level verified edges onto atomic claims derived from those sentences."""
    by_sent: dict[str, list] = {}
    for c in pred_claims:
        by_sent.setdefault(c.claim_id.split(".a")[0], []).append(c)
    out, lost = [], 0
    for e in verified:
        s, t = by_sent.get(e.source, []), by_sent.get(e.target, [])
        if not s or not t:
            lost += 1
            continue
        a = e.meta.get("anchor")
        s1 = next((c for c in s if a and contains_phrase(c.text, a)), s[0])
        t1 = next((c for c in t if a and contains_phrase(c.text, a)), t[0])
        out.append(e.model_copy(update={"source": s1.claim_id, "target": t1.claim_id,
                                        "meta": {**e.meta, "projected_via_provenance": True}}))
    return out, lost


# The C2 predictor finds DEPENDS_ON by title mention. HotpotQA's derived order (R-HPQ) uses the
# same cue, so agreement there is circular; R-ANCHOR (MuSiQue/2Wiki) anchors on sub-answer
# mentions, which often coincide with titles. Recorded on every record; agreement is only
# interpretable against human-verified edges.
DEP_GOLD_CIRCULARITY = {"hotpotqa": "same_rule", "musique": "shared_surface_cue",
                        "2wikimultihopqa": "shared_surface_cue", "toy": "shared_surface_cue"}


def depends_on_prf(pred: list[Edge], verified: list[Edge], claim_passage: dict[str, str], dataset: str = "") -> dict:
    """DEPENDS_ON agreement at passage-pair level (claim anchors differ across extractors)."""
    pp = lambda es: {(claim_passage[e.source], claim_passage[e.target]) for e in es  # noqa: E731
                     if e.relation == RelationType.DEPENDS_ON and e.source in claim_passage and e.target in claim_passage}
    P, V = pp(pred), pp(verified)
    deps = [e for e in verified if e.relation == RelationType.DEPENDS_ON]
    circ = ("none:human_verified" if deps and all(e.status == AnnotationStatus.HUMAN_VERIFIED for e in deps)
            else DEP_GOLD_CIRCULARITY.get(dataset, "unknown"))
    if circ == "same_rule":  # agreement with labels made by the predictor's own heuristic is not reported
        return {"dep_gold_circularity": circ, "dep_precision": None, "dep_recall": None,
                "dep_prf_suppressed": "gold edges derived with the predictor's own title-mention rule",
                "n_pred_dep": len(P), "n_verified_dep": len(V),
                "n_unverifiable_pred_edges": sum(e.relation != RelationType.DEPENDS_ON for e in pred)}
    return {"dep_gold_circularity": circ,"dep_precision": len(P & V) / len(P) if P else None, "dep_recall": len(P & V) / len(V) if V else None,
            "n_pred_dep": len(P), "n_verified_dep": len(V),
            "n_unverifiable_pred_edges": sum(e.relation != RelationType.DEPENDS_ON for e in pred)}


def build_condition(cond: str, q: Question, runner: Runner, oracle: EvidenceBundle, oracle_tokens: int):
    cfg, res = runner.cfg, runner.res
    info: dict = {"component_condition": cond}
    gold_pass = [oracle.passages[p] for p in oracle.passage_order]
    if cond == "oracle":
        return oracle, info
    if cond == "C1":
        claims, xs = res.extractor("llm").extract(gold_pass, gold_units(q))
        edges, lost = project_edges(oracle.edges, claims)
        b = EvidenceBundle(question_uid=q.uid, claims=claims, passages=dict(oracle.passages),
                           passage_order=list(oracle.passage_order), edges=edges,
                           origin={"claims": "predicted(llm)", "relations": "verified(projected)", "selection": "verified"})
        info.update({"extraction": xs, "verified_edges_lost_in_projection": lost})
        return b, info
    if cond == "C2":
        b = oracle.model_copy(deep=True)
        b.edges, rs = res.relation_classifier().classify(b.claims, q.question)
        b.origin = {"claims": "verified", "relations": "predicted", "selection": "verified"}
        cmap_all = {c.claim_id: c.passage_id for c in b.claims}
        info.update({"relations": rs, **depends_on_prf(b.edges, oracle.edges, cmap_all, q.dataset)})
        return b, info
    budget_cfg = cfg.egrag.model_copy(update={"token_budget": max(oracle_tokens, 64)})
    run_cfg = cfg.model_copy(update={"egrag": budget_cfg})
    if cond == "C3":
        pool = list(q.passages)
        ranked = retrieve(q, cfg.retrieval, method="hybrid", top_k=len(pool), dense_encoder=res.dense, corpus=None)
        sc = [r.score for r in ranked]
        lo, hi = min(sc), max(sc)
        prel = {r.passage.passage_id: (r.score - lo) / (hi - lo) if hi > lo else 1.0 for r in ranked}
        claims, _ = SentenceClaimExtractor().extract(pool, gold_units(q))
        egr = res.egrag_resources(q.dataset, "sentence")
        selected, _b, _u, conflicts, trace = score_and_select(q, claims, [], prel, run_cfg, egr,
                                                              use_edges_for_selection=False)
        sel = set(selected)
        verified_edges = [e for e in oracle.edges if e.source in sel and e.target in sel]
        b = subset_bundle(q, claims, verified_edges, conflicts, selected, {p.passage_id: p for p in pool},
                          {"claims": "verified", "relations": "verified(restricted to selected)", "selection": "predicted"})
        info.update({"selection": trace["selection"], "n_verified_edges_kept": len(verified_edges),
                     "n_verified_edges_total": len(oracle.edges)})
        return b, info
    if cond == "C4":
        egr = res.egrag_resources(q.dataset, "llm")
        got = retrieve(q, cfg.retrieval, method="hybrid", rerank=True, dense_encoder=res.dense, reranker=res.reranker,
                       corpus=res.corpus(q.dataset))
        passages = [r.passage for r in got]
        sc = [r.score for r in got]
        lo, hi = min(sc), max(sc)
        prel = {r.passage.passage_id: (r.score - lo) / (hi - lo) if hi > lo else 1.0 for r in got}
        claims, xs = egr.extractor.extract(passages, gold_units(q))
        edges, rs = egr.relation_classifier.classify(claims, q.question)
        selected, _b, _u, conflicts, trace = score_and_select(q, claims, edges, prel, run_cfg, egr)
        b = subset_bundle(q, claims, edges, conflicts, selected, {p.passage_id: p for p in passages},
                          {"claims": "predicted(llm)", "relations": "predicted", "selection": "predicted"})
        cmap_all = {c.claim_id: c.passage_id for c in b.claims}
        info.update({"extraction": xs, "relations": rs, "selection": trace["selection"],
                     **depends_on_prf(b.edges, oracle.edges, {**cmap_all, **{c.claim_id: c.passage_id for c in oracle.claims}}, q.dataset)})
        return b, info
    raise ValueError(cond)


def body(runner: Runner, questions) -> None:
    e3 = runner.cfg.exp3
    for ds, qs in questions.items():
        for q in qs:
            reason = eligibility(q, e3.accepted_statuses, runner.res.verified_record(q) is not None)
            oracle = None
            if reason is None:
                try:
                    oracle = gold_bundle(q, "gold_passages")
                    runner.res.apply_verified(q, oracle)
                except EvidenceUnavailable as e:
                    reason = str(e)
            stratum = bundle_edge_stratum(oracle) if oracle else None
            otoks = runner.res.count_tokens(render(make_layout(e3.representation, oracle)).text) if oracle else 0
            for cond in e3.conditions:
                c = {"component_condition": cond, "representation": e3.representation,
                     "accepted_statuses": sorted(e3.accepted_statuses)}

                def build(cond=cond):
                    if reason:
                        raise ConditionUnavailable(reason)
                    b, info = build_condition(cond, q, runner, oracle, otoks)
                    info["oracle_evidence_tokens"] = otoks
                    info["oracle_edge_stratum"] = stratum
                    info["annotation_statuses"] = {k: v.value for k, v in q.annotations.items()}
                    return b, make_layout(e3.representation, b), info

                runner.run(q, c, build)
