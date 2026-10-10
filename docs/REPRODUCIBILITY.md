# Reproducibility

## Environment used for development and smoke tests (2026-10-10)

| Item | Value |
|---|---|
| Hardware | Apple M3, 16 GB RAM, CPU inference (MPS available, not used, for determinism) |
| Python | 3.14.3 (Homebrew), venv `.venv` with `--system-site-packages` |
| torch / transformers / sentence-transformers | 2.12.0 / 5.12.1 / 5.5.1 |
| numpy / pandas / pydantic / rank-bm25 | 2.4.6 / 3.0.3 / 2.13.4 / installed |

Every run manifest records the exact package versions, platform, CPU count, memory, code version (`git_commit`, or `null` if not a git repo, plus `source_tree_sha256` over `src/` and `configs/`), config hash, start/end time, sampled question IDs, and dataset file hashes.

The project is a local git repository (initialised 2026-10-11, not pushed); manifests record the commit and a `-dirty` suffix for uncommitted changes. Server-specific paths come from `WSH_DATA_ROOT`, `WSH_RESULTS_ROOT`, `WSH_CACHE_PATH` and `HF_HOME` and are excluded from the config hash. Exact dev-machine package versions: `requirements-pinned.txt`. Server instructions: SERVER_SETUP.md.

## Pinned artefacts

- Datasets: `configs/datasets.yaml` (repo + revision). File sha256 values are in `data/raw/MANIFEST.json` (written by `wsh data fetch`).
- Models: `configs/models.yaml` (revision + parameter count from the Hub API). Generators and encoders load with `local_files_only=True`; downloads only happen via `wsh models fetch` after policy and resource checks.

## Determinism

- Greedy decoding (`do_sample` cannot be enabled), `torch.manual_seed(0)`, CPU float32 in smoke; on CUDA, deterministic cuDNN, `use_deterministic_algorithms(warn_only)` and `CUBLAS_WORKSPACE_CONFIG=:4096:8` (applied settings recorded in the manifest).
- All randomness (sampling, R2 shuffles, interventions, the Exp4 split) uses `derive_seed(...)`, i.e. SHA-256 of the named parts. It is independent of `PYTHONHASHSEED` and of call order.
- Generation, NLI, reranker and embedding outputs are cached in SQLite (`cache/wsh_cache.sqlite`), keyed by model + revision + full rendered prompt + decoding parameters including device and dtype (CPU outputs are never reused on GPU). Cache hits are flagged in records (`generation.cached`) and keep the original latency.
- GPU (bf16/CUDA) results will not be bit-identical to CPU. Pilot and full runs must report their own hardware.

## Commands

```bash
# setup (uses system torch/transformers; see pyproject for deps)
uv venv --python python3 --system-site-packages .venv
uv pip install --python .venv/bin/python -e .
for d in musique 2wikimultihopqa hotpotqa hover fever; do .venv/bin/wsh data fetch --dataset $d; done
for m in Qwen/Qwen2.5-0.5B-Instruct cross-encoder/ms-marco-MiniLM-L6-v2 \
         cross-encoder/nli-deberta-v3-xsmall cross-encoder/nli-deberta-v3-small BAAI/bge-small-en-v1.5; do
  .venv/bin/wsh models fetch $m --stage smoke; done

# tests
.venv/bin/python -m pytest -q

# smoke test (each command creates a NEW run directory)
scripts/run_smoke.sh                       # exp0..exp3 + exp4 plumbing check
.venv/bin/wsh run exp1 --config configs/smoke.yaml        # a single experiment
.venv/bin/wsh run exp1 --config configs/smoke.yaml --resume results/smoke/exp1/<run_id>   # resume
.venv/bin/wsh report results/smoke/exp1/<run_id>          # recompute aggregates from predictions.jsonl
```

## Artefacts per run

`results/<stage>/<exp>/<timestamp>_<confighash>/`: `config.resolved.yaml`, `manifest.json`, `predictions.jsonl` (one self-contained record per question × condition: evidence text, id map, claims and edges with statuses, intervention records, prompt, raw output, parsed answer, evaluation, failure flags, tokens, latency), `metrics.json`, `summary.csv`, `report.md`.
