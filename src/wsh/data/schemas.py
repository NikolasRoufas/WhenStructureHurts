"""Shared internal schemas.

Design rules
------------
* Every annotation carries an ``AnnotationStatus`` saying where it came from. A dataset
  with supporting facts does NOT thereby provide gold SUPPORTS/CONTRADICTS/DEPENDS_ON
  edges; those are recorded as UNAVAILABLE unless supplied or deterministically derived.
* Identifiers are globally unique and stable:
    passage_id = "{dataset}/{qid}/p{position:02d}"   (position in the dataset's context list;
                                                       never the title, which can repeat)
    claim_id   = "{passage_id}#s{sentence:02d}"       (sentence-unit claim)
               | "{passage_id}#s{sentence:02d}.a{k}"  (atomic claim k extracted from that sentence)
               | "{claim_id}~{tag}"                   (corrupted / duplicated derivative)
  Display identifiers shown to a generator ("E1", "E2", ...) are assigned per prompt and
  mapped back to these ids; generators never have to copy hashes.
* Spans are character offsets into ``Passage.text``.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class AnnotationStatus(str, Enum):
    DATASET_SUPPLIED = "dataset_supplied"
    DETERMINISTIC_DERIVED = "deterministic_derived"  # documented rule over dataset annotations
    HUMAN_VERIFIED = "human_verified"  # verified by this project's annotators (none yet)
    MODEL_PREDICTED = "model_predicted"
    CORRUPTED = "corrupted"  # produced by a controlled intervention; never gold
    UNAVAILABLE = "unavailable"


VERIFIED_STATUSES_STRICT = frozenset({AnnotationStatus.DATASET_SUPPLIED, AnnotationStatus.HUMAN_VERIFIED})
GOLD_USABLE_STATUSES = frozenset({AnnotationStatus.DATASET_SUPPLIED, AnnotationStatus.HUMAN_VERIFIED,
                                  AnnotationStatus.DETERMINISTIC_DERIVED})


class RelationType(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    DUPLICATE = "DUPLICATE"
    SUPERSEDES = "SUPERSEDES"
    DEPENDS_ON = "DEPENDS_ON"


TaskType = Literal["qa", "verification"]


class SourceRef(BaseModel):
    dataset: str
    split: str
    source_repo: str
    source_revision: str
    source_file: str
    row_index: int


class Span(BaseModel):
    passage_id: str
    start: int
    end: int

    def overlaps(self, other: "Span") -> bool:
        return self.passage_id == other.passage_id and self.start < other.end and other.start < self.end


class Passage(BaseModel):
    passage_id: str
    title: str
    text: str
    sentence_spans: list[tuple[int, int]]
    segmentation: str  # "dataset" or splitter id (e.g. "regex-v1")
    segmentation_status: AnnotationStatus
    position: int  # index in the dataset's candidate list
    lineage_id: str  # passages sharing a lineage are not independent sources
    timestamp: str | None = None

    def sentence(self, i: int) -> str:
        s, e = self.sentence_spans[i]
        return self.text[s:e]

    @property
    def n_sentences(self) -> int:
        return len(self.sentence_spans)


class SupportingFact(BaseModel):
    passage_id: str
    sentence_index: int | None  # None => passage-level annotation only
    status: AnnotationStatus


class ReasoningStep(BaseModel):
    index: int
    passage_ids: list[str]
    sentence_indices: dict[str, list[int]] = Field(default_factory=dict)  # passage_id -> sentences
    sub_question: str | None = None
    sub_answer: str | None = None
    triple: list[str] | None = None  # 2Wiki evidence triple (subject, relation, object)
    depends_on: list[int] = Field(default_factory=list)  # indices of steps this one needs


class Question(BaseModel):
    uid: str  # "{dataset}/{qid}"
    qid: str
    dataset: str
    split: str
    task: TaskType
    question: str
    answers: list[str]  # gold answer + aliases (QA) or verdict label (verification)
    answer_type: Literal["span", "yes_no", "verdict"]
    label_set: list[str] | None = None  # for verification tasks
    question_type: str | None = None  # dataset-supplied type (bridge/comparison/...)
    hop_count: int | None = None
    passages: list[Passage]
    supporting_facts: list[SupportingFact] = Field(default_factory=list)
    reasoning_steps: list[ReasoningStep] = Field(default_factory=list)
    annotations: dict[str, AnnotationStatus]
    annotation_notes: dict[str, str] = Field(default_factory=dict)
    source: SourceRef

    def passage(self, pid: str) -> Passage:
        for p in self.passages:
            if p.passage_id == pid:
                return p
        raise KeyError(pid)

    def gold_facts(self) -> list[SupportingFact]:
        """Supporting facts usable as gold: excludes model-predicted evidence (e.g. FEVER NEI)."""
        return [f for f in self.supporting_facts if f.status in GOLD_USABLE_STATUSES]

    def gold_passage_ids(self) -> list[str]:
        seen: list[str] = []
        for f in self.gold_facts():
            if f.passage_id not in seen:
                seen.append(f.passage_id)
        return seen

    def has_sentence_level_support(self) -> bool:
        g = self.gold_facts()
        return bool(g) and all(f.sentence_index is not None for f in g)


class Claim(BaseModel):
    claim_id: str
    text: str
    spans: list[Span]
    passage_id: str
    title: str
    lineage_id: str
    status: AnnotationStatus  # status of the claim *text* as a faithful unit of its span
    extraction_method: str
    extraction_confidence: float = 1.0
    is_gold_support: bool = False  # overlaps a dataset supporting fact AND not corrupted
    is_distractor: bool = False
    is_corrupted: bool = False
    derived_from: str | None = None  # claim_id of the original for corrupted/duplicated claims
    negated: bool = False
    entities: list[str] = Field(default_factory=list)
    timestamp: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class Edge(BaseModel):
    source: str  # claim_id
    target: str  # claim_id
    relation: RelationType
    confidence: float = 1.0
    status: AnnotationStatus
    method: str
    meta: dict[str, Any] = Field(default_factory=dict)

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.source, self.target, self.relation.value)


class PathStep(BaseModel):
    claim_ids: list[str]
    label: str | None = None


class ConflictSet(BaseModel):
    claim_ids: list[str]
    resolution: dict[str, Literal["preferred", "superseded", "unresolved", "rejected", "excluded"]]


class EvidenceBundle(BaseModel):
    """The evidence handed to a representation serializer for one question/condition."""

    question_uid: str
    claims: list[Claim]
    passages: dict[str, Passage]
    passage_order: list[str]  # order for passage-level (R0) rendering
    edges: list[Edge] = Field(default_factory=list)
    path: list[PathStep] | None = None
    path_status: AnnotationStatus = AnnotationStatus.UNAVAILABLE
    conflicts: list[ConflictSet] = Field(default_factory=list)
    provenance_visible: bool = True
    origin: dict[str, Any] = Field(default_factory=dict)  # how this bundle was constructed
    interventions: list[dict[str, Any]] = Field(default_factory=list)

    def claim(self, cid: str) -> Claim:
        for c in self.claims:
            if c.claim_id == cid:
                return c
        raise KeyError(cid)

    def claim_map(self) -> dict[str, Claim]:
        return {c.claim_id: c for c in self.claims}
