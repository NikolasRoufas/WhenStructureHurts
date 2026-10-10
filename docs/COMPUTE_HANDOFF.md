# Compute handoff — what is needed to run the pilot and full experiments

**Nothing in this document has been executed.** The commands are prepared for when a GPU environment is provided and the full stage is explicitly authorised.

> **Superseded in part (2026-10-11).** Installation, preflight, pilot commands and resumption now live in [SERVER_SETUP.md](SERVER_SETUP.md); the frozen pilot design is in [PILOT_PROTOCOL.md](PILOT_PROTOCOL.md) (50–100 questions per dataset, frozen question file — the 200/100 sample sizes below are obsolete); readiness is in [PRE_GPU_READINESS.md](PRE_GPU_READINESS.md). Section 1 (what is needed from you) remains current.

## 1. What I need from you

1. **A GPU machine:** 1× ≥24 GB GPU is enough for 7B in bf16 (A10G/L4/A100/RTX 4090); 2× or 80 GB for larger or concurrent runs. ≥64 GB RAM, ≥200 GB disk, Linux, CUDA 12.x, Python 3.11–3.12.
2. **Authorisation**, written, naming (a) which generators (proposed: Qwen2.5-7B-Instruct plus one non-Qwen family of similar size, e.g. Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3, both to be added to `configs/models.yaml` with pinned revisions), (b) which stage (pilot vs full), and (c) a GPU-hour budget.
3. **HF access tokens** for any gated models (Llama).
4. **Decision on HoVer:** recovering the remaining 3,092 claims needs the HotpotQA 2017 Wikipedia abstracts dump (`enwiki-20171001-pages-meta-current-withlinks-abstracts`, about 1.6 GB compressed). Do you want it?
5. **Annotation effort**: complete `annotations/verification_v1` (50 questions, 64 edges, 178 claim items; about 3–5 hours, guide included). Without it, graph results exist only for derived strata B/C and Exp3 stays unavailable in the pilot.
6. Optionally, **verified temporal data for P7** (e.g. a curated subset of a temporal QA dataset with dated old/new statements). Otherwise P7 stays unavailable.

## 2. Setup on the server

```bash
git clone <repo> when-structure-hurts && cd when-structure-hurts
python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]'     # installs CUDA torch per platform
for d in musique 2wikimultihopqa hotpotqa hover fever; do .venv/bin/wsh data fetch --dataset $d; done
.venv/bin/python -m pytest -q                                      # must be 133/133 before anything else
scripts/run_smoke.sh                                               # re-run the smoke test on the new hardware
```

Compare `data/raw/MANIFEST.json` sha256 values with the ones from the development machine (listed in docs/EXPERIMENT_LOG.md).

## 3. Pilot (exploratory, policy-compliant 0.5B)

```bash
.venv/bin/wsh validate-config configs/pilot.yaml
for e in exp0 exp1 exp2 exp3; do .venv/bin/wsh run $e --config configs/pilot.yaml --set model.device=cuda; done
```

Expected scale: about 700 questions. Exp1 ≈ 7 reps × 3 R2 seeds × 2 modes ≈ 12k generations. Exp2 ≈ 4 reps × 13 perturbation specs × ~3 rates × 2 seeds ≈ 200k records, most served from cache at rate 0; reduce if needed. Exp0/Exp3 are dominated by LLM claim extraction (~15 calls per question per extractive condition). Rough cost at ~10 gen/s batched-equivalent on one GPU: about 10–20 GPU-hours. The current generator is unbatched, so batching (§6) should be added first.

## 4. Larger-model pilot and full run (requires authorisation)

```bash
# 1. add the authorised models with pinned revisions to configs/models.yaml (stages: [full])
# 2. freeze docs/EXPERIMENT_SPEC.md §9 (preregistration) and commit
export WSH_COMPUTE_AUTHORIZED=1
.venv/bin/wsh validate-config configs/full.yaml --authorized-compute
for e in exp1 exp2 exp3 exp0; do
  .venv/bin/wsh run $e --config configs/full.yaml --authorized-compute
done
# second generator: --set model.model_id=<id> model.revision=<sha>
# interrupted runs: add --resume results/full/<exp>/<run_id>
```

Without both the env var and the flag, the policy refuses every model above 1B parameters (unit-tested).

## 5. Resuming the research

1. Read `docs/EXPERIMENT_LOG.md` (what ran, what failed) and the newest `results/*/*/*/report.md`.
2. Pilot outputs → compute per-contrast SDs from `predictions.jsonl` → set n in `full.yaml` → fill `EXPERIMENT_SPEC.md §9`.
3. Only if Exp1–3 show a reproducible effect: set `exp4.enabled: true` and run `wsh exp4 --config configs/full.yaml --source-run <exp1 run with evidence_source=retrieved>`.

## 6. Items to do before the pilot

Status on 2026-10-11: see PRE_GPU_READINESS.md (133/133 tests; corrected pipeline smoke-tested).

- ~~Decide and implement the token-matched mode fix~~ done: Protocols A/B (METHODOLOGICAL_AUDIT F1).
- **Human audit of derived gold structure** (item 5 above). This is needed to interpret Exp3 C2, since C2 is circular on HotpotQA (audit A3).

- **Batched generation** (left-padded batches) in `LocalHFGenerator`, or a vLLM adapter implementing the same `Generator` protocol. Not implemented yet.
- ~~`git init` and commit~~ done (local repository, not pushed).
- Retrieved-evidence Exp1 run (`--set exp1.evidence_source=retrieved`), which Exp4 needs.
- Add missing baselines (NOVELTY_AND_BASELINES.md §3).
