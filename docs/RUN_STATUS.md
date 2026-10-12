# Run status: Qwen2.5-7B GPU campaign (authorised 2026-10-12)

**Authorisation and constraints:**
- Compute ceiling: 24 GPU-hours of new computation on physical GPU 0 of `interstellar`.
- Model: Qwen2.5-7B-Instruct `a09a3545` (cached), bf16, batch size 1.
- Questions: the frozen sets only; smoke and pilot exclusions enforced.

**Where everything lives (server, all under `/data/roufas/`):**
- Campaign root: `wsh_campaign/`.
- Runs: `wsh_campaign/results/gpu_pilot/<exp>/<run_dir>/`, each with `manifest.json`, `config.resolved.yaml` and `predictions.jsonl`.
- Shared generation cache: `wsh_campaign/cache/gen.sqlite`.
- Per-run logs and 30-second GPU traces: `wsh_campaign/logs/`.
- Start/end lines: `wsh_campaign/status.log`.
- The jobs run in tmux session `wsh`, started via `scripts/campaign/run.sh`.
- `run.sh` checks before every run that the device is bus `01:00.0`, reached directly with no MPS routing, and that the GPU is idle.

GPU-hours are counted as the wall-clock time a run holds GPU 0 (one process at a time).

## Stages

| stage | run | config | status | records | errors | wall clock / GPU-h |
|---|---|---|---|---|---|---|
| A | Exp1, focused 200 questions | `configs/gpu_pilot_focused.yaml` | running (started 09:52 UTC) | 5,580 / ≈9,000 at 10:15 UTC | 0 generation errors, 0 pipeline errors (snapshot at 1,440 records) | — |
| A | Exp0, focused 200 questions | `configs/gpu_pilot_focused.yaml` | queued (starts automatically after Exp1) | — | — | — |
| B | decision gate | — | pending Stage A | | | |
| C | Exp1 / Exp2 / Exp0 / Exp3, 350 questions | `configs/gpu_pilot.yaml` | not started | | | |

## GPU-hour ledger

| item | GPU-h |
|---|---|
| preflight (2026-10-12, bounded) | < 0.1 |
| Stage A Exp1 (in progress) | — |
| **total so far** | — |

## Notes

- 2026-10-12: the Mac's disk was full. All analysis and LaTeX compilation therefore run on the server (`/data/roufas/tools/tectonic`, with its cache in `/data/roufas/tools/cache`); only small text files and the final PDF and figures are kept locally.
