# GPU preflight report (2026-10-12)

Server `interstellar`, bounded GPU preflight authorised by the investigator: the already-cached
Qwen2.5-7B-Instruct, at most two real questions per GPU, at most 128 new tokens, no pilot.
**No pilot question was generated on.** The only real questions used were smoke questions,
which are excluded from the frozen pilot set. **No scientific result is reported here.**

**Verdict: READY_WITH_RESTRICTIONS** (§11).

Raw artefacts:
- Measurements: `docs/gpu_preflight/` (`gpu0_7b.json`, `diag05.json`, `runner_check_gpu0.json`, `util_gpu0.csv`).
- Scripts: `scripts/preflight/` (`bench7b.py`, `diag_batch.py`, `check_runs.py`, `runner_check.yaml`).

---

## 1. Server specifications (measured)

| item | value |
|---|---|
| host / OS | `interstellar`, Ubuntu 24.04.4 LTS, kernel 6.8.0-138 |
| CPU / RAM | AMD Ryzen Threadripper PRO 9975WX (32 cores, 48 logical CPUs); 188 GB RAM |
| GPUs | 2 × NVIDIA RTX 5000 Ada Generation, 32 GB each (compute capability 8.9); driver 610.57.04 |
| GPU 0 | PCI `01:00.0`, compute mode Default. **This is the GPU for experiments.** |
| GPU 1 | PCI `02:00.0`, compute mode Exclusive_Process. It is served by the root `nvidia-mps.service` ("shared inference GPU"), and `ollama.service` is pinned to it. **Not available for experiments.** |
| disks | `/` 48 GB, **98 % full, about 1.4 GB free; never write there**. `/data` 1.6 TB, about 1.5 TB free. |
| scheduler / network | no Slurm; GitHub and Hugging Face reachable |
| software | Python 3.12.3; torch 2.12.1+cu130 (CUDA 13.0, cuDNN 9.20, NCCL 2.29.7); every package in `requirements-pinned.txt` installed at the pinned version |
| locations | repo `/data/roufas/when-structure-hurts`, venv `.venv` inside it, HF cache `/data/roufas/hf_cache` (`~/.cache/huggingface` is a symlink to it), preflight scratch `/data/roufas/wsh_preflight` |

### The MPS routing problem (found during this preflight)

With the root MPS control daemon running, **every CUDA process connects to it by default**. The process then sees only GPU 1, the shared Ollama GPU, whatever `CUDA_VISIBLE_DEVICES` says:
- `CUDA_VISIBLE_DEVICES=0` silently ran on GPU 1;
- `CUDA_VISIBLE_DEVICES=1` failed with "No CUDA GPUs are available".

The first bounded measurements of this preflight therefore ran on GPU 1 through MPS before this was noticed. They were set aside (`/data/roufas/wsh_preflight/mps_gpu1_runs/`), and **every number below was re-measured on GPU 0 directly**.

The repeat runs on GPU 0 matched the GPU 1 runs exactly. That includes the outputs that differed between batched and unbatched generation, and the throughput to within 1 %.

GPU 0 is used directly with:
```bash
export CUDA_MPS_PIPE_DIRECTORY=/data/roufas/wsh_preflight/no_mps   # any unused directory: bypasses the MPS daemon
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0
```

`wsh preflight` now fails its `device` check when CUDA would be routed through an MPS daemon (override: `WSH_ALLOW_MPS=1`). Every manifest records:
- the PCI bus ID of each device;
- `CUDA_DEVICE_ORDER`;
- the MPS pipe in use;
- nvidia-smi index, bus ID and compute mode.

**Open item for the investigator.** An idle MPS server process running as user `roufas` (PID 2179342) was started on GPU 1 by those first runs. It has no clients. I tried to shut it down, but the request was blocked by the permission system, because GPU 1 is a shared workload. MPS normally replaces an idle server when another user's client arrives, but check that Ollama on GPU 1 is unaffected, or ask the administrator to restart `nvidia-mps.service`.

## 2. Deployed revision

| item | value |
|---|---|
| server checkout | `/data/roufas/when-structure-hurts`, branch `main`, clean working tree |
| commit | `011e38d` (fast-forward descendant of `final-server-handoff-v2` = `fe92c44`). The difference is only the two preflight commits in §9, which change 5 files. |
| tags | `final-server-handoff-v2` → `fe92c44` (unchanged). `final-server-handoff` → `30b3c49` is unchanged locally and on GitHub; it was never transferred to the server. Neither tag was moved or deleted. |
| source files | all tracked files present (0 missing, 0 untracked), including the 6 files of `src/wsh/models/` |
| frozen pilot set | `configs/question_sets/pilot_v1.json` sha256 `67e815648caf9bbcacd3928904b84205097f84df0e475d5a4b591ccb4b786f58` (matches PILOT_PROTOCOL §3) |
| datasets | 5/5 files match `data/raw/MANIFEST.json`. Preflight `datasets_match_frozen_set` OK (each file is the one the frozen set was drawn from). |
| model snapshots | Qwen2.5-7B-Instruct `a09a3545…` (pre-existing; not downloaded again), Qwen2.5-0.5B-Instruct `7ae55760…`, bge-small `5c38ec7c…`, ms-marco-MiniLM-L6 `233902d2…`, nli-deberta-v3-xsmall `a1508764…`, nli-deberta-v3-small `fa280487…`. All match `configs/models.yaml`. |
| downloads this session | only the five sub-1B pinned models above (about 2.0 GB, into `/data/roufas/hf_cache`). Root disk unchanged at 1.4 GB free. |
| code transfer | git bundles from the local repository (no credentials on the server). `origin` is set to the GitHub URL, but the server has no GitHub credentials. |

## 3. Test results

| run | result |
|---|---|
| full suite, server, GPUs hidden (before the sub-1B models were cached) | 147 passed, 10 skipped. 8 batching tests had no Qwen tokenizer; 1 preflight test had no models; 1 opt-in. |
| full suite, server, after caching the pinned sub-1B models | **158 passed, 0 failed, 1 skipped**. The skip is the opt-in real-model check (`WSH_RUN_SLOW=1`). |
| full suite, local Mac (same commit) | 158 passed, 1 skipped |
| opt-in real-model check, server CPU fp32 | passed (30/30 batched = unbatched) |
| opt-in real-model check, **server GPU 0 bf16** | **failed: 27/30** batched = unbatched. This is a real finding, not a test defect (§5). The test was not modified. |

## 4. CUDA and model loading (GPU 0, measured)

- **`wsh preflight --tiny-generation`:** every check OK for `configs/pilot.yaml` (0.5B) and for `configs/gpu_pilot.yaml` (7B, authorised).
  - Device: RTX 5000 Ada, bus 1, no MPS.
  - Models cached, generator resources and paths OK. The frozen questions (100/100/50/50/50) load without excluded questions.
  - The 7B model answered "ready".
- **Qwen2.5-7B-Instruct, bf16:**
  - Load time: 2.9 s (weights already in the OS page cache).
  - Parameters: 7,615,616,512, all on `cuda:0`, all `torch.bfloat16`.
  - Memory after load: 15.28 GB allocated, 17.59 GB reserved.
  - Peak during generation: 15.41 GB allocated and 17.64 GB reserved unbatched; 16.04 GB and 17.64 GB with a batch of 8. **About 14 GB of the 32 GB stays free.**
  - nvidia-smi peak: 17.2 GB used, 207 W.
- **Determinism:**
  - Settings: seed 0, cuDNN deterministic, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, deterministic algorithms in warn-only mode.
  - Unbatched bf16 greedy outputs were run-to-run identical (7B 8/8, 0.5B 30/30).

## 5. Sequential vs batched inference (measured)

| check | 0.5B fp32 | 0.5B bf16 | 7B bf16 |
|---|---|---|---|
| unbatched, run-to-run identical | 30/30 | 30/30 | 8/8 |
| batched = unbatched | **30/30** | **27/30** | **5/8** |

**Interpretation.** The padding and attention-mask logic is correct: fp32 batched equals unbatched exactly on CUDA, as it does on CPU and MPS.

In bf16, the GPU kernels round differently depending on batch shape, so greedy decoding can diverge. **The differences change scored answers.** For one MuSiQue question under R1 and R5, unbatched decoding gives "insufficient evidence" but batched decoding gives "Hayneville". Batch composition depends on prompt lengths across conditions, so batching in bf16 would add length-correlated noise to the representation contrasts.

**Decision:** following the fallback pre-specified in PILOT_PROTOCOL §11, `configs/gpu_pilot.yaml` now uses `batch_size: 1`. No other setting changes. The cache key includes the batch size (verified below), so outputs from different batch sizes are never mixed.

**Runner-level checks** (GPU 0, 0.5B bf16, Exp1 smoke config limited to 2 MuSiQue smoke questions; `docs/gpu_preflight/runner_check_gpu0.json`):

| check | result |
|---|---|
| device placement | every generation `device: cuda`. The manifest records GPU bus 1, `CUDA_VISIBLE_DEVICES=0`, `CUDA_DEVICE_ORDER=PCI_BUS_ID`, no MPS pipe. |
| stop at a generation cap, then resume with a raised cap | 24 records at the stop, 4 written on resume, 24 skipped as done. 28 records with 28 unique keys: no duplicates, none lost. Status `completed`, 0 queued records unflushed. |
| question-to-output mapping | every record's prompt contains its own question; prefill token counts equal per-result input tokens (7B benchmark) |
| cache correctness | a fresh run sharing the cache: 28/28 served from cache, texts byte-identical. A run with `batch_size=4` sharing the same cache: **0 cache hits from batch-size-1 entries** (22 generated; the 6 cached are in-run duplicate prompts). |
| batch size 4 vs 1, end to end | 20/28 records identical, consistent with §5 |

## 6. Two-GPU execution

**Not verified, and not available on this server.**
- **Hardware:** GPU 1 is reserved by the administrator for Ollama (Exclusive_Process mode with MPS), so only GPU 0 can run experiments. No two-GPU throughput was measured. No speedup is claimed, nor should any be inferred from the GPU count.
- **Software:** `wsh` has no multi-GPU scheduling or question sharding. A run is one process on one device with one SQLite cache. Running two experiments at once would need separate `WSH_RESULTS_ROOT`/`WSH_CACHE_PATH` values, and no merge tool exists.
- **Not needed:** the estimated runtimes below fit comfortably on one GPU, so I did not implement sharding.

## 7. Performance (GPU 0, Qwen2.5-7B-Instruct bf16, measured)

Workload: 2 MuSiQue smoke questions × R0/R1/R5/R4 = 8 prompts, 3,565 input tokens in total (364–516 per prompt), at most 64 new tokens. Every output ended at EOS, after 10–15 tokens.

| metric | unbatched (batch 1) | batched (batch 8; not used) |
|---|---|---|
| wall time, 8 prompts | 2.64–2.74 s | 0.83 s |
| output tokens | 94 | 93 |
| throughput | **34–36 output tok/s, 2.9–3.0 prompts/s** | 112 tok/s, 9.7 prompts/s |
| peak allocated / reserved VRAM | 15.41 / 17.64 GB | 16.04 / 17.64 GB |

- **Prefill latency** (one forward pass): 0.050–0.063 s for 398–516 input tokens, i.e. about 0.12 ms per token. The first call was 0.19 s (warm-up).
- **Decode:** about 23 ms per generated token, derived as (wall time − prefill) ÷ output tokens.
- **GPU utilisation** (nvidia-smi, sampled every 100 ms): peak 100 %, mean 85.5 % while busy, peak 207 W.
- **CPU and RAM:** 1.3 CPU cores (132 %) and 5.6 GB maximum resident memory for the whole process, including model loading.
- **Runner overhead:** about 0.11 s per record (evaluation, grounding NLI and I/O), measured as a fully cached 28-record run taking 3.2 s including start-up.

## 8. Estimated runtimes (estimates, not measurements)

The estimates are built from the §7 measurements and the record counts in PILOT_PROTOCOL §4, on **one GPU, batch size 1**.

**Assumptions:**
- Per uncached answer generation:
  - central 0.5 s: prefill of about 1,000 tokens, plus about 15 output tokens at 23 ms each;
  - pessimistic 1.7 s: every answer runs the full 64 tokens, with 1,600-token prompts.
- Every record adds 0.11 s of overhead.
- Generation counts are upper bounds: identical prompts are generated once (R5 = R1 for 25–56 % of primary questions), so real counts are lower.
- Exp0 adds LLM claim extraction: about 11.4 calls per question at up to 96 tokens (from the Exp0 smoke run: 245 calls for 15 questions). Each call is estimated at 1.3 s central and 2.4 s pessimistic, plus about 2 s per question for retrieval and reranking.
- The 7B model's answer lengths on pilot questions are unknown. The smoke answers ended after 10–15 tokens, but a model that rambles to the 64-token limit moves the estimate toward the pessimistic column.

| experiment | 200 questions (MuSiQue + 2Wiki, focused): records / generations | time, central – pessimistic | 350 questions (frozen pilot set): records / generations | time, central – pessimistic |
|---|---|---|---|---|
| Exp1 Protocol A (9 variants; 8 for HoVer and FEVER) | 1,800 / ≤1,800 | 0.3 – 0.9 h | 3,050 / ≤3,050 | 0.5 – 1.5 h |
| Exp1 Protocol B (2 budgets × 2 policies) | 7,200 / ≤7,200 | 1.2 – 3.6 h | 12,200 / ≤12,200 | 2.1 – 6.1 h |
| Exp2 (R1, R4 × P1–P6; P7 unavailable) | 7,200 / ≤4,800 | 0.9 – 2.5 h | 12,600 / ≤8,400 | 1.6 – 4.4 h |
| Exp0 (B0–B4) | 1,000 / ≈3,300 | 1.1 – 2.1 h | 1,750 / ≈5,700 | 1.8 – 3.7 h |
| **total, one GPU** | | **≈3.5 – 9 GPU-hours** | | **≈6 – 16 GPU-hours** |

- **Cost:** the GPU belongs to the server. At about 200 W, energy is 1–3 kWh. Exp3 adds nothing until annotations exist (every question unavailable), and Exp4 is disabled.
- **If GPU 1 became available:** each process would need its own results and cache paths, and the experiments would be split across GPUs by experiment, not by question shard. The speedup would have to be measured, not assumed.

## 9. Code changes made during this preflight (tests: 158 passed, 1 skipped)

1. **`7f61ac3`: execution caps are no longer part of the config hash.**
   - Before: resuming a run stopped by `max_generations` with a raised cap (the procedure in SERVER_SETUP §8) was refused with "config hash differs".
   - Now: like the path settings, `max_generations` and `max_wall_clock_s` are excluded from the hash. Anything that affects outputs still blocks resume (tested).
   - Also: `configs/gpu_pilot.yaml` `batch_size` changed from 8 to 1 (§5).
2. **`011e38d`: manifests record the physical GPU, and preflight refuses unintended MPS routing** (§1). Test added.

No change was made to hypotheses, metrics, contrasts, the frozen question set, prompts, conditions or the statistical procedure.

## 10. Research readiness (reviewed against code and configs)

| requirement | status |
|---|---|
| Primary comparisons | Unchanged. `PRESPECIFIED_CONTRASTS["exp1"]` primary contrasts are R0–R1, R1–R5 and R5–R4, on `PRIMARY_DATASETS = (musique, 2wikimultihopqa)`, with question-level EM (PILOT_PROTOCOL §2, §5). |
| Exp1 Protocols A and B separated | `protocol` is part of every condition and stratum. Reports never pool them. Protocol A's information equivalence is checked per question. |
| Exp3 disabled without verified annotations | `exp3.accepted_statuses: [human_verified]` and `verified_annotations: null` in both pilot configs, so every Exp3 question is reported unavailable. |
| Exp4 disabled | `exp4.enabled: false`. The CLI refuses Exp4 unless the config enables it or `--plumbing-check` is passed. |
| Derived edges not called human-verified | Edge strata: A (human-verified) only via the imported overlay; B (exact-anchor derivation) and C (fallback-anchor derivation) are labelled derived; D is model-predicted. The verification package is still blank (50/50 questions outstanding). |
| Smoke questions excluded | The preflight check `frozen_questions_load_without_excluded` is OK on the server. `full` additionally refuses every pilot question. |
| Gold answers not passed to the generator | `assert_prompt_composition` runs for every record: the prompt must equal template + evidence + question. Gold answers can reach the prompt only inside the evidence, by design. |
| Two-GPU metadata | Not applicable (single GPU). Each manifest records the physical GPU (PCI bus ID), the MPS state, the git commit and the generator settings. |
| Cache cannot mix configurations | The key covers model, revision, full prompt, `max_new_tokens` and every decoding setting (device, dtype, batch size, chat-template arguments). Verified on GPU 0: a batch-size-4 run got 0 hits from batch-size-1 entries. |
| Documents | `PRE_GPU_READINESS.md` is marked superseded (by `FINAL_SERVER_HANDOFF.md` and now this report). **`configs/pilot_gpu.template.yaml` no longer exists**: it was replaced by `configs/gpu_pilot.yaml` in the final readiness audit and removed with `git rm`. |

**Remaining methodological limitations (unchanged by this preflight):**
- Graph contrasts measure **automatically derived** structure. 25–33 % of primary questions have fallback-anchor (stratum C) endpoints.
- Many pairs are identical (R5 = R1 for 25/100 MuSiQue and 56/100 2Wiki questions), so each contrast must be read with its identical-pair count, informative-pairs estimate and coverage difference.
- Citation metrics are not interpreted until the generator cites. The 7B model did cite (`Evidence: E5, E7`) in this preflight, but that is not an evaluation.
- The pilot is exploratory with one generator. Nothing from it is confirmatory.
- P7 is unavailable.
- Exp3 waits for the 50-question human verification.

## 11. Verdict and remaining blockers

**READY_WITH_RESTRICTIONS.**

The software, data, model and determinism checks all pass on GPU 0, the runner checks pass, and the measured runtime is small (about 6–16 GPU-hours for everything on the 350-question set).

**Restrictions:**
1. Run **only on GPU 0** with the MPS bypass environment (§1). GPU 1 is not available. Two-GPU execution is unverified and not implemented.
2. **Batch size 1**, as now set in `configs/gpu_pilot.yaml`. Batched bf16 changes answers.
3. **Qwen2.5-7B-Instruct only** for now:
   - the 3B and 9B models are neither cached nor tested;
   - Qwen3.5-9B loading is still unverified;
   - each additional model needs authorisation, a download into `/data/roufas/hf_cache` and its own preflight.
4. **Exp3 stays disabled** until the annotations are imported, Exp4 stays disabled, and P7 stays unavailable.
5. **Before launch:** check that the leftover idle MPS server on GPU 1 (§1) is not affecting Ollama, and get your sign-off on `docs/PILOT_PROTOCOL.md`.
6. **Never use the root filesystem** (1.4 GB free). Every path in the commands below points to `/data`.

### Pilot launch commands (prepared, NOT executed; wait for approval)

```bash
ssh interstellar-remote
cd /data/roufas/when-structure-hurts && source .venv/bin/activate
export HF_HOME=/data/roufas/hf_cache HF_HUB_OFFLINE=1
export CUDA_MPS_PIPE_DIRECTORY=/data/roufas/wsh_preflight/no_mps CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0
export WSH_RESULTS_ROOT=/data/roufas/wsh_results WSH_CACHE_PATH=/data/roufas/wsh_cache/gen.sqlite
export WSH_COMPUTE_AUTHORIZED=1

# 0) preflight (must print ok: true; the device must be bus 1 with no MPS pipe)
wsh preflight --config configs/gpu_pilot.yaml --authorized-compute --tiny-generation

# 1) Exp1 (primary), frozen 350-question pilot set, 7B, batch size 1; use tmux so a dropped SSH session does not kill it
tmux new -s wsh-exp1
wsh run exp1 --config configs/gpu_pilot.yaml --authorized-compute 2>&1 | tee -a /data/roufas/wsh_results/exp1.log

# 2) then Exp2 and Exp0 (secondary), the same way
wsh run exp2 --config configs/gpu_pilot.yaml --authorized-compute
wsh run exp0 --config configs/gpu_pilot.yaml --authorized-compute

# resume after an interruption or a cap stop (a raised cap is allowed)
wsh run exp1 --config configs/gpu_pilot.yaml --authorized-compute --resume <run_dir> [--set max_generations=<n>]

# reports
wsh report <run_dir>
```

The focused 200-question variant restricts `datasets` to MuSiQue and 2Wiki, e.g. with a config copy that keeps the remaining datasets out. It is still drawn from the same frozen file, and per PILOT_PROTOCOL the secondary datasets are then simply not run. Decide which variant to run before launching. Neither has been run.
