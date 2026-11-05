"""Integrity of the original (frozen) research artifacts.

record : hash every original run output (predictions, manifests, metrics) under the campaign directory, the
         revision analysis outputs and the annotation keys on the server -> original_artifact_hashes.json
verify : recompute and compare; exits non-zero on any difference or missing file.

    python experiments/andreas_revision/audits/verify_originals.py record|verify <hashes.json> [--campaign DIR --revision DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def h(p: Path) -> str:
    d = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            d.update(chunk)
    return d.hexdigest()


def collect(campaign: Path, revision: Path) -> dict[str, str]:
    files = sorted(campaign.glob("results/**/*.jsonl")) + sorted(campaign.glob("results/**/manifest.json")) + \
        sorted(campaign.glob("results/**/metrics.json")) + sorted(p for p in revision.rglob("*") if p.is_file())
    return {str(p): h(p) for p in files}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["record", "verify"])
    ap.add_argument("hashes", type=Path)
    ap.add_argument("--campaign", type=Path, default=Path("/data/roufas/wsh_campaign"))
    ap.add_argument("--revision", type=Path, default=Path("/data/roufas/wsh_revision"))
    a = ap.parse_args()
    if a.mode == "record":
        d = collect(a.campaign, a.revision)
        a.hashes.write_text(json.dumps(d, indent=1))
        print(f"recorded {len(d)} files")
        return
    want = json.loads(a.hashes.read_text())
    bad = [p for p, x in want.items() if not Path(p).exists() or h(Path(p)) != x]
    print(json.dumps({"n_checked": len(want), "n_changed_or_missing": len(bad), "changed": bad[:20]}, indent=1))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
