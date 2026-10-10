"""Controlled downloads of datasets and models (pinned revisions, recorded hashes)."""

from __future__ import annotations

import json
import logging
import time
import urllib.request
from pathlib import Path

from .data.loaders import DEFAULT_DATA_ROOT, load_registry
from .hashing import file_sha256
from .models.policy import check_model, load_model_registry, preflight

log = logging.getLogger(__name__)

MODEL_FILE_PATTERNS = ["*.json", "*.safetensors", "*.txt", "*.model", "merges.txt", "vocab.*", "1_Pooling/*"]


def _update_manifest(root: Path, key: str, entry: dict) -> None:
    mpath = root / "MANIFEST.json"
    m = json.loads(mpath.read_text()) if mpath.exists() else {}
    m[key] = entry
    mpath.write_text(json.dumps(m, indent=2, sort_keys=True))


def fetch_dataset(name: str, split: str, data_root: Path = DEFAULT_DATA_ROOT) -> Path:
    if split == "test":
        raise ValueError("test splits are not fetched")
    spec = load_registry()[name]
    src = spec.raw["source"]
    rel = spec.raw["splits"][split]["file"]
    dest_dir = spec.local_dir(data_root)
    dest = dest_dir / rel
    if not dest.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
        if src["kind"] == "hf_dataset":
            from huggingface_hub import hf_hub_download

            hf_hub_download(src["repo"], rel, repo_type="dataset", revision=src["revision"], local_dir=dest_dir)
        elif src["kind"] == "url":
            dest.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(src["url"], dest)
        else:
            raise ValueError(f"unknown source kind {src['kind']}")
    _update_manifest(data_root, f"{name}/{split}", {
        "file": str(dest.relative_to(data_root)), "sha256": file_sha256(str(dest)), "bytes": dest.stat().st_size,
        "source": src, "official_split": spec.raw["splits"][split].get("official_split"),
        "license": spec.raw.get("license"), "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    })
    return dest


def fetch_model(model_id: str, stage: str, authorized_flag: bool = False) -> dict:
    """Policy check -> cache check -> disk/memory preflight -> pinned download."""
    entry = check_model(model_id, None, stage, authorized_flag=authorized_flag)
    policy, _ = load_model_registry()
    report = preflight(entry, policy)
    if not report["cached"]:
        from huggingface_hub import snapshot_download

        snapshot_download(model_id, revision=entry.revision, allow_patterns=MODEL_FILE_PATTERNS)
        report["downloaded"] = True
    return report
