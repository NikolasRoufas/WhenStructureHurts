"""Model allowlist, size policy and pre-download resource checks.

The policy is enforced in code (not just documented): any attempt to configure, fetch or
load a model goes through ``check_model``. Smoke/pilot stages are capped at 1e9 params;
gpu_pilot/full accept larger models only with explicit authorisation (env var AND CLI flag).
"""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ..data.loaders import REPO_ROOT

DEFAULT_MODELS_YAML = REPO_ROOT / "configs" / "models.yaml"
AUTH_ENV = "WSH_COMPUTE_AUTHORIZED"


class PolicyViolation(RuntimeError):
    pass


class ResourceBlocker(RuntimeError):
    pass


@dataclass
class ModelEntry:
    model_id: str
    revision: str
    n_params: int
    kind: str  # generator | encoder
    raw: dict[str, Any]


def load_model_registry(path: str | Path = DEFAULT_MODELS_YAML) -> tuple[dict[str, Any], dict[str, ModelEntry]]:
    with open(path) as f:
        raw = yaml.safe_load(f)
    entries: dict[str, ModelEntry] = {}
    for kind in ("generators", "encoders"):
        for mid, v in (raw.get(kind) or {}).items():
            entries[mid] = ModelEntry(mid, v.get("revision"), int(v["n_params"]), kind[:-1], v)
    return raw["policy"], entries


def check_model(model_id: str, revision: str | None, stage: str, *, authorized_flag: bool = False,
                registry_path: str | Path = DEFAULT_MODELS_YAML) -> ModelEntry:
    policy, entries = load_model_registry(registry_path)
    if stage not in policy["stages"]:
        raise PolicyViolation(f"unknown stage '{stage}'")
    sp = policy["stages"][stage]
    entry = entries.get(model_id)
    if entry is None:
        raise PolicyViolation(f"{model_id} is not in the model allowlist (configs/models.yaml)")
    if not entry.revision:
        raise PolicyViolation(f"{model_id} has no pinned revision")
    if revision is not None and revision != entry.revision:
        raise PolicyViolation(f"{model_id}: revision {revision} != pinned {entry.revision}")
    if entry.n_params > float(sp["max_params"]):
        raise PolicyViolation(f"{model_id}: {entry.n_params:,} params exceeds the {stage} cap of {float(sp['max_params']):,.0f}")
    if entry.kind == "generator" and stage not in entry.raw.get("stages", []):
        raise PolicyViolation(f"{model_id} is not enabled for stage '{stage}'")
    if not sp.get("requires_authorization"):  # local-development stages: also block by name
        for pat in policy.get("forbidden_name_patterns_unauthorized_stages", []):
            if re.search(pat, model_id):
                raise PolicyViolation(f"{model_id} matches forbidden pattern {pat!r} for stage {stage}")
    if sp.get("requires_authorization"):
        if os.environ.get(AUTH_ENV) != "1" or not authorized_flag:
            raise PolicyViolation(
                f"stage '{stage}' requires explicit authorisation: set {AUTH_ENV}=1 and pass --authorized-compute"
            )
    return entry


def verify_loaded_param_count(model: Any, entry: ModelEntry, stage: str,
                              registry_path: str | Path = DEFAULT_MODELS_YAML) -> int:
    """Re-check the parameter count of an instantiated model; abort on mismatch or excess."""
    policy, _ = load_model_registry(registry_path)
    n = sum(p.numel() for p in model.parameters())
    if n > float(policy["stages"][stage]["max_params"]):
        raise PolicyViolation(f"loaded model has {n:,} params, above the {stage} cap")
    # tied embeddings can make numel() differ slightly from safetensors totals
    if abs(n - entry.n_params) / entry.n_params > 0.2:
        raise PolicyViolation(f"loaded param count {n:,} deviates from registry {entry.n_params:,}")
    return n


# ----------------------------------------------------------------------------- resources


def available_memory_bytes() -> tuple[int, int]:
    """(total, available) physical memory. 'available' on macOS = free + inactive + speculative."""
    total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    avail = total
    if shutil.which("vm_stat"):
        import subprocess

        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        page = int(re.search(r"page size of (\d+)", out).group(1))
        pages = {k: int(v) for k, v in re.findall(r"Pages (free|inactive|speculative|purgeable):\s+(\d+)", out)}
        avail = page * sum(pages.values())
    elif Path("/proc/meminfo").exists():
        m = dict(re.findall(r"(\w+):\s+(\d+) kB", Path("/proc/meminfo").read_text()))
        avail = int(m.get("MemAvailable", 0)) * 1024
    return total, avail


def is_cached(model_id: str, revision: str) -> bool:
    from huggingface_hub import try_to_load_from_cache

    p = try_to_load_from_cache(model_id, "config.json", revision=revision)
    return isinstance(p, str)


def preflight(entry: ModelEntry, policy: dict[str, Any], weight_bytes: int | None = None,
              cache_dir: str | None = None) -> dict[str, Any]:
    """Check cache, disk and memory before downloading/loading. Raises ResourceBlocker."""
    wb = weight_bytes or int(entry.raw.get("weight_bytes") or entry.n_params * 4)  # fp32 upper bound
    cached = is_cached(entry.model_id, entry.revision)
    hf_home = Path(cache_dir or os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    hf_home.mkdir(parents=True, exist_ok=True)
    free_disk = shutil.disk_usage(hf_home).free
    total_mem, avail_mem = available_memory_bytes()
    need_disk = 0 if cached else wb + policy.get("safety_margin_disk_gb", 2.0) * 1e9
    need_mem = wb * policy.get("ram_multiplier", 2.5)
    report = {
        "model_id": entry.model_id, "revision": entry.revision, "n_params": entry.n_params, "cached": cached,
        "weight_bytes_est": wb, "free_disk_bytes": free_disk, "need_disk_bytes": need_disk,
        "total_mem_bytes": total_mem, "avail_mem_bytes": avail_mem, "need_mem_bytes": need_mem,
    }
    if free_disk < need_disk:
        raise ResourceBlocker(f"insufficient disk for {entry.model_id}: {report}")
    if avail_mem < need_mem:
        raise ResourceBlocker(f"insufficient memory for {entry.model_id}: {report}")
    report["ok"] = True
    return report
