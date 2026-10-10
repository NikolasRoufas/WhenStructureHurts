# Server setup (prepared; nothing here has been executed on a GPU)

This guide assumes nothing about the specific GPU. **Large-model commands are templates that need your written authorisation**: the size policy refuses any model above 1B parameters unless `WSH_COMPUTE_AUTHORIZED=1` **and** `--authorized-compute` are both given, and the model is in `configs/models.yaml` with a pinned revision for stage `full`. Nothing selects a larger model automatically.

No runtime or memory figure in this document is a measurement. Measure them with the preflight in §6 on the actual machine.

## 1. Required software

- Linux x86_64 or aarch64; NVIDIA driver plus CUDA runtime compatible with the PyTorch build you install. Apple MPS and CPU are also supported.
- Python 3.11–3.14. The dev machine used 3.14.3; 3.11 or 3.12 is recommended on servers for wheel availability.
- git, and about 2 GB of disk for datasets and the 0.5B/encoder models, plus whatever any authorised larger model needs.
- Optional: `tmux` or `screen`, and a job scheduler (e.g. Slurm). Runs can be resumed, so preemption is safe (§8).

## 2. Python dependencies

```bash
git clone <repo-url> when-structure-hurts && cd when-structure-hurts   # or copy the committed tree
python3.12 -m venv .venv && source .venv/bin/activate
# 1) torch: the build matching the server's CUDA version (see https://pytorch.org/get-started/locally/), e.g.
pip install torch --index-url https://download.pytorch.org/whl/<cuXXX>
# 2) everything else at the dev-machine versions, then the package
pip install -r requirements-pinned.txt && pip install -e .
python -m pytest -q          # must report: 133 passed (see docs/PRE_GPU_READINESS.md)
```

Package versions are recorded in every run manifest (`environment.packages`), so any difference from the dev machine stays visible.

## 3. Dataset locations

The datasets are not in git. Fetch them at the pinned revisions in `configs/datasets.yaml`:

```bash
export WSH_DATA_ROOT=/data/wsh/raw        # optional; default: <repo>/data/raw
for d in musique 2wikimultihopqa hotpotqa hover fever; do wsh data fetch --dataset $d; done
```

`wsh preflight` (§6) checks that every file's sha256 equals the hash recorded in the frozen question set (`configs/question_sets/pilot_v1.json → details.*.dataset_file_sha256`). The dev-machine hashes are listed in EXPERIMENT_LOG §1.

## 4. Model cache configuration

```bash
export HF_HOME=/data/hf          # Hugging Face cache (weights); never inside the repo
export HF_HUB_OFFLINE=1          # optional after fetching: guarantees no download during runs
# fetch only allow-listed models at pinned revisions; disk/RAM preflight runs before any download
for m in Qwen/Qwen2.5-0.5B-Instruct cross-encoder/ms-marco-MiniLM-L6-v2 cross-encoder/nli-deberta-v3-xsmall \
         cross-encoder/nli-deberta-v3-small BAAI/bge-small-en-v1.5; do wsh models fetch $m --stage pilot; done
```

All models load with `local_files_only=True` at the pinned revision; the parameter count is checked again after loading.

**Larger generators (authorisation required, do not run without it):**
1. Add the model to `configs/models.yaml` with `stages: [full]`, the pinned revision and the Hub-verified parameter count.
2. Fetch it with `WSH_COMPUTE_AUTHORIZED=1 wsh models fetch <id> --stage full --authorized-compute`.

## 5. CUDA verification

```bash
nvidia-smi
python - <<'EOF'
import torch
print("torch", torch.__version__, "cuda", torch.version.cuda, "available", torch.cuda.is_available())
for i in range(torch.cuda.device_count()):
    p = torch.cuda.get_device_properties(i); print(i, p.name, round(p.total_memory / 1e9, 1), "GB", "cc", p.major, p.minor)
x = torch.randn(1024, 1024, device="cuda"); print("matmul ok", float((x @ x).sum()) == float((x @ x).sum()))
print("bf16 supported", torch.cuda.is_bf16_supported())
EOF
```

## 6. Small preflight (no experiment is run)

```bash
export WSH_RESULTS_ROOT=/data/wsh/results WSH_CACHE_PATH=/data/wsh/cache/wsh_cache.sqlite   # optional
wsh preflight --config configs/pilot.yaml --tiny-generation
```

It checks:
- the config and model-size policy;
- the device resolution (it actually touches the GPU);
- that every model is cached at its pinned revision;
- generator memory and disk;
- dataset hashes against the frozen question set;
- that the frozen questions load without excluded ones;
- that the results and cache paths are writable;
- one 4-token generation with the 0.5B model.

It exits non-zero if any check fails, and prints a JSON report; keep it with the run.

To verify the whole pipeline on the new hardware (a few minutes, 15 smoke questions, 0.5B):

```bash
wsh run exp1 --config configs/smoke.yaml --set model.device=cuda
```

Smoke outputs are pipeline checks, never results.

## 7. Pilot command templates (prepared, NOT executed)

**0.5B pilot** (no authorisation needed by the size policy, but it **still requires your explicit go-ahead**):

```bash
wsh validate-config configs/pilot.yaml
wsh preflight --config configs/pilot.yaml
wsh run exp1 --config configs/pilot.yaml      # primary
wsh run exp2 --config configs/pilot.yaml      # secondary
wsh run exp0 --config configs/pilot.yaml      # secondary (baselines)
wsh run exp3 --config configs/pilot.yaml      # all questions unavailable until verified annotations are imported
```

**Larger authorised generator** (template; requires your written authorisation naming the model):

```bash
cp configs/pilot_gpu.template.yaml configs/pilot_gpu.yaml   # then fill model_id + revision (must be in models.yaml)
export WSH_COMPUTE_AUTHORIZED=1
wsh validate-config configs/pilot_gpu.yaml --authorized-compute
wsh preflight --config configs/pilot_gpu.yaml --authorized-compute --tiny-generation
for e in exp1 exp2 exp0; do wsh run $e --config configs/pilot_gpu.yaml --authorized-compute; done
```

**After human verification** (enables stratum A and Exp3):

```bash
wsh annotations import --package annotations/verification_v1 --completed <dir> --out annotations/verified/verification_v1.jsonl
wsh run exp3 --config configs/pilot.yaml --set verified_annotations=annotations/verified/verification_v1.jsonl
```

## 8. Checkpointing and resumption

- Every record is appended to `predictions.jsonl` and fsync'd as soon as it is generated. A killed job loses at most the record in flight, and a torn last line is tolerated.
- To resume:

  ```bash
  wsh run exp1 --config configs/pilot.yaml --resume <results_root>/pilot/exp1/<run_id>
  ```

  The run continues only if the config hash matches. Machine paths are excluded from the hash, so a run can move between mounts. Completed records are skipped.
- Generation, NLI, reranker and embedding outputs are cached in SQLite (`WSH_CACHE_PATH`), keyed by model, revision, full prompt, decoding settings, device and dtype. A resumed or repeated run never regenerates an identical prompt, and never reuses CPU outputs on a GPU.
- Hard caps: `max_generations` and `max_wall_clock_s` per run. When a cap is hit the run stops cleanly with status `stopped: …`; resume it with a raised cap only if you authorise that.
- Reports are recomputable at any time: `wsh report <run_dir>`.
- Use one cache file per machine. SQLite on network filesystems with concurrent writers is not supported, so run experiments sequentially or give each concurrent job its own `WSH_CACHE_PATH`.

## 9. Artefact structure

```
<results_root>/<stage>/<experiment>/<YYYYmmdd-HHMMSS>_<confighash8>[-n]/
  config.resolved.yaml   exact configuration
  manifest.json          git commit, source-tree hash, argv, environment (packages, GPU names/memory,
                         CUDA/cuDNN, nvidia-smi, paths), determinism settings, device, dataset hashes,
                         question IDs, model revisions, timings, status, cache hits
  predictions.jsonl      one self-contained record per question x condition (evidence text, fact
                         ids, budget accounting, prompt, raw output, parsing, metrics, failure flags)
  metrics.json, summary.csv, report.md   aggregates (recomputable)
```

`predictions.jsonl` files are not committed to git (size). Archive them with the manifest, for example with `tar czf <run_id>.tgz <run_dir>`, and keep the archives.

## 10. Hardware information to send before launch

1. The `wsh preflight … --tiny-generation` JSON output.
2. The `nvidia-smi` output and the §5 script output: GPU model(s), memory, driver, CUDA, bf16 support.
3. CPU model and core count, RAM, free disk on the results/cache/HF paths, and filesystem type (local vs network).
4. Scheduler constraints: maximum job length, preemption, how many GPUs per job.
5. Whether outbound internet access exists (for dataset and model fetching), or whether files must be staged.
6. The GPU-hour budget and the generator(s) you authorise, in writing.

## 11. Known engineering limits before a large pilot

- Generation is **unbatched**, one prompt at a time, so GPU utilisation will be low. Measure throughput with a short run first. Batching (left-padded) or a vLLM backend behind the `Generator` protocol is the main speed-up; it is not implemented yet.
- Encoders run on the generator's device (`model.device`).
