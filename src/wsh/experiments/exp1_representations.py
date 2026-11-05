"""Experiment 1 - does the representation of the same evidence change reasoning?

Primary setting: gold evidence (dataset text only), scope = all sentences of the gold
passages. All representations are built from the same sentence-unit facts. Structure added
by R3/R4/R5 comes from dataset reasoning annotations (or human-verified ones when supplied);
its provenance is recorded per record as ``info.information.added_information`` and the
question's edge stratum (A human-verified / B exact / C fallback / D predicted).

Two protocols, never pooled (``protocol`` is part of every condition, so every summary and
contrast is computed within one protocol):
  A  information-controlled: identical fact sets, natural lengths; the equivalence of the
     fact sets is checked per question (a violation is a pipeline error, not a silent pass).
  B  budget-controlled: whole facts selected by a representation-independent ranking under a
     token budget (policy 'shared' or 'per_representation'); every dropped fact is logged with
     its gold-support / answer-bearing status. See representations/protocols.py.
"""

from __future__ import annotations

from ..data.schemas import EvidenceBundle, Question
from ..representations.evidence import EvidenceUnavailable, gold_bundle
from ..representations.protocols import (InformationEquivalenceViolation, budget_select, bundle_edge_stratum,
                                         check_equivalence, information_profile, parse_budget, rank_facts)
from ..representations.reasoning_paths import PathUnavailable, predicted_path
from ..representations.serialization import render
from .common import Runner, make_layout


def _retrieved_bundle(q: Question, runner: Runner) -> EvidenceBundle:
    from ..extraction.claim_extractor import SentenceClaimExtractor
    from ..data.provenance import gold_units
    from ..representations.evidence import bundle_from_passages
    from ..retrieval.reranking import retrieve
    from ..extraction.relation_classifier import heuristic_depends_on

    cfg, res = runner.cfg, runner.res
    got = retrieve(q, cfg.retrieval, method="bm25", rerank=True, reranker=res.reranker, corpus=res.corpus(q.dataset))
    passages = [r.passage for r in got]
    claims, _ = SentenceClaimExtractor().extract(passages, gold_units(q))
    b = bundle_from_passages(q, passages, claims, {"evidence_source": "retrieved", "retrieval": "bm25+rerank",
                                                    "claims": "sentence units",
                                                    "retrieved_passage_ids": [p.passage_id for p in passages]})
    if cfg.exp1.retrieved_edges == "annotation_restricted":
        # oracle STRUCTURE on real retrieval: annotation-derived edges whose two endpoints were retrieved
        ids = {c.claim_id for c in claims}
        try:
            gold = gold_bundle(q, cfg.exp1.evidence_scope)
            b.edges = [e for e in gold.edges if e.source in ids and e.target in ids]
            n_gold_edges = len(gold.edges)
        except EvidenceUnavailable:
            b.edges, n_gold_edges = [], 0
        b.origin = {**b.origin, "edges": "annotation_derived_restricted_to_retrieved",
                    "n_annotation_edges_total": n_gold_edges, "n_annotation_edges_kept": len(b.edges)}
    else:
        b.edges = heuristic_depends_on(claims, q.question)
    predicted_path(b, q.question)
    return b


def bundles_for(q: Question, runner: Runner) -> dict[str, EvidenceBundle | Exception]:
    e1 = runner.cfg.exp1
    try:
        if e1.evidence_source == "gold":
            base = gold_bundle(q, e1.evidence_scope)
            runner.res.apply_verified(q, base)
        else:
            base = _retrieved_bundle(q, runner)
    except EvidenceUnavailable as e:
        return {r: e for r in e1.representations}
    from ..representations.relation_controls import (CONTROL_REPS, LABEL_REPS, IncompleteContradictionLabels,
                                                     control_bundle)

    out: dict[str, EvidenceBundle | Exception] = {}
    pred = None
    if any(r == "R4P" or r in CONTROL_REPS or r in LABEL_REPS for r in e1.representations):
        pred = base.model_copy(deep=True)
        pred.edges, stats = runner.res.relation_classifier().classify(pred.claims, q.question)
        pred.origin = {**pred.origin, "edges": "model_predicted", "relation_stats": stats}
    for rep in e1.representations:
        if rep == "R3" and not base.path:
            out[rep] = PathUnavailable(f"{q.uid}: reasoning path unavailable ({base.path_status.value})")
        elif rep == "R4P":
            out[rep] = pred
        elif rep in LABEL_REPS:
            try:
                out[rep] = control_bundle(rep, base, pred, _human_labels(e1.contradiction_labels).get(q.uid))
            except IncompleteContradictionLabels as err:
                out[rep] = err  # recorded as a pipeline error for this condition, never imputed
        elif rep in CONTROL_REPS:
            out[rep] = control_bundle(rep, base, pred)
        else:
            out[rep] = base
    return out


_LABELS_CACHE: dict[str, dict] = {}


def _human_labels(path: str | None) -> dict[str, dict[str, str]]:
    """question_uid -> {pair_id: genuine|false|ambiguous} from a frozen human-label file (Experiment B)."""
    if path is None:
        return {}
    if path not in _LABELS_CACHE:
        import json

        from ..config import repo_path

        d = json.loads(repo_path(path).read_text())
        if d.get("label_source") != "human_adjudicated":
            raise ValueError(f"{path}: label_source must be 'human_adjudicated'")
        _LABELS_CACHE[path] = d["questions"]
    return _LABELS_CACHE[path]


def _variants(bundles: dict, seeds: list[int]) -> tuple[dict, dict]:
    """name -> (rep, seed, bundle) for buildable variants; name -> exception otherwise."""
    ok, bad = {}, {}
    for rep, b in bundles.items():
        for s in (seeds if rep == "R2" else [0]):
            name = f"R2#s{s}" if rep == "R2" else rep
            (bad if isinstance(b, Exception) else ok)[name] = (rep, s, b)
    return ok, bad


def _cond(rep: str, s: int, e1, **extra) -> dict:
    return {**extra, "representation": rep, "shuffle_seed": s if rep == "R2" else None,
            "evidence_source": e1.evidence_source, "scope": e1.evidence_scope}


def body(runner: Runner, questions) -> None:
    e1 = runner.cfg.exp1
    count = runner.res.count_tokens
    for ds, qs in questions.items():
        for q in qs:
            bundles = bundles_for(q, runner)
            ok, bad = _variants(bundles, e1.shuffle_seeds)
            from ..representations.relation_controls import PREDICTED_REPS
            first = next((v[2] for v in ok.values() if v[0] not in PREDICTED_REPS), None)
            stratum = bundle_edge_stratum(first) if first is not None else None
            settings = []
            if "A" in e1.protocols:
                settings.append({"protocol": "A"})
            if "B" in e1.protocols:
                settings += [{"protocol": "B", "budget": bud, "selection": sel, "policy": pol}
                             for bud in e1.budgets for sel in e1.selection for pol in e1.budget_policies]
            for st in settings:
                built = _protocol_a(q, ok, count) if st["protocol"] == "A" else _protocol_b(q, ok, first, st, count)
                for name, (rep, s, b) in ok.items():
                    cond = _cond(rep, s, e1, **st)
                    item = built[name] if not isinstance(built, Exception) else built

                    def build(item=item, b=b, rep=rep):
                        if isinstance(item, Exception):
                            raise item
                        sub, ser, extra = item
                        return sub, ser, {"edge_status": sorted({e.status.value for e in sub.edges}),
                                          "path_status": sub.path_status.value, "question_edge_stratum": stratum,
                                          **extra}

                    runner.run(q, cond, build)
                for name, (rep, s, err) in bad.items():
                    def fail(err=err):
                        raise err

                    runner.run(q, _cond(rep, s, e1, **st), fail)


def _protocol_a(q: Question, ok: dict, count):
    out, profiles = {}, {}
    for name, (rep, s, b) in ok.items():
        lay = make_layout(rep, b, s)
        ser = render(lay)
        ser.evidence_tokens = count(ser.text)
        profiles[name] = information_profile(rep, lay, ser, b, q, count)
        out[name] = (b, ser, {"information": profiles[name]})
    try:
        check_equivalence(profiles)
    except InformationEquivalenceViolation as e:
        return e
    return out


def _protocol_b(q: Question, ok: dict, base: EvidenceBundle | None, st: dict, count):
    if base is None:
        return {}
    content_full = count("\n".join(c.text for c in base.claims))
    budget = parse_budget(st["budget"], content_full)
    ranking = rank_facts(base, q, st["selection"])
    variants = {name: (b, (lambda sub, rep=rep, s=s: make_layout(rep, sub, s))) for name, (rep, s, b) in ok.items()}
    sel = budget_select(variants, q, budget, ranking, st["policy"], count)
    out = {}
    for name, (rep, s, b) in ok.items():
        sub, lay, ser, acct = sel[name]
        acct = {**acct, "content_tokens_full": content_full, "selection": st["selection"],
                "selection_uses_gold_labels": st["selection"] == "support_first"}
        out[name] = (sub, ser, {"budget_accounting": acct,
                                "information": information_profile(rep, lay, ser, sub, q, count)})
    return out
