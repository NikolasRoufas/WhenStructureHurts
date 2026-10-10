"""SQLite key-value cache for expensive intermediate computations.

Keys are stable hashes of everything that determines the value (model id + revision,
prompt/template version, inputs, parameters). Values are JSON. The cache never
changes results: a hit returns exactly what the original computation produced, and
callers mark cached values as such in their records.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Callable

from .hashing import stable_hash


class KVCache:
    def __init__(self, path: str | Path | None):
        self.path = str(path) if path else ":memory:"
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS kv (ns TEXT, key TEXT, value TEXT, PRIMARY KEY (ns, key))"
        )
        self._conn.commit()
        self.hits = 0
        self.misses = 0

    def get(self, ns: str, key_obj: Any) -> Any | None:
        key = stable_hash(key_obj)
        with self._lock:
            row = self._conn.execute("SELECT value FROM kv WHERE ns=? AND key=?", (ns, key)).fetchone()
        if row is None:
            self.misses += 1
            return None
        self.hits += 1
        return json.loads(row[0])

    def set(self, ns: str, key_obj: Any, value: Any) -> None:
        key = stable_hash(key_obj)
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO kv (ns, key, value) VALUES (?, ?, ?)",
                (ns, key, json.dumps(value, ensure_ascii=False)),
            )
            self._conn.commit()

    def get_or_compute(self, ns: str, key_obj: Any, fn: Callable[[], Any]) -> tuple[Any, bool]:
        """Return (value, was_cached)."""
        v = self.get(ns, key_obj)
        if v is not None:
            return v, True
        v = fn()
        self.set(ns, key_obj, v)
        return v, False

    def close(self) -> None:
        self._conn.close()
