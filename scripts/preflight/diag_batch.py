"""Diagnose batched != unbatched on CUDA: padding bug or bf16 numerics?
Usage: python diag_batch.py MODEL_ID REVISION MAX_PROMPTS MAX_NEW  (run from the repo root)."""
import json
import sys

from wsh.cache import KVCache
from wsh.config import load_config
from wsh.experiments.common import load_questions, make_layout
from wsh.models.local_generator import LocalHFGenerator
from wsh.models.prompts import build_request
from wsh.representations.evidence import gold_bundle
from wsh.representations.serialization import render

model_id, rev, n_max, max_new = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
stage = "smoke" if "0.5B" in model_id else "gpu_pilot"
cfg = load_config("configs/smoke.yaml")
reqs = []
for qs in load_questions(cfg).values():
    for q in qs[:2]:
        try:
            b = gold_bundle(q)
        except Exception:
            continue
        for rep in ("R0", "R2", "R4"):
            reqs.append(build_request(q, render(make_layout(rep, b, 0)).text, max_new))
reqs = reqs[:n_max]


def gen(dtype, bs, rr, auth=False):
    m = cfg.model.model_copy(update={"model_id": model_id, "revision": rev, "device": "cuda", "dtype": dtype,
                                     "batch_size": bs})
    g = LocalHFGenerator(m, stage, KVCache(None), auth)
    return [r.text for r in g.generate_batch(rr)]


auth = stage != "smoke"
out = {}
for dtype in ("float32", "bfloat16"):
    if dtype == "float32" and stage != "smoke":
        continue
    a = gen(dtype, 1, reqs, auth)
    a2 = gen(dtype, 1, reqs, auth)
    b = gen(dtype, 8, reqs, auth)
    out[dtype] = {
        "n": len(reqs),
        "unbatched_run_to_run_identical": sum(x == y for x, y in zip(a, a2)),
        "batched_vs_unbatched_identical": sum(x == y for x, y in zip(a, b)),
        "differing": [{"i": i, "unbatched": x, "batched": y} for i, (x, y) in enumerate(zip(a, b)) if x != y],
    }
print(json.dumps(out, indent=1))
