"""Small encoder models: NLI cross-encoder, reranker cross-encoder, dense bi-encoder.

All load from the local cache only, at pinned revisions, and cache their outputs.
"""

from __future__ import annotations

import logging
from typing import Sequence

import numpy as np

from ..cache import KVCache
from ..config import EncoderRef

log = logging.getLogger(__name__)


class NonFiniteOutputError(RuntimeError):
    pass


def realign_parameters(model) -> int:
    """Copy every parameter/buffer into freshly allocated memory.

    safetensors memory-maps checkpoints; when a tensor sits at a misaligned file offset
    (observed: ms-marco-MiniLM-L6-v2, data_ptr % 64 == 2) the Apple-CPU matmul path returns
    NaN for finite inputs. Smoke run 20261010-124651 was affected (all reranker scores NaN, so
    B1 silently equalled B0). Returns the number of tensors that were misaligned.
    """
    import torch

    n = 0
    with torch.no_grad():
        for t in list(model.parameters()) + list(model.buffers()):
            if t.data_ptr() % 64:
                n += 1
            t.data = t.data.clone()
    return n


def assert_finite(values, what: str) -> None:
    import math

    if any(not math.isfinite(float(v)) for v in values):
        raise NonFiniteOutputError(f"{what} produced non-finite outputs")


class NLIModel:
    """Premise/hypothesis NLI with label names read from the model config."""

    def __init__(self, ref: EncoderRef, cache: KVCache | None = None, device: str = "cpu", batch_size: int = 16):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.ref = ref
        self.cache = cache
        self.device = device
        self.batch_size = batch_size
        self.tok = AutoTokenizer.from_pretrained(ref.model_id, revision=ref.revision, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            ref.model_id, revision=ref.revision, local_files_only=True).to(device).eval()
        self.n_realigned = realign_parameters(self.model)
        self.labels = [self.model.config.id2label[i].lower() for i in range(self.model.config.num_labels)]
        self._torch = torch

    @property
    def id(self) -> str:
        return f"{self.ref.model_id}@{self.ref.revision[:8]}"

    def predict(self, pairs: Sequence[tuple[str, str]]) -> list[dict[str, float]]:
        out: list[dict[str, float] | None] = [None] * len(pairs)
        todo = []
        for i, (p, h) in enumerate(pairs):
            hit = self.cache.get("nli", [self.id, p, h]) if self.cache else None
            if hit is not None:
                out[i] = hit
            else:
                todo.append(i)
        for b in range(0, len(todo), self.batch_size):
            idx = todo[b:b + self.batch_size]
            enc = self.tok([pairs[i][0] for i in idx], [pairs[i][1] for i in idx], padding=True,
                           truncation=True, max_length=512, return_tensors="pt").to(self.device)
            with self._torch.inference_mode():
                probs = self._torch.softmax(self.model(**enc).logits, dim=-1).cpu().numpy()
            assert_finite(probs.flatten(), f"NLI {self.id}")
            for i, pr in zip(idx, probs):
                d = {lab: float(v) for lab, v in zip(self.labels, pr)}
                out[i] = d
                if self.cache:
                    self.cache.set("nli", [self.id, pairs[i][0], pairs[i][1]], d)
        return out  # type: ignore[return-value]


class Reranker:
    def __init__(self, ref: EncoderRef, cache: KVCache | None = None, device: str = "cpu"):
        from sentence_transformers import CrossEncoder

        self.ref = ref
        self.cache = cache
        self.model = CrossEncoder(ref.model_id, revision=ref.revision, device=device, local_files_only=True)
        self.n_realigned = realign_parameters(self.model.model)

    def score(self, query: str, texts: Sequence[str]) -> list[float]:
        key = [self.ref.model_id, self.ref.revision, query, list(texts)]
        if self.cache and (hit := self.cache.get("rerank", key)) is not None:
            return hit
        s = [float(x) for x in self.model.predict([(query, t) for t in texts], show_progress_bar=False)]
        assert_finite(s, f"reranker {self.ref.model_id}")
        if self.cache:
            self.cache.set("rerank", key, s)
        return s


class DenseEncoder:
    QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # bge-v1.5 convention

    def __init__(self, ref: EncoderRef, cache: KVCache | None = None, device: str = "cpu"):
        from sentence_transformers import SentenceTransformer

        self.ref = ref
        self.cache = cache
        self.model = SentenceTransformer(ref.model_id, revision=ref.revision, device=device, local_files_only=True)
        self.n_realigned = realign_parameters(self.model)

    def encode(self, texts: Sequence[str], is_query: bool = False) -> np.ndarray:
        texts = [self.QUERY_PREFIX + t if is_query else t for t in texts]
        out: list[list[float] | None] = [None] * len(texts)
        todo = []
        for i, t in enumerate(texts):
            hit = self.cache.get("dense", [self.ref.model_id, self.ref.revision, t]) if self.cache else None
            if hit is not None:
                out[i] = hit
            else:
                todo.append(i)
        if todo:
            vecs = self.model.encode([texts[i] for i in todo], normalize_embeddings=True, show_progress_bar=False)
            assert_finite(vecs.flatten(), f"dense encoder {self.ref.model_id}")
            for i, v in zip(todo, vecs):
                out[i] = v.tolist()
                if self.cache:
                    self.cache.set("dense", [self.ref.model_id, self.ref.revision, texts[i]], out[i])
        return np.asarray(out, dtype=np.float32)
