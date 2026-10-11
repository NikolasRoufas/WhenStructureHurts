"""Generator interface. Experiments depend only on this protocol."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal, Protocol, runtime_checkable

FinishReason = Literal["eos", "length", "time", "error", "skipped_overflow"]


@dataclass
class GenerationRequest:
    system: str
    user: str
    max_new_tokens: int
    purpose: str = "answer"  # answer | claim_extraction
    prefill: str = ""  # text the assistant turn starts with (identical across conditions); part of the output


@dataclass
class GenerationResult:
    text: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    finish_reason: FinishReason
    model_id: str
    revision: str
    decoding: dict = field(default_factory=dict)
    cached: bool = False
    error: str | None = None
    batch_size: int = 1  # rows in the padded batch that produced this output (latency_s is the batch's wall time)

    def to_dict(self) -> dict:
        return asdict(self)


@runtime_checkable
class Generator(Protocol):
    model_id: str
    revision: str
    max_input_tokens: int

    def count_tokens(self, text: str) -> int: ...

    def prompt_tokens(self, req: GenerationRequest) -> int: ...

    def generate(self, req: GenerationRequest) -> GenerationResult: ...

    # optional: generate_batch(reqs) -> list[GenerationResult] in request order (used when
    # model.batch_size > 1; the runner falls back to generate() otherwise)


class TokenCounter(Protocol):
    def count_tokens(self, text: str) -> int: ...
