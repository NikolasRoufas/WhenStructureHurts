"""Run directories, manifests, append-only per-example records, and safe resumption.

Layout: results/<stage>/<experiment>/<YYYYmmdd-HHMMSS>_<confighash8>/
    config.resolved.yaml   exact configuration
    manifest.json          code version, environment, data/model versions, seeds, timing, status
    predictions.jsonl      one record per (question, condition); append-only, fsync'd
    metrics.json / summary.csv / report.md   aggregates (recomputable from predictions.jsonl)
A new run never writes into an existing directory. ``--resume <dir>`` continues a run only
if its stored config hash matches, skipping records whose keys are already present.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path
from typing import Any

import yaml

from .data.loaders import REPO_ROOT
from .hashing import stable_hash


class RunExistsError(RuntimeError):
    pass


def source_tree_hash() -> str:
    files = sorted(list((REPO_ROOT / "src").rglob("*.py")) + list((REPO_ROOT / "configs").rglob("*.yaml")))
    return stable_hash([(str(f.relative_to(REPO_ROOT)), f.read_text()) for f in files])


def git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
        if out.returncode != 0:
            return None
        dirty = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout
        return out.stdout.strip() + ("-dirty" if dirty.strip() else "")
    except Exception:
        return None


def environment() -> dict[str, Any]:
    pk = {}
    for name in ("torch", "transformers", "sentence-transformers", "numpy", "pydantic", "rank-bm25", "pandas",
                 "huggingface-hub", "tokenizers"):
        try:
            pk[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            pk[name] = None
    env = {"python": sys.version.split()[0], "platform": platform.platform(), "machine": platform.machine(),
           "processor": platform.processor(), "cpu_count": os.cpu_count(), "packages": pk}
    try:
        import torch

        env["torch_devices"] = {"cuda": torch.cuda.is_available(), "mps": torch.backends.mps.is_available()}
        if torch.cuda.is_available():
            env["cuda"] = {"torch_cuda_version": torch.version.cuda, "cudnn": torch.backends.cudnn.version(),
                           "devices": [{"name": torch.cuda.get_device_name(i),
                                        "capability": list(torch.cuda.get_device_capability(i)),
                                        "total_mem_bytes": torch.cuda.get_device_properties(i).total_memory}
                                       for i in range(torch.cuda.device_count())],
                           "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES")}
            try:
                smi = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
                                     capture_output=True, text=True, timeout=10)
                env["cuda"]["nvidia_smi"] = smi.stdout.strip() if smi.returncode == 0 else None
            except Exception:
                env["cuda"]["nvidia_smi"] = None
    except Exception:
        pass
    env["paths"] = {k: os.environ.get(k) for k in ("WSH_DATA_ROOT", "WSH_RESULTS_ROOT", "WSH_CACHE_PATH", "HF_HOME")}
    try:
        env["total_mem_bytes"] = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (ValueError, OSError):
        pass
    return env


UNHASHED_CONFIG_KEYS = ("results_root", "cache_path", "max_generations", "max_wall_clock_s")


class RunContext:
    def __init__(self, cfg, experiment: str, resume_dir: str | None = None, argv: list[str] | None = None):
        self.cfg = cfg
        self.experiment = experiment
        cfg_dict = cfg.model_dump(mode="json")
        # machine-specific paths and execution caps do not change what is computed (records are
        # keyed; a cap only decides how many are written before a clean stop), so they are not
        # hashed: a capped run can be resumed on another mount point or with a raised cap.
        hashed = {k: v for k, v in cfg_dict.items() if k not in UNHASHED_CONFIG_KEYS}
        self.config_hash = stable_hash({"experiment": experiment, "config": hashed})
        if resume_dir:
            self.dir = Path(resume_dir)
            stored = json.loads((self.dir / "manifest.json").read_text())
            if stored["config_hash"] != self.config_hash:
                raise RunExistsError(f"cannot resume {self.dir}: config hash differs ({stored['config_hash'][:8]} vs "
                                     f"{self.config_hash[:8]})")
            self.manifest = stored
            self.manifest.setdefault("resumed_at", []).append(time.strftime("%Y-%m-%dT%H:%M:%S%z"))
        else:
            ts = time.strftime("%Y%m%d-%H%M%S")
            root = Path(cfg.results_root)
            if not root.is_absolute():
                root = REPO_ROOT / root
            base = root / cfg.stage / experiment / f"{ts}_{self.config_hash[:8]}"
            self.dir, n = base, 1
            while True:  # unique: mkdir(exist_ok=False) is atomic, so concurrent launches never share a dir
                try:
                    self.dir.mkdir(parents=True, exist_ok=False)
                    break
                except FileExistsError:
                    n += 1
                    self.dir = base.with_name(f"{base.name}-{n}")
            (self.dir / "config.resolved.yaml").write_text(yaml.safe_dump(cfg_dict, sort_keys=False))
            self.manifest = {
                "experiment": experiment, "run_id": self.dir.name, "stage": cfg.stage, "config_name": cfg.name,
                "config_hash": self.config_hash, "git_commit": git_commit(), "source_tree_sha256": source_tree_hash(),
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "argv": argv or sys.argv,
                "seed": cfg.seed, "environment": environment(), "status": "running",
                "model": {"model_id": cfg.model.model_id, "revision": cfg.model.revision},
            }
            self._write_manifest()
        self.pred_path = self.dir / "predictions.jsonl"
        self._done = self._load_done()

    def _write_manifest(self) -> None:
        tmp = self.dir / "manifest.json.tmp"
        tmp.write_text(json.dumps(self.manifest, indent=2, default=str))
        tmp.replace(self.dir / "manifest.json")

    def update_manifest(self, **kw) -> None:
        self.manifest.update(kw)
        self._write_manifest()

    def _load_done(self) -> set[str]:
        done = set()
        if self.pred_path.exists():
            with open(self.pred_path) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            done.add(json.loads(line)["record_key"])
                        except json.JSONDecodeError:
                            pass  # a torn final line from an interrupted write; the record is redone
        return done

    def is_done(self, key: str) -> bool:
        return key in self._done

    def write(self, record: dict[str, Any]) -> None:
        with open(self.pred_path, "a") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self._done.add(record["record_key"])

    def records(self) -> list[dict[str, Any]]:
        if not self.pred_path.exists():
            return []
        out = []
        with open(self.pred_path) as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        # keep the last record per key (a resumed run may have re-done a torn record)
        return list({r["record_key"]: r for r in out}.values())

    def write_json(self, name: str, obj: Any) -> None:
        (self.dir / name).write_text(json.dumps(obj, indent=2, default=str))
