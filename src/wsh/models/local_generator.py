"""Local Hugging Face causal-LM generator (greedy, bounded, optionally batched).

* Loads only from the local cache (``local_files_only=True``); downloads happen exclusively
  through ``wsh models fetch`` after policy and resource checks.
* Generation is bounded by ``max_new_tokens`` and a wall-clock ``max_time``; prompts longer
  than ``max_input_tokens`` are not generated (finish_reason='skipped_overflow').
* Results are cached by (model, revision, rendered prompt, decoding params incl. device,
  dtype and batch size). Cache hits are flagged and keep the latency measured on the
  original call.

Batching (``model.batch_size`` > 1, ``generate_batch``):
* left padding with an explicit attention mask (decoder-only models continue from the right);
* uncached requests are de-duplicated (an identical prompt is generated once; later copies
  are returned as cache hits, exactly as a sequential run would return them), sorted by
  length to limit padding, grouped by ``max_new_tokens`` and chunked by ``batch_size``;
* each row is cut at its first end-of-sequence token, so rows that finished early never
  carry padding into their text;
* out-of-memory: the chunk is split in half and retried, down to single prompts; a single
  prompt that still does not fit is recorded as a generation error (never dropped);
* results are returned in request order (association is index-based, never by content).
Greedy decoding of a padded batch can differ numerically from unpadded decoding; the
configured batch size is therefore part of the decoding settings and of the cache key, and
``tests/test_batching.py`` measures batched-vs-unbatched agreement.
"""

from __future__ import annotations

import logging
import os
import time

from ..cache import KVCache
from ..config import ModelConfig
from .interfaces import GenerationRequest, GenerationResult
from .policy import check_model, verify_loaded_param_count

log = logging.getLogger(__name__)


def resolve_device(device: str) -> str:
    import torch

    if device != "auto":
        return device
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def generation_cache_key(model_id: str, revision: str, prompt: str, max_new_tokens: int, decoding: dict) -> dict:
    """Everything that can change an output: model + revision, the fully rendered prompt (which
    contains the representation's evidence block and the prompt template), the token limit and
    all decoding settings INCLUDING device, dtype and batch size (CPU and GPU numerics differ,
    and padded batches can differ from single prompts, so such outputs are never shared)."""
    return {"m": model_id, "r": revision, "p": prompt, "n": max_new_tokens, "d": dict(sorted(decoding.items()))}


def set_determinism(device: str) -> dict:
    """Best-effort determinism; what was applied is recorded in the run manifest."""
    import torch

    torch.manual_seed(0)
    applied = {"torch_manual_seed": 0}
    if device.startswith("cuda"):
        torch.cuda.manual_seed_all(0)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.use_deterministic_algorithms(True, warn_only=True)
        applied.update({"cudnn_deterministic": True, "deterministic_algorithms": "warn_only",
                        "CUBLAS_WORKSPACE_CONFIG": os.environ.get("CUBLAS_WORKSPACE_CONFIG")})
    return applied


def is_oom(e: BaseException) -> bool:
    import torch

    if isinstance(e, getattr(torch, "OutOfMemoryError", ())) or isinstance(e, getattr(torch.cuda, "OutOfMemoryError", ())):
        return True
    return isinstance(e, RuntimeError) and "out of memory" in str(e).lower()


class LocalHFGenerator:
    def __init__(self, cfg: ModelConfig, stage: str, cache: KVCache | None = None, authorized_flag: bool = False):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        entry = check_model(cfg.model_id, cfg.revision, stage, authorized_flag=authorized_flag)
        device = resolve_device(cfg.device)
        determinism = set_determinism(device)
        tokenizer = AutoTokenizer.from_pretrained(cfg.model_id, revision=cfg.revision, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(
            cfg.model_id, revision=cfg.revision, local_files_only=True, dtype=getattr(torch, cfg.dtype)
        ).to(device)
        from .encoders import realign_parameters

        n_realigned = realign_parameters(model)
        n_params = verify_loaded_param_count(model, entry, stage)
        self._setup(cfg, model, tokenizer, device, cache, entry.raw.get("chat_template_kwargs") or {})
        self.entry, self.determinism, self.n_realigned, self.n_params = entry, determinism, n_realigned, n_params
        log.info("loaded %s@%s on %s (%d params)", cfg.model_id, cfg.revision[:8], device, n_params)

    @classmethod
    def from_components(cls, cfg: ModelConfig, model, tokenizer, device: str = "cpu", cache: KVCache | None = None,
                        chat_template_kwargs: dict | None = None) -> "LocalHFGenerator":
        """Wrap an already-built model (tests only: tiny randomly initialised models)."""
        self = cls.__new__(cls)
        self._setup(cfg, model, tokenizer, device, cache, chat_template_kwargs or {})
        self.determinism, self.n_params = set_determinism(device), sum(p.numel() for p in model.parameters())
        return self

    def _setup(self, cfg: ModelConfig, model, tokenizer, device: str, cache, chat_template_kwargs: dict) -> None:
        import torch

        self.cfg = cfg
        self.model_id, self.revision = cfg.model_id, cfg.revision
        self.max_input_tokens = cfg.max_input_tokens
        self.device, self.cache = device, cache
        self.model, self.tokenizer = model.eval(), tokenizer
        self.tokenizer.padding_side = "left"
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.chat_template_kwargs = dict(chat_template_kwargs)
        self.batch_size = cfg.batch_size
        eos = getattr(model.generation_config, "eos_token_id", None)
        self.eos_ids = set(eos if isinstance(eos, list) else [eos]) | {tokenizer.eos_token_id}
        self.eos_ids.discard(None)
        self.decoding = {"do_sample": False, "num_beams": 1, "dtype": cfg.dtype, "device": device,
                         "max_time_s": cfg.max_time_s, "batch_size": cfg.batch_size,
                         **({"chat_template_kwargs": self.chat_template_kwargs} if self.chat_template_kwargs else {})}
        self.n_uncached = 0  # every real model call (answers AND claim extraction); used by budget caps
        self.stats = {"n_batches": 0, "n_batched_prompts": 0, "n_oom_splits": 0, "n_oom_failures": 0,
                      "peak_gpu_mem_bytes": None, "n_dedup_in_batch": 0}
        if device.startswith("cuda"):
            torch.cuda.reset_peak_memory_stats()

    # -- prompt rendering ---------------------------------------------------------------

    def render(self, req: GenerationRequest) -> str:
        msgs = [{"role": "system", "content": req.system}, {"role": "user", "content": req.user}]
        return self.tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                                  **self.chat_template_kwargs) + req.prefill

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer(text, add_special_tokens=False)["input_ids"])

    def prompt_tokens(self, req: GenerationRequest) -> int:
        return self.count_tokens(self.render(req))

    def memory_stats(self) -> dict:
        import torch

        if self.device.startswith("cuda"):
            self.stats["peak_gpu_mem_bytes"] = int(torch.cuda.max_memory_allocated())
            self.stats["gpu_mem_reserved_bytes"] = int(torch.cuda.memory_reserved())
        elif self.device == "mps":
            self.stats["mps_driver_allocated_bytes"] = int(torch.mps.driver_allocated_memory())
        return dict(self.stats)

    # -- generation -----------------------------------------------------------------------

    def _key(self, prompt: str, req: GenerationRequest) -> dict:
        return generation_cache_key(self.model_id, self.revision, prompt, req.max_new_tokens, self.decoding)

    def generate(self, req: GenerationRequest) -> GenerationResult:
        return self.generate_batch([req])[0]

    def generate_batch(self, reqs: list[GenerationRequest]) -> list[GenerationResult]:
        from ..hashing import stable_hash

        prompts = [self.render(r) for r in reqs]
        keys = [self._key(p, r) for p, r in zip(prompts, reqs)]
        out: list[GenerationResult | None] = [None] * len(reqs)
        first: dict[str, int] = {}  # key hash -> index of the request that will be generated
        dups: list[tuple[int, int]] = []
        for i, k in enumerate(keys):
            if self.cache is not None and (hit := self.cache.get("generation", k)) is not None:
                out[i] = GenerationResult(**{**hit, "cached": True})
                continue
            h = stable_hash(k)
            if h in first:
                dups.append((i, first[h]))
            else:
                first[h] = i
        todo = list(first.values())
        # tokenise once; overflowing prompts are never generated
        lens = {i: len(self.tokenizer(prompts[i], add_special_tokens=False)["input_ids"]) for i in todo}
        for i in todo:
            if lens[i] > self.max_input_tokens:
                out[i] = GenerationResult(text="", input_tokens=lens[i], output_tokens=0, latency_s=0.0,
                                          finish_reason="skipped_overflow", model_id=self.model_id,
                                          revision=self.revision, decoding=self.decoding,
                                          error=f"prompt has {lens[i]} tokens > max_input_tokens={self.max_input_tokens}")
        todo = [i for i in todo if out[i] is None]
        groups: dict[int, list[int]] = {}
        for i in sorted(todo, key=lambda i: (-lens[i], i)):  # longest first: OOM shows up early
            groups.setdefault(reqs[i].max_new_tokens, []).append(i)
        for _, idx in sorted(groups.items()):
            for s in range(0, len(idx), self.batch_size):
                chunk = idx[s:s + self.batch_size]
                for i, res in zip(chunk, self._run_chunk([prompts[i] for i in chunk], [reqs[i] for i in chunk])):
                    out[i] = res
                    self.n_uncached += 1
                    if self.cache is not None and res.finish_reason not in ("error", "time"):
                        self.cache.set("generation", keys[i], {**res.to_dict(), "cached": False})
        for i, j in dups:  # identical prompt in the same call: served like a sequential cache hit
            self.stats["n_dedup_in_batch"] += 1
            out[i] = GenerationResult(**{**out[j].to_dict(), "cached": out[j].finish_reason not in ("error", "time")})
        return out  # type: ignore[return-value]

    def _run_chunk(self, prompts: list[str], reqs: list[GenerationRequest]) -> list[GenerationResult]:
        """Generate one padded chunk; on out-of-memory split it in half and retry."""
        try:
            return self._generate_padded(prompts, reqs)
        except Exception as e:
            if not is_oom(e):
                raise
            self._free_memory()
            if len(prompts) == 1:
                self.stats["n_oom_failures"] += 1
                n_in = self.count_tokens(prompts[0])
                return [GenerationResult(text="", input_tokens=n_in, output_tokens=0, latency_s=0.0,
                                         finish_reason="error", model_id=self.model_id, revision=self.revision,
                                         decoding=self.decoding, error=f"OutOfMemory at batch size 1: {e}")]
            self.stats["n_oom_splits"] += 1
            h = len(prompts) // 2
            log.warning("OOM at batch size %d; retrying as %d + %d", len(prompts), h, len(prompts) - h)
            return self._run_chunk(prompts[:h], reqs[:h]) + self._run_chunk(prompts[h:], reqs[h:])

    def _free_memory(self) -> None:
        import gc

        import torch

        gc.collect()
        if self.device.startswith("cuda"):
            torch.cuda.empty_cache()
        elif self.device == "mps":
            torch.mps.empty_cache()

    def _generate_padded(self, prompts: list[str], reqs: list[GenerationRequest]) -> list[GenerationResult]:
        import torch

        enc = self.tokenizer(prompts, return_tensors="pt", padding=True, add_special_tokens=False)
        n_in = enc["attention_mask"].sum(dim=1).tolist()
        width = int(enc["input_ids"].shape[1])
        max_new = reqs[0].max_new_tokens
        enc = {k: v.to(self.device) for k, v in enc.items()}
        t0 = time.perf_counter()
        try:
            with torch.inference_mode():
                gen = self.model.generate(
                    **enc, max_new_tokens=max_new, do_sample=False, num_beams=1, max_time=self.cfg.max_time_s,
                    pad_token_id=self.tokenizer.pad_token_id, temperature=None, top_p=None, top_k=None,
                )
        except Exception as e:
            if is_oom(e):
                raise
            dt = time.perf_counter() - t0  # recorded as a generation error, never swallowed silently
            return [GenerationResult(text="", input_tokens=int(n), output_tokens=0, latency_s=dt, finish_reason="error",
                                     model_id=self.model_id, revision=self.revision, decoding=self.decoding,
                                     error=f"{type(e).__name__}: {e}") for n in n_in]
        dt = time.perf_counter() - t0
        self.stats["n_batches"] += 1
        self.stats["n_batched_prompts"] += len(prompts)
        rows = gen[:, width:].tolist()
        out = []
        for req, row, n in zip(reqs, rows, n_in):
            cut = next((j for j, t in enumerate(row) if t in self.eos_ids), None)
            new = row[:cut + 1] if cut is not None else row
            if cut is not None:
                reason = "eos"
            elif len(new) >= max_new:
                reason = "length"
            else:
                reason = "time" if dt >= self.cfg.max_time_s * 0.98 else "eos"
            text = req.prefill + self.tokenizer.decode(new, skip_special_tokens=True)
            out.append(GenerationResult(text=text, input_tokens=int(n), output_tokens=len(new), latency_s=dt,
                                        finish_reason=reason, model_id=self.model_id, revision=self.revision,
                                        decoding=self.decoding, batch_size=len(prompts)))
        return out
