"""Shared experiment machinery: lazily-loaded resources, representation dispatch, and the
generate -> evaluate -> record loop with hard budgets and safe resumption."""

from __future__ import annotations

import logging
import time
import traceback
from typing import Any, Callable

from ..artifacts import RunContext
from ..cache import KVCache
from ..config import ExperimentConfig
from ..data.loaders import DEFAULT_DATA_ROOT, load_fever_corpus, load_registry, sample_questions
from ..data.schemas import EvidenceBundle, Question
from ..data.validation import validate_bundle, validate_question
from ..evaluation.evaluator import evaluate
from ..hashing import stable_hash
from ..models.prompts import assert_prompt_composition, build_request, prompt_version
from ..representations import atomic_claims, evidence_graphs, raw_passages, reasoning_paths
from ..representations.serialization import Layout, SerializedEvidence, render

log = logging.getLogger(__name__)


class BudgetExceeded(RuntimeError):
    pass


class ConditionUnavailable(RuntimeError):
    """The condition cannot be built for this question without fabricating annotations.
    Recorded as 'unavailable' (excluded from metric denominators, always counted in reports)."""


def _unavailable_types():
    from ..representations.evidence import EvidenceUnavailable
    from ..representations.reasoning_paths import PathUnavailable

    return (ConditionUnavailable, EvidenceUnavailable, PathUnavailable)


class Resources:
    """Lazily constructs models so that experiments load only what they need."""

    def __init__(self, cfg: ExperimentConfig, authorized_flag: bool = False):
        from ..data.loaders import REPO_ROOT

        self.cfg = cfg
        self.authorized_flag = authorized_flag
        cache_path = cfg.cache_path if cfg.cache_path.startswith("/") else str(REPO_ROOT / cfg.cache_path)
        self.cache = KVCache(cache_path)
        from ..models.local_generator import resolve_device

        self.device = resolve_device(cfg.model.device)  # encoders follow the generator's device
        self._gen = self._dense = self._rerank = self._nli_rel = self._nli_ground = None
        self._corpora: dict[str, Any] = {}
        self.loaded: dict[str, str] = {}
        from ..annotations import load_verified
        from ..config import repo_path

        self.verified = load_verified(repo_path(cfg.verified_annotations) if cfg.verified_annotations else None)

    def verified_record(self, q: Question) -> dict | None:
        return self.verified.get(q.uid)

    def apply_verified(self, q: Question, b: EvidenceBundle) -> None:
        from ..annotations import apply_verified

        apply_verified(q, b, self.verified.get(q.uid))

    @property
    def generator(self):
        if self._gen is None:
            from ..models.local_generator import LocalHFGenerator

            self._gen = LocalHFGenerator(self.cfg.model, self.cfg.stage, self.cache, self.authorized_flag)
            self.loaded["generator"] = f"{self._gen.model_id}@{self._gen.revision} ({self._gen.n_params} params, {self._gen.device})"
        return self._gen

    def count_tokens(self, text: str) -> int:
        return self.generator.count_tokens(text)

    @property
    def dense(self):
        if self._dense is None:
            from ..models.encoders import DenseEncoder

            self._dense = DenseEncoder(self.cfg.retrieval.dense, self.cache, device=self.device)
            self.loaded["dense"] = f"{self.cfg.retrieval.dense.model_id}@{self.cfg.retrieval.dense.revision}"
        return self._dense

    @property
    def reranker(self):
        if self._rerank is None:
            from ..models.encoders import Reranker

            self._rerank = Reranker(self.cfg.retrieval.reranker, self.cache, device=self.device)
            self.loaded["reranker"] = f"{self.cfg.retrieval.reranker.model_id}@{self.cfg.retrieval.reranker.revision}"
        return self._rerank

    @property
    def nli_relations(self):
        if self._nli_rel is None:
            from ..models.encoders import NLIModel

            self._nli_rel = NLIModel(self.cfg.relations.nli, self.cache, device=self.device)
            self.loaded["nli_relations"] = self._nli_rel.id
        return self._nli_rel

    @property
    def nli_grounding(self):
        if not self.cfg.grounding.enabled:
            return None
        if self._nli_ground is None:
            from ..models.encoders import NLIModel

            self._nli_ground = NLIModel(self.cfg.grounding.nli, self.cache, device=self.device)
            self.loaded["nli_grounding"] = self._nli_ground.id
        return self._nli_ground

    def extractor(self, method: str | None = None):
        from ..extraction.claim_extractor import build_extractor

        m = method or self.cfg.extraction.method
        return build_extractor(m, self.generator if m == "llm" else None, self.cfg.extraction)

    def relation_classifier(self):
        from ..extraction.relation_classifier import RelationClassifier

        return RelationClassifier(self.nli_relations, self.cfg.relations)

    def corpus(self, dataset: str):
        """Shared retrieval corpus (FEVER only); None for distractor-setting datasets."""
        if dataset != "fever":
            return None
        if dataset not in self._corpora:
            from ..retrieval.bm25 import CorpusIndex

            self._corpora[dataset] = CorpusIndex(load_fever_corpus(load_registry()["fever"], "dev", DEFAULT_DATA_ROOT))
        return self._corpora[dataset]

    def egrag_resources(self, dataset: str, extraction_method: str | None = None):
        from ..egrag.pipeline import EGRAGResources

        return EGRAGResources(extractor=self.extractor(extraction_method), relation_classifier=self.relation_classifier(),
                              count_tokens=self.count_tokens, dense_encoder=self.dense, reranker=self.reranker,
                              corpus=self.corpus(dataset))


def load_questions(cfg: ExperimentConfig) -> dict[str, list[Question]]:
    out: dict[str, list[Question]] = {}
    for d in cfg.datasets:
        qs = sample_questions(d.name, d.split, d.n_examples, d.sample_seed, d.qids, stratify_by=d.stratify_by)
        for q in qs:
            validate_question(q)
        out[d.name] = qs
    from ..data.question_sets import assert_no_excluded, load_excluded

    assert_no_excluded(out, load_excluded(cfg.excluded_questions), cfg.stage)
    return out


class UnfrozenQuestionSetError(RuntimeError):
    pass


def require_frozen_questions(cfg: ExperimentConfig) -> None:
    """Pilot/full runs must use a question list fixed before execution (qids / qids_file)."""
    if cfg.stage != "smoke":
        loose = [d.name for d in cfg.datasets if not d.qids]
        if loose:
            raise UnfrozenQuestionSetError(f"stage {cfg.stage}: datasets {loose} are not frozen; "
                                           "run `wsh questions freeze` and set datasets[*].qids_file")


def make_layout(rep: str, b: EvidenceBundle, seed: int = 0) -> Layout:
    if rep == "R0":
        return raw_passages.layout(b)
    if rep == "R1":
        return atomic_claims.layout(b)
    if rep == "R2":
        return atomic_claims.shuffled_layout(b, seed)
    if rep == "R3":
        return reasoning_paths.layout(b)
    if rep in ("R4", "R4P"):
        return evidence_graphs.layout(b, rep=rep, with_edges=True)
    if rep == "R5":
        return evidence_graphs.layout(b, rep="R5", with_edges=False)
    from ..representations.relation_controls import CONTROL_REPS, with_edges
    if rep in CONTROL_REPS:
        return evidence_graphs.layout(b, rep=rep, with_edges=with_edges(rep))
    raise ValueError(f"unknown representation {rep}")


class Runner:
    def __init__(self, cfg: ExperimentConfig, ctx: RunContext, res: Resources):
        self.cfg, self.ctx, self.res = cfg, ctx, res
        self.n_generated = 0
        self.t0 = time.time()
        self.n_written = 0
        self.n_skipped_done = 0
        # batched generation: prepared records wait here until a full batch can be generated.
        # They are written only after generation, so an interruption loses at most the queue,
        # which a resumed run rebuilds (records are keyed; nothing is duplicated or dropped).
        self.batch_size = cfg.model.batch_size
        self.queue_limit = cfg.model.batch_size * 4  # a few batches, so chunks are length-sorted
        self._pending: list[dict] = []

    def _model_calls(self) -> int:
        gen = getattr(self.res, "_gen", None)
        return max(self.n_generated, getattr(gen, "n_uncached", 0) or 0)

    def _check_budget(self) -> None:
        if self.cfg.max_generations is not None and self._model_calls() + len(self._pending) >= self.cfg.max_generations:
            raise BudgetExceeded(f"generation cap {self.cfg.max_generations} reached")
        if self.cfg.max_wall_clock_s is not None and time.time() - self.t0 > self.cfg.max_wall_clock_s:
            raise BudgetExceeded(f"wall-clock cap {self.cfg.max_wall_clock_s}s reached")

    def key(self, q: Question, condition: dict) -> str:
        return stable_hash({"exp": self.ctx.experiment, "q": q.uid, "c": condition, "seed": self.cfg.seed})

    def run(self, q: Question, condition: dict, build: Callable[[], tuple[EvidenceBundle, Any, dict]],
            extra: dict | None = None) -> dict | None:
        """``build`` returns (bundle, layout-or-serialized, info). Exceptions inside ``build``
        are recorded as pipeline_error records (they stay in the denominator)."""
        key = self.key(q, condition)
        if self.ctx.is_done(key) or any(p["key"] == key for p in self._pending):
            self.n_skipped_done += 1
            return None
        self._check_budget()
        base = {
            "record_key": key, "run_id": self.ctx.dir.name, "experiment": self.ctx.experiment, "condition": condition,
            "dataset": q.dataset, "split": q.split, "question_uid": q.uid, "qid": q.qid,
            "dataset_source": q.source.model_dump(), "question": q.question, "gold_answers": q.answers,
            "task": q.task, "question_type": q.question_type, "hop_count": q.hop_count,
            "model_id": self.cfg.model.model_id, "model_revision": self.cfg.model.revision, "seed": self.cfg.seed,
            "prompt_version": prompt_version(), "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            **(extra or {}),
        }
        try:
            bundle, lay, info = build()
            validate_bundle(bundle)
            ser = lay if isinstance(lay, SerializedEvidence) else render(lay)
        except _unavailable_types() as e:
            rec = {**base, "unavailable": f"{type(e).__name__}: {e}"}
            self.ctx.write(rec)
            self.n_written += 1
            return rec
        except Exception as e:
            rec = {**base, "pipeline_error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc(limit=5),
                   **evaluate(q, None, None, None, None, pipeline_error=True)}
            self.ctx.write(rec)
            self.n_written += 1
            return rec
        req = build_request(q, ser.text, self.cfg.model.max_new_tokens)
        assert_prompt_composition(q, req, ser.text)
        gen = self.res.generator
        overhead = gen.prompt_tokens(build_request(q, "", self.cfg.model.max_new_tokens))
        item = {"key": key, "q": q, "base": base, "info": info, "bundle": bundle, "ser": ser, "req": req,
                "overhead": overhead}
        if self.batch_size > 1 and hasattr(gen, "generate_batch"):
            self._pending.append(item)
            if len(self._pending) >= self.queue_limit:
                self.flush()
            return None
        return self._finish(item, gen.generate(req))

    def flush(self) -> None:
        """Generate every queued record (in batches) and write them in queue order."""
        if not self._pending:
            return
        items, self._pending = self._pending, []
        results = self.res.generator.generate_batch([it["req"] for it in items])
        if len(results) != len(items):
            raise RuntimeError(f"generate_batch returned {len(results)} results for {len(items)} requests")
        for it, res in zip(items, results):
            self._finish(it, res)

    def _finish(self, item: dict, res) -> dict:
        q, base, info, bundle, ser, req, overhead = (item[k] for k in ("q", "base", "info", "bundle", "ser", "req", "overhead"))
        gen = self.res.generator
        self.n_generated += int(not res.cached)
        ev = evaluate(q, res.text, res.finish_reason, ser, bundle, self.res.nli_grounding, self.cfg.grounding.entail_threshold)
        rec = {
            **base, "info": info,
            "evidence": {"representation": ser.rep, "text": ser.text, "id_map": ser.id_map, "n_units": ser.n_units,
                         "n_relations": ser.n_relations, "dropped": ser.dropped, "budget": ser.budget,
                         "evidence_tokens": ser.evidence_tokens if ser.evidence_tokens is not None else gen.count_tokens(ser.text),
                         "notes": ser.notes, "bundle_origin": bundle.origin, "interventions": bundle.interventions,
                         "claims": [{"claim_id": c.claim_id, "status": c.status.value, "gold": c.is_gold_support,
                                     "corrupted": c.is_corrupted, "distractor": c.is_distractor,
                                     "extraction_confidence": c.extraction_confidence,
                                     "unsupported": bool(c.meta.get("unsupported"))} for c in bundle.claims],
                         "edges": [{"source": e.source, "target": e.target, "relation": e.relation.value,
                                    "status": e.status.value, "confidence": e.confidence} for e in bundle.edges]},
            "prompt": {"system": req.system, "user": req.user, "overhead_tokens": overhead},
            "generation": {"text": res.text, "finish_reason": res.finish_reason, "input_tokens": res.input_tokens,
                           "output_tokens": res.output_tokens, "latency_s": res.latency_s, "cached": res.cached,
                           "error": res.error, "decoding": res.decoding, "batch_size": getattr(res, "batch_size", 1),
                           "latency_per_item_s": res.latency_s / max(1, getattr(res, "batch_size", 1))},
            **ev,
        }
        self.ctx.write(rec)
        self.n_written += 1
        return rec


def run_experiment(cfg: ExperimentConfig, experiment: str, body: Callable[[Runner, dict[str, list[Question]]], None],
                   resume_dir: str | None = None, authorized_flag: bool = False) -> RunContext:
    cfg.enforce_model_policy(authorized_flag)
    require_frozen_questions(cfg)
    questions = load_questions(cfg)  # before creating a run directory: exclusion guards may refuse
    ctx = RunContext(cfg, experiment, resume_dir)
    res = Resources(cfg, authorized_flag)
    from ..data.loaders import DEFAULT_DATA_ROOT as DR
    import json

    data_manifest = json.loads((DR / "MANIFEST.json").read_text()) if (DR / "MANIFEST.json").exists() else {}
    ctx.update_manifest(datasets={
        d: {"split": qs[0].split if qs else None, "qids": [q.qid for q in qs],
            "source": data_manifest.get(f"{d}/{qs[0].split}") if qs else None} for d, qs in questions.items()})
    runner = Runner(cfg, ctx, res)
    status = "completed"
    try:
        body(runner, questions)
        runner.flush()
    except BudgetExceeded as e:
        runner.flush()  # queued records were admitted under the cap: generate and write them
        status = f"stopped: {e}"
        log.warning(status)
    except KeyboardInterrupt:
        status = "interrupted (resume with --resume)"
        raise
    finally:
        ctx.update_manifest(status=status, finished_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                            wall_clock_s=round(time.time() - runner.t0, 2), n_generated_uncached=runner.n_generated,
                            n_model_calls_uncached_incl_extraction=runner._model_calls(),
                            n_records_written=runner.n_written, n_records_skipped_already_done=runner.n_skipped_done,
                            loaded_models=res.loaded, cache_hits=res.cache.hits, cache_misses=res.cache.misses,
                            determinism=getattr(res._gen, "determinism", None), device=res.device,
                            generation_batch_size=cfg.model.batch_size, n_records_unflushed=len(runner._pending),
                            generator_stats=res._gen.memory_stats() if hasattr(res._gen, "memory_stats") else None)
    from ..evaluation.reporting import write_reports

    write_reports(ctx)
    return ctx
