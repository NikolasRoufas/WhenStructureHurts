# Run status: Qwen2.5-7B GPU campaign (authorised 2026-10-12)

**Authorisation and constraints:**
- Compute ceiling: 24 GPU-hours of new computation on physical GPU 0 of `interstellar`.
- Model: Qwen2.5-7B-Instruct `a09a3545` (cached), bf16, batch size 1.
- Questions: frozen sets only; smoke and pilot exclusions enforced.

**Where everything lives (server, all under `/data/roufas/`):**
- Campaign root: `wsh_campaign/`.
- Runs: `wsh_campaign/results/<stage>/<exp>/<run_dir>/`, each with `manifest.json`, `config.resolved.yaml` and `predictions.jsonl`.
- Shared generation cache: `wsh_campaign/cache/gen.sqlite`.
- Logs and 30-second GPU traces: `wsh_campaign/logs/`.
- Start/end lines: `wsh_campaign/status.log`.
- Analysis outputs: `wsh_campaign/research_outputs/` (built by `scripts/analysis/build.py` in the separate analysis clone `/data/roufas/wsh_analysis`).
- Jobs run in tmux session `wsh`: window 0 is Stage A, window `stageC` is the queued Stage C and confirmatory runs.
- Every job goes through `scripts/campaign/run.sh`, which checks before each run that the device is bus `01:00.0`, reached directly with no MPS routing, and that the GPU is idle.

GPU-hours are counted as the wall-clock time a run holds GPU 0 (one process at a time).

## Stages

| stage | run | config | status | records | errors | wall clock / GPU-h |
|---|---|---|---|---|---|---|
| A | Exp1, focused 200 questions — `gpu_pilot/exp1/20261012-095222_797a0644` | `configs/gpu_pilot_focused.yaml` @ `dea50b3` | **completed** 10:29 UTC | 9,000 / 9,000 (4,956 generated, the rest identical prompts served from cache) | 0 generation, 0 pipeline, 0 unavailable; 9,000 × EOS | 2,243 s / **0.62** |
| A | Exp0, focused 200 questions — `gpu_pilot/exp0/20261012-102947_8dad35aa` | `configs/gpu_pilot_focused.yaml` @ `dea50b3` | running since 10:29 UTC (about 40 s per question) | 122 / 1,000 at 10:43 UTC | 0 so far | est. 2.2–2.5 |
| B | decision gate | `research_outputs/reports/DECISION_GATE_STAGE_B.md` | **done: proceed** | | | 0 |
| C | Exp1, 350 questions | `configs/gpu_pilot.yaml` | queued (window `stageC`) | | | est. 0.4 |
| C | Exp2, 350 questions | `configs/gpu_pilot.yaml` | queued | | | est. 1.5 |
| confirmatory | Exp1, 1,744 MuSiQue + 3,232 2Wiki, Protocol A | `configs/confirm.yaml` (stage `full`) | queued | | | est. 4–6 |
| C | Exp3, 350 questions | `configs/gpu_pilot.yaml` | queued (expected: every question unavailable, since there are no human-verified annotations) | | | est. < 0.1 |
| C | Exp0, 350 questions (the 200 already done come from cache) | `configs/gpu_pilot.yaml` | queued last (first to cut if the budget tightens) | | | est. 1.8 |

## GPU-hour ledger

| item | GPU-h |
|---|---|
| preflight (2026-10-12, bounded) | < 0.1 |
| Stage A Exp1 | 0.62 |
| Stage A Exp0 | running |
| **total completed** | **≈ 0.7** |
| projected total for every queued item | ≈ 11–13 (ceiling 24) |

## Frozen artefacts used

- Pilot set: `configs/question_sets/pilot_v1.json`, sha256 `67e81564…`.
- Confirmatory set: `configs/question_sets/confirm_v1.json`, sha256 `d7b49cb3…`. Drawn after `docs/CONFIRMATORY_PROTOCOL.md` was committed (`0850982`), and disjoint from the pilot and smoke sets.

## Notes

- 2026-10-12: the Mac's disk is nearly full. All analysis and LaTeX compilation run on the server (`/data/roufas/tools/tectonic`, with its cache in `/data/roufas/tools/cache`); only text files and small outputs are kept locally.
- 10:20 UTC: a local SSH watcher dropped (exit 255). The tmux jobs were unaffected; watchers now reconnect on every poll.
