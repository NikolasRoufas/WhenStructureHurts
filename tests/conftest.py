"""Test fixtures. The FakeGenerator is a SOFTWARE-TEST MOCK ONLY; it is never used by any
experiment command and smoke results are never produced with it."""

from __future__ import annotations

import pytest

from wsh.data.loaders import DEFAULT_DATA_ROOT, load_registry
from wsh.data.provenance import passage_id
from wsh.data.schemas import AnnotationStatus as S, Passage, Question, ReasoningStep, SourceRef, SupportingFact
from wsh.models.interfaces import GenerationResult


class FakeGenerator:
    model_id = "fake/mock"
    revision = "0"
    max_input_tokens = 10_000

    def __init__(self, replies=None, default="Answer: Paris\nEvidence: E1"):
        self.replies = list(replies or [])
        self.default = default
        self.calls = []

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def prompt_tokens(self, req) -> int:
        return self.count_tokens(req.system + " " + req.user)

    def generate(self, req) -> GenerationResult:
        self.calls.append(req)
        text = self.replies.pop(0) if self.replies else self.default
        if req.prefill and not text.startswith(req.prefill):
            text = req.prefill + text
        return GenerationResult(text=text, input_tokens=self.prompt_tokens(req), output_tokens=len(text.split()),
                                latency_s=0.001, finish_reason="eos", model_id=self.model_id, revision=self.revision)


def _p(qid, pos, title, sents):
    text = " ".join(sents)
    spans, off = [], 0
    for s in sents:
        spans.append((off, off + len(s)))
        off += len(s) + 1
    return Passage(passage_id=passage_id("toy", qid, pos), title=title, text=text, sentence_spans=spans,
                   segmentation="dataset", segmentation_status=S.DATASET_SUPPLIED, position=pos,
                   lineage_id=f"toy:title:{title.lower()}")


@pytest.fixture
def toy_question() -> Question:
    """Synthetic 2-hop fixture (for code correctness only; never reported as a result)."""
    qid = "q1"
    ps = [
        _p(qid, 0, "DeepMind", ["DeepMind is an AI lab.", "DeepMind was acquired by Google in 2014.", "It is not in Paris."]),
        _p(qid, 1, "Google", ["Google was founded by Larry Page and Sergey Brin.", "Google is based in California."]),
        _p(qid, 2, "Paris", ["Paris is the capital of France.", "About 2 million people live in Paris."]),
        _p(qid, 3, "Google", ["Google is also a verb."]),  # duplicate title on purpose
    ]
    facts = [SupportingFact(passage_id=ps[0].passage_id, sentence_index=1, status=S.DATASET_SUPPLIED),
             SupportingFact(passage_id=ps[1].passage_id, sentence_index=0, status=S.DATASET_SUPPLIED)]
    steps = [ReasoningStep(index=0, passage_ids=[ps[0].passage_id], sentence_indices={ps[0].passage_id: [1]}, sub_answer="Google"),
             ReasoningStep(index=1, passage_ids=[ps[1].passage_id], sentence_indices={ps[1].passage_id: [0]}, depends_on=[0])]
    return Question(
        uid=f"toy/{qid}", qid=qid, dataset="toy", split="dev", task="qa",
        question="Who founded the company that acquired DeepMind?", answers=["Larry Page and Sergey Brin", "Larry Page"],
        answer_type="span", question_type="bridge", hop_count=2, passages=ps, supporting_facts=facts, reasoning_steps=steps,
        annotations={"answer": S.DATASET_SUPPLIED, "supporting_passages": S.DATASET_SUPPLIED,
                     "supporting_sentences": S.DATASET_SUPPLIED, "sentence_segmentation": S.DATASET_SUPPLIED,
                     "reasoning_order": S.DETERMINISTIC_DERIVED, "depends_on_edges": S.DETERMINISTIC_DERIVED,
                     "supports_edges": S.UNAVAILABLE, "contradicts_edges": S.UNAVAILABLE, "duplicate_edges": S.UNAVAILABLE,
                     "supersedes_edges": S.UNAVAILABLE, "temporal_info": S.UNAVAILABLE},
        source=SourceRef(dataset="toy", split="dev", source_repo="synthetic", source_revision="0", source_file="-", row_index=0),
    )


def data_available(name: str, split: str = "dev") -> bool:
    try:
        return load_registry()[name].file_for(split, DEFAULT_DATA_ROOT).exists()
    except Exception:
        return False


@pytest.fixture
def fake_gen():
    return FakeGenerator()
