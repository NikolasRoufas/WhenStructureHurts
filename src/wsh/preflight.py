"""`wsh preflight`: verify a machine before any experiment is launched (no experiment runs).

Checks: config + model-size policy; the device the config resolves to; every model cached at
its pinned revision (nothing is downloaded); generator memory/disk preflight; dataset files
present and identical (sha256) to the ones the frozen question set was drawn from; frozen
question set loads and does not overlap the exclusion list; results/cache directories
writable. ``tiny_generation`` additionally loads the configured generator and generates once;
``batch_check`` compares batched vs unbatched greedy outputs on real pilot prompts and reports
memory and throughput (both are subject to the size policy and its authorisation).
"""

from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path
from typing import Any


def _check(report: dict, name: str, fn) -> Any:
    try:
        val = fn()
        report["checks"][name] = {"ok": True, "detail": val}
        return val
    except Exception as e:  # every failure is reported, none aborts the remaining checks
        report["checks"][name] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        return None


def run_preflight(config_path: str, authorized_flag: bool = False, tiny_generation: bool = False,
                  batch_check: int = 0, overrides: dict | None = None) -> dict[str, Any]:
    from .artifacts import environment
    from .config import load_config, repo_path
    from .data.loaders import DEFAULT_DATA_ROOT, load_registry
    from .hashing import file_sha256
    from .models.policy import check_model, is_cached, load_model_registry, preflight

    report: dict[str, Any] = {"config": config_path, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "checks": {}}
    report["overrides"] = overrides or {}
    cfg = _check(report, "config_valid", lambda: load_config(config_path, overrides).stage)
    if cfg is None:
        report["ok"] = False
        return report
    cfg = load_config(config_path, overrides)
    _check(report, "model_policy", lambda: cfg.enforce_model_policy(authorized_flag) or "all models allowed for stage")
    report["environment"] = environment()

    def device():
        from .models.local_generator import resolve_device

        d = resolve_device(cfg.model.device)
        if cfg.model.device not in ("auto", d):
            raise RuntimeError(f"configured {cfg.model.device} but resolved {d}")
        if d == "cuda":
            import torch

            from .artifacts import mps_control_pipe

            pipe = mps_control_pipe()
            if pipe and not os.environ.get("WSH_ALLOW_MPS"):
                raise RuntimeError(f"CUDA clients would be routed through the MPS daemon at {pipe} (a shared "
                                   "GPU on this machine). Bypass it with CUDA_MPS_PIPE_DIRECTORY=<unused dir>, "
                                   "or set WSH_ALLOW_MPS=1 if that GPU is meant for this run.")
            torch.zeros(1, device="cuda").sum().item()  # actually touch the GPU
            props = torch.cuda.get_device_properties(torch.cuda.current_device())
            return {"device": d, "name": props.name, "pci_bus_id": getattr(props, "pci_bus_id", None),
                    "total_mem_gb": round(props.total_memory / 1e9, 1), "mps_control_pipe": pipe,
                    "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES")}
        return d

    _check(report, "device", device)

    def models_cached():
        refs = [(cfg.model.model_id, cfg.model.revision)] + [(e.model_id, e.revision) for e in (
            cfg.retrieval.dense, cfg.retrieval.reranker, cfg.relations.nli, cfg.grounding.nli)]
        missing = [m for m, r in refs if not is_cached(m, r)]
        if missing:
            raise RuntimeError(f"not in the local HF cache (fetch with `wsh models fetch`): {missing}")
        return [m for m, _ in refs]

    _check(report, "models_cached", models_cached)

    def generator_resources():
        pol, _ = load_model_registry()
        return preflight(check_model(cfg.model.model_id, cfg.model.revision, cfg.stage, authorized_flag=authorized_flag), pol)

    _check(report, "generator_resources", generator_resources)

    def datasets():
        reg, out = load_registry(), {}
        frozen = {}
        for d in cfg.datasets:
            p = reg[d.name].file_for(d.split, DEFAULT_DATA_ROOT)
            if not p.exists():
                raise FileNotFoundError(f"{d.name}/{d.split}: {p} (fetch with `wsh data fetch`)")
            out[d.name] = file_sha256(p)
            if d.qids_file:
                frozen = json.loads(repo_path(d.qids_file).read_text())
                want = frozen["details"][d.name]["dataset_file_sha256"]
                if want != out[d.name]:
                    raise RuntimeError(f"{d.name}: dataset file differs from the one the frozen set was drawn from")
        return out

    _check(report, "datasets_match_frozen_set", datasets)

    def questions():
        from .experiments.common import load_questions, require_frozen_questions

        require_frozen_questions(cfg)
        return {k: len(v) for k, v in load_questions(cfg).items()}

    _check(report, "frozen_questions_load_without_excluded", questions)

    def writable():
        out = {}
        for name, p in (("results_root", repo_path(cfg.results_root)), ("cache_dir", repo_path(cfg.cache_path).parent)):
            p.mkdir(parents=True, exist_ok=True)
            t = p / f".preflight_{os.getpid()}"
            t.write_text("x")
            t.unlink()
            out[name] = {"path": str(p), "free_gb": round(shutil.disk_usage(p).free / 1e9, 1)}
        return out

    _check(report, "paths_writable", writable)

    if tiny_generation:
        def gen():
            from .cache import KVCache
            from .models.interfaces import GenerationRequest
            from .models.local_generator import LocalHFGenerator

            g = LocalHFGenerator(cfg.model, cfg.stage, KVCache(":memory:"), authorized_flag)
            r = g.generate(GenerationRequest(system="You are terse.", user="Reply with the word: ready",
                                              max_new_tokens=4, purpose="preflight", prefill=""))
            return {"device": g.device, "n_params": g.n_params, "text": r.text, "latency_s": r.latency_s,
                    "determinism": g.determinism}

        _check(report, "tiny_generation", gen)
    if batch_check:
        _check(report, "batched_equals_unbatched", lambda: _batch_check(cfg, authorized_flag, batch_check))
    report["ok"] = all(c["ok"] for c in report["checks"].values())
    return report


def _batch_check(cfg, authorized_flag: bool, n_prompts: int) -> dict:
    """Greedy outputs of the configured model/device/dtype with batch_size 1 vs the configured
    batch size, on real Exp1 prompts from the frozen questions (mixed lengths and
    representations). Any disagreement fails the check: run with batch_size 1, or accept and
    document the difference, before the pilot."""
    import time as _t

    from .cache import KVCache
    from .experiments.common import load_questions, make_layout
    from .models.local_generator import LocalHFGenerator
    from .models.prompts import build_request
    from .representations.evidence import EvidenceUnavailable, gold_bundle
    from .representations.serialization import render

    if cfg.model.batch_size < 2:
        return {"skipped": "model.batch_size is 1"}
    reqs = []
    for qs in load_questions(cfg).values():
        for q in qs:
            try:
                b = gold_bundle(q)
            except EvidenceUnavailable:
                continue
            for rep in ("R0", "R4"):
                reqs.append(build_request(q, render(make_layout(rep, b, 0)).text, cfg.model.max_new_tokens))
            if len(reqs) >= n_prompts:
                break
        if len(reqs) >= n_prompts:
            break
    gen = LocalHFGenerator(cfg.model, cfg.stage, KVCache(None), authorized_flag)
    t0 = _t.perf_counter()
    gen.batch_size = 1
    ref = gen.generate_batch(reqs)
    t1 = _t.perf_counter()
    gen.batch_size = cfg.model.batch_size
    gen.cache = KVCache(None)  # fresh: decoding settings are shared, outputs must be regenerated
    got = gen.generate_batch(reqs)
    t2 = _t.perf_counter()
    diff = [i for i, (a, b) in enumerate(zip(ref, got)) if a.text != b.text]
    out = {"n_prompts": len(reqs), "batch_size": cfg.model.batch_size, "n_identical": len(reqs) - len(diff),
           "differing_indices": diff[:20], "seconds_unbatched": round(t1 - t0, 2), "seconds_batched": round(t2 - t1, 2),
           "output_tokens": sum(r.output_tokens for r in got), "memory": gen.memory_stats(),
           "finish_reasons": sorted({r.finish_reason for r in got})}
    if diff or any(r.finish_reason == "error" for r in got):
        raise RuntimeError(f"batched outputs differ from unbatched for {len(diff)}/{len(reqs)} prompts "
                           f"or errored: {out}")
    return out
