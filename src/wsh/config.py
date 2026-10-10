"""Typed experiment configuration (pydantic). Unknown keys are rejected."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import json
import os

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models.policy import check_model

Stage = Literal["smoke", "pilot", "gpu_pilot", "full"]
STAGE_LIMITS = {"smoke": {"max_examples": 10, "max_generations": 2000},
                "pilot": {"max_examples": 1000, "max_generations": 200000},
                "gpu_pilot": {"max_examples": 1000, "max_generations": 200000},  # exploratory, frozen pilot set
                "full": {"max_examples": 100000, "max_generations": 10_000_000}}


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_path(p: str | Path) -> Path:
    p = Path(p)
    return p if p.is_absolute() else REPO_ROOT / p


class ModelConfig(Strict):
    model_id: str
    revision: str  # a commit sha, or "pinned" = the revision pinned in configs/models.yaml
    device: Literal["auto", "cpu", "mps", "cuda"] = "cpu"
    dtype: Literal["float32", "bfloat16", "float16"] = "float32"
    max_new_tokens: int = Field(64, ge=1, le=1024)
    max_input_tokens: int = Field(3072, ge=128, le=32768)
    max_time_s: float = Field(60.0, gt=0, le=600)
    batch_size: int = Field(1, ge=1, le=256)  # answer generation; claim extraction stays one prompt at a time
    do_sample: Literal[False] = False  # greedy decoding only; sampling would need seeds per run

    @model_validator(mode="after")
    def _resolve_pinned(self) -> "ModelConfig":
        if self.revision == "pinned":
            from .models.policy import load_model_registry

            entry = load_model_registry()[1].get(self.model_id)
            if entry is None:
                raise ValueError(f"{self.model_id} is not in configs/models.yaml")
            self.revision = entry.revision
        return self


class EncoderRef(Strict):
    model_id: str
    revision: str


class DatasetSelection(Strict):
    name: str
    split: str = "dev"
    n_examples: int = Field(3, ge=1)
    sample_seed: int = 0
    qids: list[str] | None = None
    qids_file: str | None = None  # frozen question list: JSON {"datasets": {name: [qid, ...]}}
    stratify_by: str | None = None

    @model_validator(mode="after")
    def _resolve_qids_file(self) -> "DatasetSelection":
        if self.qids_file:
            if self.qids:
                raise ValueError("give either qids or qids_file, not both")
            frozen = json.loads(repo_path(self.qids_file).read_text())
            if self.name not in frozen["datasets"]:
                raise ValueError(f"{self.qids_file} has no question list for {self.name}")
            self.qids = list(frozen["datasets"][self.name])
        return self


class RetrievalConfig(Strict):
    method: Literal["bm25", "dense", "hybrid"] = "bm25"
    top_k: int = 4
    fusion: Literal["weighted", "rrf"] = "weighted"
    lambda_sparse: float = 0.5
    lambda_dense: float = 0.5
    rerank_pool: int = 10
    corpus_prefilter: int = 50  # shared-corpus datasets (FEVER): BM25 prefilter size
    dense: EncoderRef = EncoderRef(model_id="BAAI/bge-small-en-v1.5", revision="5c38ec7c405ec4b44b94cc5a9bb96e735b38267a")
    reranker: EncoderRef = EncoderRef(model_id="cross-encoder/ms-marco-MiniLM-L6-v2", revision="233902d25c440f23af6f7d6e94d2946bac0bee0a")


class ExtractionConfig(Strict):
    method: Literal["sentence", "rule_atomic", "llm"] = "llm"
    on_empty: Literal["drop", "keep_sentence"] = "drop"
    min_lexical_support: float = 0.6
    max_new_tokens: int = 96
    max_claims_per_sentence: int = 6


class RelationConfig(Strict):
    nli: EncoderRef = EncoderRef(model_id="cross-encoder/nli-deberta-v3-xsmall", revision="a150876415327c80daeff35ca6f68f5ed8cf5c24")
    prune_min_jaccard: float = 0.15
    entail_threshold: float = 0.7
    contradict_threshold: float = 0.9
    contradiction_requires_shared_entity: bool = True  # v2 (smoke inspection: 190 CONTRADICTS among 42 claims)
    duplicate_jaccard: float = 0.8
    max_pairs: int = 400
    year_supersession_threshold: float = 0.7


class EGRAGConfig(Strict):
    # Eq. 5 weights (theta0..theta5) and Eq. 6 weights (eta1..eta3): NOT given in the paper;
    # defaults chosen here and documented as approximations.
    theta: list[float] = [-1.0, 0.5, 1.0, 1.5, 0.5, 0.5]
    eta: list[float] = [1.0, 0.5, 0.5]
    propagate: bool = True
    mu: float = 1.0
    alpha: float = 1.0
    beta: float = 1.0
    gamma: float = 1.0
    eps: float = 1e-4
    max_iter: int = 50
    conflict_margin: float = 0.1
    selector: Literal["greedy_connected", "top_claim"] = "greedy_connected"
    token_budget: int = 450
    omega: dict[str, float] = {"b": 1.0, "u": 1.0, "c": 0.5, "p": 0.2, "r": 0.5, "x": 0.5, "l": 0.3}
    max_claims: int = 12


class GroundingConfig(Strict):
    enabled: bool = True
    nli: EncoderRef = EncoderRef(model_id="cross-encoder/nli-deberta-v3-small", revision="fa2804872c3b4bd748f38c0185cc85775361e735")
    entail_threshold: float = 0.5


class Exp0Config(Strict):
    systems: list[Literal["B0", "B1", "B2", "B3", "B4"]] = ["B0", "B1", "B2", "B3", "B4"]


class Exp1Config(Strict):
    representations: list[str] = ["R0", "R1", "R2", "R3", "R4", "R4P", "R5"]
    evidence_source: Literal["gold", "retrieved"] = "gold"
    evidence_scope: Literal["gold_passages", "gold_sentences"] = "gold_passages"
    # Protocol A = information-controlled (identical fact sets, natural lengths);
    # Protocol B = budget-controlled (whole-fact selection under a token budget). The old
    # 'min_matched' end-truncation mode was retired (see docs/METHODOLOGICAL_AUDIT.md).
    protocols: list[Literal["A", "B"]] = ["A", "B"]
    budgets: list[str] = ["content:0.75"]  # Protocol B: "abs:<tokens>" or "content:<fraction>"
    selection: list[Literal["relevance", "support_first"]] = ["relevance"]
    budget_policies: list[Literal["shared", "per_representation"]] = ["shared"]
    shuffle_seeds: list[int] = [0]


class PerturbationSpec(Strict):
    name: Literal["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
    rates: list[float] = [0.0, 0.1, 0.2, 0.4]
    params: dict[str, Any] = {}


class Exp2Config(Strict):
    base_representations: list[str] = ["R1", "R4"]
    perturbations: list[PerturbationSpec] = []
    seeds: list[int] = [0]
    temporal_spec_path: str | None = None


class Exp3Config(Strict):
    conditions: list[Literal["oracle", "C1", "C2", "C3", "C4"]] = ["oracle", "C1", "C2", "C3", "C4"]
    accepted_statuses: list[str] = ["dataset_supplied", "deterministic_derived", "human_verified"]
    representation: str = "R4"


class Exp4Config(Strict):
    enabled: bool = False  # activated only after Exp1-3 show a reproducible effect
    source_run: str | None = None
    selectors: list[str] = ["fixed:R0", "fixed:R1", "rule", "logistic", "oracle"]
    train_fraction: float = 0.5
    split_seed: int = 0


class ExperimentConfig(Strict):
    stage: Stage
    name: str
    seed: int = 0
    datasets: list[DatasetSelection]
    model: ModelConfig
    retrieval: RetrievalConfig = RetrievalConfig()
    extraction: ExtractionConfig = ExtractionConfig()
    relations: RelationConfig = RelationConfig()
    egrag: EGRAGConfig = EGRAGConfig()
    grounding: GroundingConfig = GroundingConfig()
    exp0: Exp0Config = Exp0Config()
    exp1: Exp1Config = Exp1Config()
    exp2: Exp2Config = Exp2Config()
    exp3: Exp3Config = Exp3Config()
    exp4: Exp4Config = Exp4Config()
    # Server-specific paths; env vars WSH_RESULTS_ROOT / WSH_CACHE_PATH override these at load
    # time and are excluded from the config hash (so a run can resume on another mount point).
    results_root: str = "results"
    cache_path: str = "cache/wsh_cache.sqlite"
    verified_annotations: str | None = None  # output of `wsh annotations import` (human-verified)
    excluded_questions: str | None = "configs/excluded_questions.json"  # smoke / prompt-dev questions
    max_generations: int | None = None  # hard cap per experiment run (in addition to stage cap)
    max_wall_clock_s: float | None = None

    @model_validator(mode="after")
    def _stage_limits(self) -> "ExperimentConfig":
        lim = STAGE_LIMITS[self.stage]
        for d in self.datasets:
            n = len(d.qids) if d.qids else d.n_examples
            if n > lim["max_examples"]:
                raise ValueError(f"stage {self.stage}: {d.name} requests {n} examples (> {lim['max_examples']})")
            if d.split == "test":
                raise ValueError("test splits are not permitted")
        cap = self.max_generations or lim["max_generations"]
        if cap > lim["max_generations"]:
            raise ValueError(f"max_generations {cap} exceeds the {self.stage} cap")
        self.max_generations = cap
        return self

    def enforce_model_policy(self, authorized_flag: bool = False) -> None:
        check_model(self.model.model_id, self.model.revision, self.stage, authorized_flag=authorized_flag)
        for enc in (self.retrieval.dense, self.retrieval.reranker, self.relations.nli, self.grounding.nli):
            check_model(enc.model_id, enc.revision, self.stage, authorized_flag=authorized_flag)


def load_config(path: str | Path, overrides: dict[str, Any] | None = None) -> ExperimentConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    for k, v in (overrides or {}).items():
        cur = raw
        parts = k.split(".")
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = v
    for key, env in (("results_root", "WSH_RESULTS_ROOT"), ("cache_path", "WSH_CACHE_PATH")):
        if os.environ.get(env) and key not in (overrides or {}):
            raw[key] = os.environ[env]
    return ExperimentConfig.model_validate(raw)
