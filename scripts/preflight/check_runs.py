"""Compare runner-check run directories: A+resume (complete), C (fresh, shared cache, bs1),
D (fresh, shared cache, bs4). Usage: python check_runs.py RUN_A RUN_C RUN_D"""
import json
import sys
from pathlib import Path


def load(d):
    recs = [json.loads(x) for x in (Path(d) / "predictions.jsonl").read_text().splitlines()]
    man = json.loads((Path(d) / "manifest.json").read_text())
    return recs, man


out = {}
runs = dict(zip("ACD", sys.argv[1:4]))
data = {k: load(v) for k, v in runs.items()}
for k, (recs, man) in data.items():
    keys = [r["record_key"] for r in recs]
    gens = [r.get("generation") or {} for r in recs]
    out[k] = {"dir": Path(runs[k]).name, "status": man.get("status"), "n_records": len(recs),
              "n_unique_keys": len(set(keys)),
              "n_generated": sum(1 for g in gens if g and not g.get("cached")),
              "n_cached": sum(1 for g in gens if g.get("cached")),
              "n_errors": sum(1 for g in gens if g.get("finish_reason") == "error"),
              "batch_sizes_used": sorted({g.get("batch_size") for g in gens if g}),
              "decoding_batch_size": sorted({json.dumps((g.get("decoding") or {}).get("batch_size")) for g in gens if g}),
              "device": sorted({str((g.get("decoding") or {}).get("device")) for g in gens if g}),
              "manifest_keys": sorted(k2 for k2 in man if k2 in ("config_hash", "environment", "generator_stats", "generation_batch_size", "device", "determinism", "n_records_unflushed"))}
ta = {r["record_key"]: (r.get("generation") or {}).get("text") for r in data["A"][0]}
tc = {r["record_key"]: (r.get("generation") or {}).get("text") for r in data["C"][0]}
td = {r["record_key"]: (r.get("generation") or {}).get("text") for r in data["D"][0]}
out["A_vs_C_same_keys"] = set(ta) == set(tc)
out["A_vs_C_identical_texts"] = sum(ta[k] == tc.get(k) for k in ta)
out["A_vs_D_identical_texts"] = sum(ta[k] == td.get(k) for k in ta)
# output-to-question mapping: every record's prompt must contain its own question text
out["mapping_ok"] = all(r["question"] in (r.get("prompt") or {}).get("user", "") for r in data["A"][0] if r.get("prompt"))
out["manifest_A"] = {k: data["A"][1].get(k) for k in ("status", "git_commit", "device", "generation_batch_size", "n_records_written", "n_records_skipped_already_done", "n_records_unflushed", "determinism", "generator_stats")}
print(json.dumps(out, indent=1))
