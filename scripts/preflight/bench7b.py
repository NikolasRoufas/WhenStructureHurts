"""Bounded GPU preflight benchmark (authorised: Qwen2.5-7B-Instruct, cached; <=2 questions per GPU,
<=128 new tokens). Uses SMOKE questions only (excluded from the frozen pilot set), so no pilot
question is ever generated on. Usage (repo root):
  CUDA_VISIBLE_DEVICES=<g> python bench7b.py <dataset> <out.json> [max_new]"""
import json
import os
import resource
import sys
import time

import torch

from wsh.cache import KVCache
from wsh.config import load_config
from wsh.experiments.common import load_questions, make_layout
from wsh.models.interfaces import GenerationRequest
from wsh.models.local_generator import LocalHFGenerator
from wsh.models.prompts import build_request
from wsh.representations.evidence import gold_bundle
from wsh.representations.serialization import render

dataset, out_path = sys.argv[1], sys.argv[2]
max_new = int(sys.argv[3]) if len(sys.argv) > 3 else 64
assert max_new <= 128
M, REV = "Qwen/Qwen2.5-7B-Instruct", "a09a35458c702b33eeacc393d103063234e8bc28"
REPS = ("R0", "R1", "R5", "R4")

cfg = load_config("configs/smoke.yaml")
qs = load_questions(cfg)[dataset][:2]  # at most two real questions on this GPU
assert len(qs) <= 2
reqs, meta = [], []
for q in qs:
    b = gold_bundle(q)
    for rep in REPS:
        reqs.append(build_request(q, render(make_layout(rep, b, 0)).text, max_new))
        meta.append({"uid": q.uid, "rep": rep})


def cpu_s():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def make(bs):
    m = cfg.model.model_copy(update={"model_id": M, "revision": REV, "device": "cuda", "dtype": "bfloat16",
                                     "batch_size": bs, "max_new_tokens": max_new})
    return LocalHFGenerator(m, "gpu_pilot", KVCache(None), True)


res = {"dataset": dataset, "questions": [q.uid for q in qs], "n_prompts": len(reqs), "max_new_tokens": max_new,
       "gpu": torch.cuda.get_device_name(0), "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")}
t0, c0 = time.perf_counter(), cpu_s()
g = make(1)
res["load_s"] = round(time.perf_counter() - t0, 2)
devs = {str(p.device) for p in g.model.parameters()}
res["param_devices"] = sorted(devs)
res["param_dtypes"] = sorted({str(p.dtype) for p in g.model.parameters()})
res["n_params"] = g.n_params
res["mem_after_load"] = g.memory_stats()

# prefill latency: one forward pass over each prompt, no generation
pre = []
for r in reqs:
    enc = g.tokenizer([g.render(r)], return_tensors="pt", add_special_tokens=False).to(g.device)
    torch.cuda.synchronize()
    t = time.perf_counter()
    with torch.inference_mode():
        g.model(**enc)
    torch.cuda.synchronize()
    pre.append({"input_tokens": int(enc["input_ids"].shape[1]), "prefill_s": round(time.perf_counter() - t, 4)})
res["prefill"] = pre


def timed(gen, rr):
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    t = time.perf_counter()
    out = gen.generate_batch(rr)
    torch.cuda.synchronize()
    wall = time.perf_counter() - t
    ntok = sum(o.output_tokens for o in out)
    return out, {"wall_s": round(wall, 3), "output_tokens": ntok, "input_tokens": sum(o.input_tokens for o in out),
                 "tok_per_s": round(ntok / wall, 2), "prompts_per_s": round(len(rr) / wall, 3),
                 "peak_alloc_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2),
                 "peak_reserved_gb": round(torch.cuda.max_memory_reserved() / 1e9, 2),
                 "errors": sum(o.finish_reason == "error" for o in out),
                 "finish": sorted({o.finish_reason for o in out})}


u1, res["unbatched_run1"] = timed(g, reqs)
g.cache = KVCache(None)
u2, res["unbatched_run2"] = timed(g, reqs)
g.batch_size = len(reqs)
g.cache = KVCache(None)
bt, res["batched"] = timed(g, reqs)
res["batched"]["batch_size"] = len(reqs)
res["unbatched_run_to_run_identical"] = sum(a.text == b.text for a, b in zip(u1, u2))
res["batched_vs_unbatched_identical"] = sum(a.text == b.text for a, b in zip(u1, bt))
# output-to-question mapping: each result must belong to the prompt at the same position
res["mapping_check"] = all(o.input_tokens == p["input_tokens"] for o, p in zip(u1, pre))
res["outputs"] = [{**m, "unbatched": a.text, "batched": b.text, "in": a.input_tokens, "out": a.output_tokens}
                  for m, a, b in zip(meta, u1, bt)]
res["cpu_s"] = round(cpu_s() - c0, 1)
res["max_rss_gb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6, 2)
res["total_s"] = round(time.perf_counter() - t0, 1)
json.dump(res, open(out_path, "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ("outputs", "prefill")}, indent=1))
