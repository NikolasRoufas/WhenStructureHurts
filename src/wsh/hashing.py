"""Stable hashing and deterministic seed derivation."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def stable_hash(obj: Any, n: int | None = None) -> str:
    h = hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
    return h[:n] if n else h


def derive_seed(*parts: Any) -> int:
    """Derive a 32-bit seed from arbitrary parts (independent of PYTHONHASHSEED)."""
    return int(stable_hash(list(parts), 8), 16)


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
